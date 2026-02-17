from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TTS Service")

class SpeakRequest(BaseModel):
    text: str

AUDIO_DIR = "/app/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

@app.post("/speak")
async def speak(request: SpeakRequest):
    try:
        audio_filename = f"{uuid.uuid4()}.wav"
        audio_path = os.path.join(AUDIO_DIR, audio_filename)
        
        logger.info(f"Generating speech for: {request.text[:50]}...")
        
        # Using pyttsx3 as fallback (simpler, no model download needed)
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.save_to_file(request.text, audio_path)
        engine.runAndWait()
        
        logger.info(f"Audio saved: {audio_filename}")
        
        return {"audio_file": audio_filename}
    
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
