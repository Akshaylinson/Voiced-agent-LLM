from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Service")

class QueryRequest(BaseModel):
    query: str
    context: str

MODEL_NAME = os.getenv("MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
HF_TOKEN = os.getenv("HF_TOKEN")

model = None
tokenizer = None
generator = None

@app.on_event("startup")
async def load_model():
    global model, tokenizer, generator
    
    logger.info(f"Loading model: {MODEL_NAME}")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME,
            token=HF_TOKEN,
            cache_dir="/models"
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            token=HF_TOKEN,
            cache_dir="/models",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=150,
            temperature=0.7,
            do_sample=True
        )
        
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Model loading error: {str(e)}")
        raise

@app.post("/respond")
async def respond(request: QueryRequest):
    if generator is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        prompt = f"""Context: {request.context}

Question: {request.query}

Answer:"""
        
        logger.info(f"Generating response for: {request.query}")
        
        result = generator(prompt, max_new_tokens=150, num_return_sequences=1)
        response = result[0]['generated_text']
        
        # Extract only the answer part
        if "Answer:" in response:
            response = response.split("Answer:")[-1].strip()
        
        logger.info(f"Generated response: {response[:100]}...")
        
        return {"response": response}
    
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "model": MODEL_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
