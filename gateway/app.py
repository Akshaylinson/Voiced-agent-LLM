from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import httpx
import os
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STT_SERVICE_URL = os.getenv("STT_SERVICE_URL", "http://localhost:8001")
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://localhost:8002")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://localhost:8003")
TTS_SERVICE_URL = os.getenv("TTS_SERVICE_URL", "http://localhost:8004")
AUDIO_DIR = "/app/audio"

os.makedirs(AUDIO_DIR, exist_ok=True)

@app.post("/voice/query")
async def voice_query(audio: UploadFile = File(...)):
    try:
        # Step 1: Speech-to-Text
        logger.info("Sending audio to STT service")
        async with httpx.AsyncClient(timeout=60.0) as client:
            files = {"audio": (audio.filename, await audio.read(), audio.content_type)}
            stt_response = await client.post(f"{STT_SERVICE_URL}/transcribe", files=files)
            stt_response.raise_for_status()
            transcript = stt_response.json()["transcript"]
        
        logger.info(f"Transcript: {transcript}")
        
        # Step 2: RAG Retrieval
        logger.info("Retrieving context from RAG service")
        async with httpx.AsyncClient(timeout=30.0) as client:
            rag_response = await client.post(
                f"{RAG_SERVICE_URL}/retrieve",
                json={"query": transcript}
            )
            rag_response.raise_for_status()
            context = rag_response.json()["context"]
        
        # Step 3: LLM Response Generation
        logger.info("Generating response from LLM service")
        async with httpx.AsyncClient(timeout=60.0) as client:
            llm_response = await client.post(
                f"{LLM_SERVICE_URL}/respond",
                json={"query": transcript, "context": context}
            )
            llm_response.raise_for_status()
            response_text = llm_response.json()["response"]
        
        logger.info(f"Response: {response_text}")
        
        # Step 4: Text-to-Speech
        logger.info("Converting response to speech")
        async with httpx.AsyncClient(timeout=60.0) as client:
            tts_response = await client.post(
                f"{TTS_SERVICE_URL}/speak",
                json={"text": response_text}
            )
            tts_response.raise_for_status()
            audio_filename = tts_response.json()["audio_file"]
        
        return {
            "transcript": transcript,
            "response_text": response_text,
            "audio_url": f"/audio/{audio_filename}"
        }
    
    except httpx.HTTPError as e:
        logger.error(f"HTTP error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Service error: {str(e)}")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path, media_type="audio/wav")

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
