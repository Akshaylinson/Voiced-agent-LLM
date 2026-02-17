#!/bin/bash

echo "🎤 Voice Agent System - Setup Script"
echo "===================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your HF_TOKEN if needed"
    echo ""
fi

# Create required directories
echo "📁 Creating required directories..."
mkdir -p data/audio
mkdir -p data/vectordb
mkdir -p models/whisper
mkdir -p models/llm
mkdir -p models/tts
echo "✅ Directories created"
echo ""

# Build and start services
echo "🐳 Building and starting Docker containers..."
echo "⏳ This may take 10-15 minutes on first run (downloading models)..."
echo ""

docker-compose up --build -d

echo ""
echo "✅ Services are starting!"
echo ""
echo "📊 Service URLs:"
echo "   Gateway:     http://localhost:9000"
echo "   STT Service: http://localhost:8001"
echo "   RAG Service: http://localhost:8002"
echo "   LLM Service: http://localhost:8003"
echo "   TTS Service: http://localhost:8004"
echo ""
echo "📝 Check logs with: docker-compose logs -f"
echo "🛑 Stop services with: docker-compose down"
echo ""
echo "🎯 Open mic-component/embed-example.html in your browser to test!"
