import React, { useState, useRef } from 'react';

const VoiceMicReact = ({ 
    apiUrl = 'http://localhost:9000',
    onTranscript = () => {},
    onResponse = () => {},
    onError = () => {}
}) => {
    const [isRecording, setIsRecording] = useState(false);
    const [status, setStatus] = useState('Ready');
    const [transcript, setTranscript] = useState('');
    const [response, setResponse] = useState('');
    const [error, setError] = useState('');
    
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const audioPlayerRef = useRef(null);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorderRef.current = new MediaRecorder(stream);
            audioChunksRef.current = [];

            mediaRecorderRef.current.ondataavailable = (event) => {
                audioChunksRef.current.push(event.data);
            };

            mediaRecorderRef.current.onstop = () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                sendAudio(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorderRef.current.start();
            setIsRecording(true);
            setStatus('Recording...');
            setError('');
        } catch (err) {
            handleError('Microphone access denied');
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            setStatus('Processing...');
        }
    };

    const sendAudio = async (audioBlob) => {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');

        try {
            const res = await fetch(`${apiUrl}/voice/query`, {
                method: 'POST',
                body: formData
            });

            if (!res.ok) throw new Error('API request failed');

            const data = await res.json();
            handleResponse(data);
        } catch (err) {
            handleError(err.message);
        }
    };

    const handleResponse = (data) => {
        setStatus('Ready');
        setTranscript(data.transcript);
        setResponse(data.response_text);
        
        // Play audio
        if (audioPlayerRef.current) {
            audioPlayerRef.current.src = `${apiUrl}${data.audio_url}`;
            audioPlayerRef.current.play();
        }

        onTranscript(data.transcript);
        onResponse(data.response_text);
    };

    const handleError = (message) => {
        setStatus('Ready');
        setError(message);
        onError(message);
    };

    return (
        <div style={styles.container}>
            <button
                onClick={isRecording ? stopRecording : startRecording}
                style={{
                    ...styles.button,
                    ...(isRecording ? styles.buttonRecording : {})
                }}
            >
                🎤
            </button>
            <div style={styles.status}>{status}</div>
            {error && <div style={styles.error}>Error: {error}</div>}
            {transcript && (
                <div style={styles.transcript}>You: {transcript}</div>
            )}
            {response && (
                <div style={styles.response}>Assistant: {response}</div>
            )}
            <audio ref={audioPlayerRef} style={{ display: 'none' }} />
        </div>
    );
};

const styles = {
    container: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '10px',
        fontFamily: 'Arial, sans-serif'
    },
    button: {
        width: '60px',
        height: '60px',
        borderRadius: '50%',
        border: 'none',
        background: '#007bff',
        color: 'white',
        cursor: 'pointer',
        fontSize: '24px',
        transition: 'all 0.3s',
        boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
    },
    buttonRecording: {
        background: '#dc3545',
        animation: 'pulse 1.5s infinite'
    },
    status: {
        fontSize: '12px',
        color: '#666',
        minHeight: '16px'
    },
    transcript: {
        marginTop: '10px',
        padding: '10px',
        background: '#f8f9fa',
        borderRadius: '5px',
        maxWidth: '400px',
        fontSize: '14px'
    },
    response: {
        marginTop: '10px',
        padding: '10px',
        background: '#e7f3ff',
        borderRadius: '5px',
        maxWidth: '400px',
        fontSize: '14px'
    },
    error: {
        color: '#dc3545',
        fontSize: '12px'
    }
};

export default VoiceMicReact;
