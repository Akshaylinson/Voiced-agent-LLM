from fastapi import FastAPI, File, UploadFile, HTTPException
import whisper
import os
import tempfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="STT Service")

MODEL_SIZE = os.getenv("MODEL_SIZE", "base")
model = None

@app.on_event("startup")
async def load_model():
    global model
    logger.info(f"Loading Whisper model: {MODEL_SIZE}")
    model = whisper.load_model(MODEL_SIZE, download_root="/models")
    logger.info("Model loaded successfully")

@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        logger.info(f"Transcribing audio file: {audio.filename}")
        result = model.transcribe(tmp_path)
        os.unlink(tmp_path)
        
        transcript = result["text"].strip()
        logger.info(f"Transcription: {transcript}")
        
        return {"transcript": transcript}
    
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "model": MODEL_SIZE}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
