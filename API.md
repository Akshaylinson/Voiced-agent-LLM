# API Documentation

## Base URL

```
http://localhost:9000
```

## Authentication

Currently no authentication required. For production, see [DEPLOYMENT.md](DEPLOYMENT.md).

---

## Gateway API

### POST /voice/query

Main endpoint for voice queries. Orchestrates the entire pipeline.

**Request:**

```http
POST /voice/query HTTP/1.1
Content-Type: multipart/form-data

audio: <audio file>
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| audio | File | Yes | Audio file (WAV, WebM, MP3, etc.) |

**Response:**

```json
{
  "transcript": "what is docker",
  "response_text": "Docker is a containerization platform that allows developers to package applications and their dependencies into containers.",
  "audio_url": "/audio/550e8400-e29b-41d4-a716-446655440000.wav"
}
```

**Status Codes:**

- `200 OK` - Success
- `400 Bad Request` - Invalid audio file
- `500 Internal Server Error` - Service error

**Example:**

```bash
curl -X POST http://localhost:9000/voice/query \
  -F "audio=@recording.wav"
```

```javascript
const formData = new FormData();
formData.append('audio', audioBlob, 'recording.webm');

const response = await fetch('http://localhost:9000/voice/query', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(data.transcript);
```

---

### GET /audio/{filename}

Retrieve generated audio response.

**Request:**

```http
GET /audio/550e8400-e29b-41d4-a716-446655440000.wav HTTP/1.1
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| filename | String | Yes | Audio filename from /voice/query response |

**Response:**

Binary audio file (WAV format)

**Status Codes:**

- `200 OK` - Success
- `404 Not Found` - Audio file not found

**Example:**

```bash
curl http://localhost:9000/audio/550e8400-e29b-41d4-a716-446655440000.wav \
  -o response.wav
```

```html
<audio controls>
  <source src="http://localhost:9000/audio/550e8400-e29b-41d4-a716-446655440000.wav" type="audio/wav">
</audio>
```

---

### GET /health

Check gateway service health.

**Request:**

```http
GET /health HTTP/1.1
```

**Response:**

```json
{
  "status": "healthy"
}
```

**Status Codes:**

- `200 OK` - Service is healthy

---

## STT Service API

### POST /transcribe

Convert audio to text using Whisper.

**Request:**

```http
POST /transcribe HTTP/1.1
Content-Type: multipart/form-data

audio: <audio file>
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| audio | File | Yes | Audio file to transcribe |

**Response:**

```json
{
  "transcript": "what is docker"
}
```

**Status Codes:**

- `200 OK` - Success
- `503 Service Unavailable` - Model not loaded
- `500 Internal Server Error` - Transcription error

**Example:**

```bash
curl -X POST http://localhost:8001/transcribe \
  -F "audio=@recording.wav"
```

---

### GET /health

Check STT service health.

**Response:**

```json
{
  "status": "healthy",
  "model": "base"
}
```

---

## RAG Service API

### POST /retrieve

Retrieve relevant context from knowledge base.

**Request:**

```http
POST /retrieve HTTP/1.1
Content-Type: application/json

{
  "query": "what is docker"
}
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| query | String | Yes | Search query |

**Response:**

```json
{
  "context": "Docker is a containerization platform that packages applications and dependencies.\nDocker is a platform for developing, shipping, and running applications in containers."
}
```

**Status Codes:**

- `200 OK` - Success
- `500 Internal Server Error` - Retrieval error

**Example:**

```bash
curl -X POST http://localhost:8002/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "what is docker"}'
```

```javascript
const response = await fetch('http://localhost:8002/retrieve', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'what is docker' })
});

const data = await response.json();
console.log(data.context);
```

---

### GET /health

Check RAG service health.

**Response:**

```json
{
  "status": "healthy",
  "collection_count": 4
}
```

---

## LLM Service API

### POST /respond

Generate response using LLM.

**Request:**

```http
POST /respond HTTP/1.1
Content-Type: application/json

{
  "query": "what is docker",
  "context": "Docker is a containerization platform..."
}
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| query | String | Yes | User query |
| context | String | Yes | Retrieved context |

**Response:**

```json
{
  "response": "Docker is a containerization platform that allows developers to package applications and their dependencies into containers, making it easier to deploy and run applications consistently across different environments."
}
```

**Status Codes:**

- `200 OK` - Success
- `503 Service Unavailable` - Model not loaded
- `500 Internal Server Error` - Generation error

**Example:**

```bash
curl -X POST http://localhost:8003/respond \
  -H "Content-Type: application/json" \
  -d '{
    "query": "what is docker",
    "context": "Docker is a containerization platform..."
  }'
```

---

### GET /health

Check LLM service health.

**Response:**

```json
{
  "status": "healthy",
  "model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
}
```

---

## TTS Service API

### POST /speak

Convert text to speech.

**Request:**

```http
POST /speak HTTP/1.1
Content-Type: application/json

{
  "text": "Hello, this is a test"
}
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| text | String | Yes | Text to convert to speech |

**Response:**

```json
{
  "audio_file": "550e8400-e29b-41d4-a716-446655440000.wav"
}
```

**Status Codes:**

- `200 OK` - Success
- `500 Internal Server Error` - TTS error

**Example:**

```bash
curl -X POST http://localhost:8004/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test"}'
```

---

### GET /health

Check TTS service health.

**Response:**

```json
{
  "status": "healthy"
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Error Codes:**

- `400 Bad Request` - Invalid input parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server-side error
- `503 Service Unavailable` - Service not ready

---

## Rate Limits

No rate limits in development. For production rate limiting, see [DEPLOYMENT.md](DEPLOYMENT.md).

---

## CORS

CORS is enabled for all origins in development. Configure appropriately for production.

---

## WebSocket Support (Future)

WebSocket streaming for real-time transcription and response generation is planned for future releases.

**Planned endpoint:**

```
ws://localhost:9000/voice/stream
```

---

## SDK Examples

### Python

```python
import requests

# Voice query
with open('recording.wav', 'rb') as f:
    response = requests.post(
        'http://localhost:9000/voice/query',
        files={'audio': f}
    )
    data = response.json()
    print(f"Transcript: {data['transcript']}")
    print(f"Response: {data['response_text']}")
    
    # Download audio
    audio_response = requests.get(f"http://localhost:9000{data['audio_url']}")
    with open('response.wav', 'wb') as audio_file:
        audio_file.write(audio_response.content)
```

### JavaScript/Node.js

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function voiceQuery(audioPath) {
  const form = new FormData();
  form.append('audio', fs.createReadStream(audioPath));
  
  const response = await axios.post(
    'http://localhost:9000/voice/query',
    form,
    { headers: form.getHeaders() }
  );
  
  console.log('Transcript:', response.data.transcript);
  console.log('Response:', response.data.response_text);
  
  return response.data;
}

voiceQuery('recording.wav');
```

### cURL

```bash
# Complete pipeline
curl -X POST http://localhost:9000/voice/query \
  -F "audio=@recording.wav" \
  -o response.json

# Extract audio URL and download
AUDIO_URL=$(cat response.json | jq -r '.audio_url')
curl "http://localhost:9000${AUDIO_URL}" -o response.wav
```

---

## Postman Collection

Import this collection to test all endpoints:

```json
{
  "info": {
    "name": "Voice Agent API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Voice Query",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "audio",
              "type": "file",
              "src": "/path/to/audio.wav"
            }
          ]
        },
        "url": {
          "raw": "http://localhost:9000/voice/query",
          "protocol": "http",
          "host": ["localhost"],
          "port": "9000",
          "path": ["voice", "query"]
        }
      }
    }
  ]
}
```

---

## OpenAPI Specification

Access interactive API documentation:

```
http://localhost:9000/docs
http://localhost:8001/docs
http://localhost:8002/docs
http://localhost:8003/docs
http://localhost:8004/docs
```

Each service provides Swagger UI for testing endpoints directly in the browser.
