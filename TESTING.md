# Testing Guide

## Quick Test Commands

### 1. Check All Services Health

```bash
# Gateway
curl http://localhost:9000/health

# STT Service
curl http://localhost:8001/health

# RAG Service
curl http://localhost:8002/health

# LLM Service
curl http://localhost:8003/health

# TTS Service
curl http://localhost:8004/health
```

Expected response: `{"status": "healthy"}`

### 2. Test STT Service

```bash
# Create a test audio file or use existing one
curl -X POST -F "audio=@test.wav" http://localhost:8001/transcribe
```

Expected response:
```json
{
  "transcript": "your spoken text here"
}
```

### 3. Test RAG Service

```bash
curl -X POST http://localhost:8002/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Docker?"}'
```

Expected response:
```json
{
  "context": "Docker is a containerization platform..."
}
```

### 4. Test LLM Service

```bash
curl -X POST http://localhost:8003/respond \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Docker?",
    "context": "Docker is a platform for developing applications in containers."
  }'
```

Expected response:
```json
{
  "response": "Docker is a containerization platform that..."
}
```

### 5. Test TTS Service

```bash
curl -X POST http://localhost:8004/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test"}'
```

Expected response:
```json
{
  "audio_file": "uuid.wav"
}
```

### 6. Test Full Pipeline (Gateway)

```bash
# Using a test audio file
curl -X POST http://localhost:9000/voice/query \
  -F "audio=@test.wav"
```

Expected response:
```json
{
  "transcript": "what is docker",
  "response_text": "Docker is a containerization platform...",
  "audio_url": "/audio/uuid.wav"
}
```

## Browser Testing

### Test Mic Component

1. Start a local web server:
```bash
cd mic-component
python -m http.server 8080
```

2. Open browser: `http://localhost:8080/embed-example.html`

3. Click microphone button and speak

4. Verify:
   - Recording indicator appears
   - Transcript is displayed
   - Response text is shown
   - Audio plays automatically

### Test CORS

Open browser console and run:
```javascript
fetch('http://localhost:9000/health')
  .then(r => r.json())
  .then(console.log)
```

Should return health status without CORS errors.

## Load Testing

### Using Apache Bench

```bash
# Test gateway health endpoint
ab -n 100 -c 10 http://localhost:9000/health
```

### Using Python

```python
import requests
import concurrent.futures

def test_health():
    response = requests.get('http://localhost:9000/health')
    return response.status_code

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(test_health) for _ in range(100)]
    results = [f.result() for f in futures]
    
print(f"Success rate: {results.count(200)/len(results)*100}%")
```

## Debugging

### View Service Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f gateway
docker-compose logs -f stt-service
docker-compose logs -f rag-service
docker-compose logs -f llm-service
docker-compose logs -f tts-service
```

### Check Container Status

```bash
docker-compose ps
```

### Restart Service

```bash
docker-compose restart gateway
```

### Rebuild Service

```bash
docker-compose up -d --build gateway
```

### Access Container Shell

```bash
docker-compose exec gateway /bin/bash
docker-compose exec stt-service /bin/bash
```

## Common Issues

### Issue: Model not loading

**Solution:**
```bash
# Clear model cache
rm -rf models/*
docker-compose down -v
docker-compose up --build
```

### Issue: Out of memory

**Solution:**
```yaml
# In docker-compose.yml, add memory limits
services:
  llm-service:
    deploy:
      resources:
        limits:
          memory: 4G
```

### Issue: Slow response times

**Check:**
1. Model size (use smaller models for faster inference)
2. CPU vs GPU (add GPU support for faster processing)
3. Network latency between services

### Issue: Audio not playing

**Check:**
1. Browser console for errors
2. CORS configuration
3. Audio file generation in TTS service
4. File permissions in shared volume

## Performance Benchmarks

Expected response times (CPU-only):

- STT (Whisper base): 2-5 seconds
- RAG retrieval: 0.1-0.5 seconds
- LLM generation: 5-15 seconds
- TTS: 1-3 seconds
- **Total pipeline**: 8-23 seconds

With GPU:
- STT: 0.5-2 seconds
- LLM: 1-3 seconds
- **Total pipeline**: 2-8 seconds
