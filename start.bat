@echo off
echo 🎤 Voice Agent System - Setup Script
echo ====================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo ✅ Docker is running
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env and add your HF_TOKEN if needed
    echo.
)

REM Create required directories
echo 📁 Creating required directories...
if not exist data\audio mkdir data\audio
if not exist data\vectordb mkdir data\vectordb
if not exist models\whisper mkdir models\whisper
if not exist models\llm mkdir models\llm
if not exist models\tts mkdir models\tts
echo ✅ Directories created
echo.

REM Build and start services
echo 🐳 Building and starting Docker containers...
echo ⏳ This may take 10-15 minutes on first run (downloading models)...
echo.

docker-compose up --build -d

echo.
echo ✅ Services are starting!
echo.
echo 📊 Service URLs:
echo    Gateway:     http://localhost:9000
echo    STT Service: http://localhost:8001
echo    RAG Service: http://localhost:8002
echo    LLM Service: http://localhost:8003
echo    TTS Service: http://localhost:8004
echo.
echo 📝 Check logs with: docker-compose logs -f
echo 🛑 Stop services with: docker-compose down
echo.
echo 🎯 Open mic-component\embed-example.html in your browser to test!
echo.
pause
