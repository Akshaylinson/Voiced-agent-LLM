# Quick Start Guide

Get your voice agent running in 5 minutes!

## Prerequisites

- Docker Desktop installed and running
- 8GB RAM minimum
- 10GB free disk space

## Step 1: Setup (30 seconds)

```bash
# Windows
cd voice-agent-LLM
start.bat

# Linux/Mac
cd voice-agent-LLM
chmod +x start.sh
./start.sh
```

Or manually:

```bash
# Create directories
mkdir -p data/audio data/vectordb models/whisper models/llm models/tts

# Copy environment file
cp .env.example .env

# Start services
docker-compose up --build -d
```

## Step 2: Wait for Services (5-10 minutes)

First run downloads models. Check progress:

```bash
docker-compose logs -f
```

Wait for these messages:
- `stt-service: Model loaded successfully`
- `llm-service: Model loaded successfully`
- `rag-service: Loaded existing collection`

## Step 3: Test (1 minute)

### Option A: Browser Test

1. Open `mic-component/embed-example.html` in browser
2. Click microphone button
3. Say "What is Docker?"
4. Listen to response

### Option B: API Test

```bash
# Test with curl (requires audio file)
curl -X POST http://localhost:9000/voice/query \
  -F "audio=@test.wav"
```

### Option C: Health Check

```bash
curl http://localhost:9000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

All should return: `{"status": "healthy"}`

## Step 4: Embed in Your Website

### HTML

```html
<script src="mic-button.js"></script>
<voice-mic api="http://localhost:9000"></voice-mic>
```

### React

```jsx
import VoiceMicReact from './VoiceMicReact';

<VoiceMicReact apiUrl="http://localhost:9000" />
```

## Common Issues

### Services won't start
```bash
docker-compose down
docker-compose up --build
```

### Out of memory
Edit `docker-compose.yml`, change model:
```yaml
environment:
  - MODEL_SIZE=tiny  # Smaller Whisper model
  - LLM_MODEL_NAME=TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

### Slow responses
Normal on first run. Subsequent requests are faster.

### Microphone not working
- Use Chrome/Firefox
- Allow microphone permission
- Use HTTPS or localhost

## Next Steps

- [Full Documentation](README.md)
- [API Reference](API.md)
- [Component Guide](COMPONENT_GUIDE.md)
- [Deployment Guide](DEPLOYMENT.md)

## Stop Services

```bash
docker-compose down
```

## Update Services

```bash
docker-compose pull
docker-compose up -d
```

## View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f gateway
```

## Customize

### Change Models

Edit `.env`:
```bash
MODEL_SIZE=small
LLM_MODEL_NAME=your-model-name
HF_TOKEN=your-token
```

Restart:
```bash
docker-compose restart
```

### Add Knowledge

Edit `rag-service/app.py`, add to `sample_docs` or `sample_data`.

Rebuild:
```bash
docker-compose up -d --build rag-service
```

## Architecture

```
Browser → Mic Component → Gateway (9000)
                            ↓
                    ┌───────┴───────┐
                    ↓       ↓       ↓
                  STT     RAG     LLM     TTS
                 (8001)  (8002)  (8003)  (8004)
```

## Ports

- 9000: Gateway (main API)
- 8001: Speech-to-Text
- 8002: RAG/Retrieval
- 8003: LLM/Generation
- 8004: Text-to-Speech

## Resources

- Gateway: 512MB RAM
- STT: 2GB RAM
- RAG: 1GB RAM
- LLM: 4GB RAM
- TTS: 512MB RAM

Total: ~8GB RAM

## Production Checklist

- [ ] Change API URL in mic component
- [ ] Enable authentication
- [ ] Configure HTTPS
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Review [DEPLOYMENT.md](DEPLOYMENT.md)

## Support

Issues? Check:
1. Docker is running
2. Ports are available
3. Enough disk space
4. Logs: `docker-compose logs`

Still stuck? Open a GitHub issue.
