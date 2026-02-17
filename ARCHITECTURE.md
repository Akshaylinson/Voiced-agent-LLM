# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         ANY WEBSITE                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         Reusable Mic Component (JS/React)                  │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │ │
│  │  │   Mic    │  │Recording │  │  Audio   │  │ Response │  │ │
│  │  │  Button  │→ │Indicator │→ │  Upload  │→ │  Display │  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTP POST /voice/query
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                    VOICE GATEWAY (Port 9000)                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  • Receives audio file                                     │ │
│  │  • Orchestrates microservices                              │ │
│  │  • Returns unified response                                │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ↓                       ↓                       ↓
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ STT SERVICE  │      │ RAG SERVICE  │      │ LLM SERVICE  │
│  Port 8001   │      │  Port 8002   │      │  Port 8003   │
│              │      │              │      │              │
│  ┌────────┐  │      │  ┌────────┐  │      │  ┌────────┐  │
│  │Whisper │  │      │  │Chroma  │  │      │  │HF Model│  │
│  │  Base  │  │      │  │  DB    │  │      │  │TinyLlama│ │
│  └────────┘  │      │  └────────┘  │      │  └────────┘  │
│              │      │  ┌────────┐  │      │              │
│ Audio → Text │      │  │SQLite  │  │      │ Text → Text  │
│              │      │  │  DB    │  │      │              │
└──────────────┘      └──────────────┘      └──────────────┘
                                                    │
                                                    ↓
                                          ┌──────────────┐
                                          │ TTS SERVICE  │
                                          │  Port 8004   │
                                          │              │
                                          │  ┌────────┐  │
                                          │  │Pyttsx3 │  │
                                          │  └────────┘  │
                                          │              │
                                          │ Text → Audio │
                                          └──────────────┘
```

## Data Flow

```
1. User clicks mic button
   ↓
2. Browser captures audio (WebRTC)
   ↓
3. Audio sent to Gateway
   ↓
4. Gateway → STT Service
   ├─ Whisper transcribes audio
   └─ Returns: "What is Docker?"
   ↓
5. Gateway → RAG Service
   ├─ Embeds query
   ├─ Searches ChromaDB (vector)
   ├─ Searches SQLite (structured)
   └─ Returns: Context documents
   ↓
6. Gateway → LLM Service
   ├─ Combines query + context
   ├─ Generates response
   └─ Returns: "Docker is a containerization platform..."
   ↓
7. Gateway → TTS Service
   ├─ Converts text to speech
   └─ Returns: audio file path
   ↓
8. Gateway returns to browser:
   {
     "transcript": "...",
     "response_text": "...",
     "audio_url": "/audio/uuid.wav"
   }
   ↓
9. Browser displays text + plays audio
```

## Component Architecture

### Gateway Service
```
┌─────────────────────────────┐
│      FastAPI Gateway        │
├─────────────────────────────┤
│ Endpoints:                  │
│  • POST /voice/query        │
│  • GET /audio/{filename}    │
│  • GET /health              │
├─────────────────────────────┤
│ Responsibilities:           │
│  • Request routing          │
│  • Service orchestration    │
│  • Error handling           │
│  • CORS management          │
│  • Response aggregation     │
└─────────────────────────────┘
```

### STT Service
```
┌─────────────────────────────┐
│    Speech-to-Text (STT)     │
├─────────────────────────────┤
│ Model: OpenAI Whisper       │
│ Size: base (configurable)   │
├─────────────────────────────┤
│ Endpoints:                  │
│  • POST /transcribe         │
│  • GET /health              │
├─────────────────────────────┤
│ Input: Audio file           │
│ Output: Text transcript     │
└─────────────────────────────┘
```

### RAG Service
```
┌─────────────────────────────┐
│  Retrieval-Augmented Gen    │
├─────────────────────────────┤
│ Vector DB: ChromaDB         │
│ Embeddings: MiniLM-L6       │
│ Structured: SQLite          │
├─────────────────────────────┤
│ Endpoints:                  │
│  • POST /retrieve           │
│  • GET /health              │
├─────────────────────────────┤
│ Input: Query text           │
│ Output: Context documents   │
└─────────────────────────────┘
```

### LLM Service
```
┌─────────────────────────────┐
│    Language Model (LLM)     │
├─────────────────────────────┤
│ Model: TinyLlama (default)  │
│ Source: Hugging Face        │
│ Framework: Transformers     │
├─────────────────────────────┤
│ Endpoints:                  │
│  • POST /respond            │
│  • GET /health              │
├─────────────────────────────┤
│ Input: Query + Context      │
│ Output: Generated response  │
└─────────────────────────────┘
```

### TTS Service
```
┌─────────────────────────────┐
│    Text-to-Speech (TTS)     │
├─────────────────────────────┤
│ Engine: pyttsx3             │
│ Format: WAV                 │
├─────────────────────────────┤
│ Endpoints:                  │
│  • POST /speak              │
│  • GET /health              │
├─────────────────────────────┤
│ Input: Text                 │
│ Output: Audio file          │
└─────────────────────────────┘
```

## Network Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Docker Network: voice-network          │
│                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐         │
│  │ Gateway  │───→│   STT    │    │   RAG    │         │
│  │  :9000   │    │  :8001   │    │  :8002   │         │
│  └────┬─────┘    └──────────┘    └──────────┘         │
│       │                                                 │
│       │          ┌──────────┐    ┌──────────┐         │
│       └─────────→│   LLM    │───→│   TTS    │         │
│                  │  :8003   │    │  :8004   │         │
│                  └──────────┘    └──────────┘         │
│                                                         │
└─────────────────────────────────────────────────────────┘
         ↑                                    ↓
    Port 9000                          Shared Volume
    (Exposed)                          /app/audio
```

## Storage Architecture

```
Host Machine
├── data/
│   ├── audio/              (Shared: Gateway ↔ TTS)
│   │   └── *.wav          (Generated audio responses)
│   ├── vectordb/          (RAG Service)
│   │   └── chroma.sqlite3 (Vector embeddings)
│   └── knowledge.db       (RAG Service)
│       └── Q&A pairs      (Structured data)
└── models/
    ├── whisper/           (STT Service)
    │   └── base.pt        (Whisper model)
    ├── llm/               (LLM Service)
    │   └── TinyLlama/     (Language model)
    └── tts/               (TTS Service)
        └── voice models   (Speech synthesis)
```

## Microphone Component Architecture

### Web Component (Vanilla JS)
```
┌─────────────────────────────────────┐
│      <voice-mic> Element            │
├─────────────────────────────────────┤
│  Shadow DOM:                        │
│  ┌───────────────────────────────┐  │
│  │ • Mic Button (UI)             │  │
│  │ • Recording Indicator         │  │
│  │ • Status Display              │  │
│  │ • Transcript Display          │  │
│  │ • Response Display            │  │
│  │ • Audio Player (hidden)       │  │
│  └───────────────────────────────┘  │
├─────────────────────────────────────┤
│  JavaScript:                        │
│  • MediaRecorder API              │  │
│  • Fetch API                      │  │
│  • Custom Events                  │  │
│  • State Management               │  │
└─────────────────────────────────────┘
```

### React Component
```
┌─────────────────────────────────────┐
│      <VoiceMicReact />              │
├─────────────────────────────────────┤
│  Props:                             │
│  • apiUrl                           │
│  • onTranscript                     │
│  • onResponse                       │
│  • onError                          │
├─────────────────────────────────────┤
│  State:                             │
│  • isRecording                      │
│  • status                           │
│  • transcript                       │
│  • response                         │
│  • error                            │
├─────────────────────────────────────┤
│  Refs:                              │
│  • mediaRecorderRef                 │
│  • audioChunksRef                   │
│  • audioPlayerRef                   │
└─────────────────────────────────────┘
```

## Deployment Topology

### Development
```
Localhost
├── Docker Compose
│   ├── 5 Services
│   └── Shared Network
└── Browser
    └── Mic Component
```

### Production
```
Cloud Provider (AWS/GCP/Azure)
├── Load Balancer (HTTPS)
│   └── Nginx/Traefik
├── Container Orchestration
│   ├── Kubernetes / Docker Swarm
│   ├── Gateway (3 replicas)
│   ├── STT Service (2 replicas)
│   ├── RAG Service (2 replicas)
│   ├── LLM Service (2 replicas, GPU)
│   └── TTS Service (2 replicas)
├── Persistent Storage
│   ├── S3/Cloud Storage (audio files)
│   ├── Managed Vector DB
│   └── Managed SQL DB
└── Monitoring
    ├── Prometheus
    ├── Grafana
    └── Loki
```

## Security Layers

```
┌─────────────────────────────────────┐
│         Client (Browser)            │
│  • HTTPS Only                       │
│  • CSP Headers                      │
└──────────────┬──────────────────────┘
               │ TLS 1.3
               ↓
┌─────────────────────────────────────┐
│      Reverse Proxy (Nginx)          │
│  • SSL Termination                  │
│  • Rate Limiting                    │
│  • DDoS Protection                  │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│         Gateway Service             │
│  • Authentication (JWT/API Key)     │
│  • Input Validation                 │
│  • Request Sanitization             │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│      Internal Services              │
│  • Network Isolation                │
│  • Service-to-Service Auth          │
│  • Encrypted Storage                │
└─────────────────────────────────────┘
```

## Scalability Pattern

```
Horizontal Scaling:
┌─────────────────────────────────────┐
│         Load Balancer               │
└──────────────┬──────────────────────┘
               │
       ┌───────┼───────┐
       ↓       ↓       ↓
   Gateway Gateway Gateway
       │       │       │
       └───────┼───────┘
               │
       ┌───────┼───────┐
       ↓       ↓       ↓
     STT     STT     STT
       │       │       │
       └───────┼───────┘
               │
       ┌───────┼───────┐
       ↓       ↓       ↓
     LLM     LLM     LLM
```

## Technology Stack

```
Frontend:
├── Vanilla JavaScript (Web Components)
├── React (Optional)
└── HTML5 MediaRecorder API

Backend:
├── Python 3.10
├── FastAPI (Web Framework)
├── Uvicorn (ASGI Server)
└── HTTPx (Async HTTP Client)

AI/ML:
├── OpenAI Whisper (STT)
├── Hugging Face Transformers (LLM)
├── Sentence Transformers (Embeddings)
├── ChromaDB (Vector Database)
└── pyttsx3 (TTS)

Infrastructure:
├── Docker (Containerization)
├── Docker Compose (Orchestration)
└── Nginx (Reverse Proxy)

Storage:
├── SQLite (Structured Data)
├── ChromaDB (Vector Data)
└── File System (Audio Files)
```
