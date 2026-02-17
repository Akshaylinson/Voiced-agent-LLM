# 🎤 Dockerized Web Voice RAG Agent

A production-ready, microservices-based voice agent system that accepts microphone audio from any webpage, converts speech to text, retrieves answers from a knowledge base, generates contextual responses using an LLM, and returns both text and voice replies.

## 🏗️ Architecture

```
Mic Input (Any Website)
    ↓
Reusable Mic Component (JS/React)
    ↓
Voice Gateway API (Port 9000)
    ↓
┌─────────────────────────────────────┐
│  STT Service (Whisper) - Port 8001  │
│  RAG Service (Chroma) - Port 8002   │
│  LLM Service (HF) - Port 8003       │
│  TTS Service (Pyttsx3) - Port 8004  │
└─────────────────────────────────────┘
    ↓
Audio + Text Response
```

## 📦 Components

### Backend Services
- **Gateway Service**: Orchestrates all microservices and exposes unified API
- **STT Service**: Speech-to-text using OpenAI Whisper
- **RAG Service**: Retrieval-Augmented Generation with ChromaDB + SQLite
- **LLM Service**: Response generation using Hugging Face models
- **TTS Service**: Text-to-speech using pyttsx3

### Frontend Components
- **mic-button.js**: Standalone Web Component (vanilla JS)
- **VoiceMicReact.jsx**: React component version

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- (Optional) Hugging Face token for private models

### Installation

1. **Clone and navigate to project**
```bash
cd voice-agent-LLM
```

2. **Create environment file**
```bash
cp .env.example .env
# Edit .env and add your HF_TOKEN if needed
```

3. **Create required directories**
```bash
mkdir -p data/audio data/vectordb models/whisper models/llm models/tts
```

4. **Start all services**
```bash
docker-compose up --build
```

This will start all services:
- Gateway: http://localhost:9000
- STT: http://localhost:8001
- RAG: http://localhost:8002
- LLM: http://localhost:8003
- TTS: http://localhost:8004

### First Run Notes
- First startup will download models (Whisper, embeddings, LLM)
- This may take 5-15 minutes depending on your internet speed
- Subsequent starts will be much faster

## 🎯 Using the Mic Component

### Vanilla JavaScript (Web Component)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Voice Agent</title>
</head>
<body>
    <!-- Embed the component -->
    <voice-mic api="http://localhost:9000"></voice-mic>
    
    <!-- Load the script -->
    <script src="mic-button.js"></script>
    
    <!-- Optional: Listen to events -->
    <script>
        const mic = document.querySelector('voice-mic');
        mic.addEventListener('transcript', (e) => console.log(e.detail));
        mic.addEventListener('response', (e) => console.log(e.detail));
        mic.addEventListener('error', (e) => console.error(e.detail));
    </script>
</body>
</html>
```

### React Component

```jsx
import VoiceMicReact from './VoiceMicReact';

function App() {
    return (
        <VoiceMicReact
            apiUrl="http://localhost:9000"
            onTranscript={(text) => console.log('User:', text)}
            onResponse={(text) => console.log('Bot:', text)}
            onError={(err) => console.error(err)}
        />
    );
}
```

## 📡 API Reference

### POST /voice/query

Main endpoint for voice queries.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `audio` file (WAV, WebM, MP3)

**Response:**
```json
{
    "transcript": "What is Docker?",
    "response_text": "Docker is a containerization platform...",
    "audio_url": "/audio/response-uuid.wav"
}
```

### GET /audio/{filename}

Retrieve generated audio response.

**Response:** Audio file (WAV format)

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HF_TOKEN` | Hugging Face API token | - |
| `LLM_MODEL_NAME` | HF model to use | TinyLlama/TinyLlama-1.1B-Chat-v1.0 |
| `MODEL_SIZE` | Whisper model size | base |
| `VECTOR_DB_PATH` | ChromaDB storage path | /data/vectordb |
| `DB_PATH` | SQLite database path | /data/knowledge.db |

### Customizing Models

**Change Whisper Model:**
```yaml
# In docker-compose.yml
environment:
  - MODEL_SIZE=small  # Options: tiny, base, small, medium, large
```

**Change LLM Model:**
```yaml
environment:
  - LLM_MODEL_NAME=meta-llama/Llama-2-7b-chat-hf
  - HF_TOKEN=your_token_here
```

## 📊 Adding Knowledge to RAG

### Vector Database (ChromaDB)

Edit `rag-service/app.py` and add documents in the startup function:

```python
sample_docs = [
    "Your custom knowledge here",
    "Another piece of information",
]
collection.add(documents=sample_docs, ids=[...])
```

### Structured Database (SQLite)

Add Q&A pairs:

```python
sample_data = [
    ("Question?", "Answer here"),
]
cursor.executemany("INSERT INTO knowledge (question, answer) VALUES (?, ?)", sample_data)
```

## 🧪 Testing

### Test Individual Services

```bash
# Test STT
curl -X POST -F "audio=@test.wav" http://localhost:8001/transcribe

# Test RAG
curl -X POST -H "Content-Type: application/json" \
  -d '{"query":"What is Docker?"}' \
  http://localhost:8002/retrieve

# Test LLM
curl -X POST -H "Content-Type: application/json" \
  -d '{"query":"What is Docker?","context":"Docker is..."}' \
  http://localhost:8003/respond

# Test TTS
curl -X POST -H "Content-Type: application/json" \
  -d '{"text":"Hello world"}' \
  http://localhost:8004/speak
```

### Test Full Pipeline

Open `mic-component/embed-example.html` in a browser and test the complete flow.

## 🐛 Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs gateway
docker-compose logs stt-service

# Restart specific service
docker-compose restart llm-service
```

### Model download issues
```bash
# Clear model cache and restart
rm -rf models/*
docker-compose down -v
docker-compose up --build
```

### Microphone not working
- Ensure HTTPS or localhost (browsers require secure context)
- Check browser permissions for microphone access
- Verify CORS settings in gateway service

## 📈 Scaling

### Horizontal Scaling

```yaml
# In docker-compose.yml
llm-service:
  deploy:
    replicas: 3
```

### Load Balancing

Add nginx as reverse proxy:

```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
```

## 🔒 Production Considerations

1. **Security**
   - Add authentication to gateway
   - Use HTTPS with valid certificates
   - Implement rate limiting
   - Sanitize user inputs

2. **Performance**
   - Use GPU for LLM inference
   - Implement caching layer
   - Use production ASGI server (Gunicorn)
   - Optimize model sizes

3. **Monitoring**
   - Add logging aggregation (ELK stack)
   - Implement health checks
   - Set up metrics (Prometheus)
   - Configure alerts

## 📝 License

MIT License - feel free to use in your projects!

## 🤝 Contributing

Contributions welcome! Please open issues or submit PRs.

## 📧 Support

For issues and questions, please open a GitHub issue.
