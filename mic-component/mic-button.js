class VoiceMic extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.apiUrl = this.getAttribute('api') || 'http://localhost:9000';
        
        this.render();
        this.setupEventListeners();
    }

    render() {
        this.shadowRoot.innerHTML = `
            <style>
                .voice-mic-container {
                    display: inline-flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 10px;
                    font-family: Arial, sans-serif;
                }
                .mic-button {
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    border: none;
                    background: #007bff;
                    color: white;
                    cursor: pointer;
                    font-size: 24px;
                    transition: all 0.3s;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                }
                .mic-button:hover {
                    background: #0056b3;
                    transform: scale(1.05);
                }
                .mic-button.recording {
                    background: #dc3545;
                    animation: pulse 1.5s infinite;
                }
                @keyframes pulse {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.1); }
                }
                .status {
                    font-size: 12px;
                    color: #666;
                    min-height: 16px;
                }
                .transcript, .response {
                    margin-top: 10px;
                    padding: 10px;
                    background: #f8f9fa;
                    border-radius: 5px;
                    max-width: 400px;
                    font-size: 14px;
                }
                .error {
                    color: #dc3545;
                }
            </style>
            <div class="voice-mic-container">
                <button class="mic-button" id="micBtn">🎤</button>
                <div class="status" id="status"></div>
                <div id="transcript" style="display:none;"></div>
                <div id="response" style="display:none;"></div>
                <audio id="audioPlayer" style="display:none;"></audio>
            </div>
        `;
    }

    setupEventListeners() {
        const btn = this.shadowRoot.getElementById('micBtn');
        btn.addEventListener('click', () => this.toggleRecording());
    }

    async toggleRecording() {
        if (this.isRecording) {
            this.stopRecording();
        } else {
            await this.startRecording();
        }
    }

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                this.sendAudio(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            this.updateUI('recording', 'Recording...');
        } catch (error) {
            this.handleError('Microphone access denied');
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.updateUI('processing', 'Processing...');
        }
    }

    async sendAudio(audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');

        try {
            const response = await fetch(`${this.apiUrl}/voice/query`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('API request failed');

            const data = await response.json();
            this.handleResponse(data);
        } catch (error) {
            this.handleError(error.message);
        }
    }

    handleResponse(data) {
        this.updateUI('idle', 'Ready');
        
        // Display transcript
        const transcriptEl = this.shadowRoot.getElementById('transcript');
        transcriptEl.className = 'transcript';
        transcriptEl.textContent = `You: ${data.transcript}`;
        transcriptEl.style.display = 'block';

        // Display response
        const responseEl = this.shadowRoot.getElementById('response');
        responseEl.className = 'response';
        responseEl.textContent = `Assistant: ${data.response_text}`;
        responseEl.style.display = 'block';

        // Play audio
        const audioPlayer = this.shadowRoot.getElementById('audioPlayer');
        audioPlayer.src = `${this.apiUrl}${data.audio_url}`;
        audioPlayer.play();

        // Trigger custom events
        this.dispatchEvent(new CustomEvent('transcript', { detail: data.transcript }));
        this.dispatchEvent(new CustomEvent('response', { detail: data.response_text }));
    }

    handleError(message) {
        this.updateUI('idle', '');
        const status = this.shadowRoot.getElementById('status');
        status.className = 'status error';
        status.textContent = `Error: ${message}`;
        this.dispatchEvent(new CustomEvent('error', { detail: message }));
    }

    updateUI(state, statusText) {
        const btn = this.shadowRoot.getElementById('micBtn');
        const status = this.shadowRoot.getElementById('status');
        
        btn.className = `mic-button ${state === 'recording' ? 'recording' : ''}`;
        status.className = 'status';
        status.textContent = statusText;
    }
}

customElements.define('voice-mic', VoiceMic);
