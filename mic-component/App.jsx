import React from 'react';
import VoiceMicReact from './VoiceMicReact';

function App() {
    const handleTranscript = (transcript) => {
        console.log('User said:', transcript);
    };

    const handleResponse = (response) => {
        console.log('Assistant replied:', response);
    };

    const handleError = (error) => {
        console.error('Error occurred:', error);
    };

    return (
        <div style={styles.app}>
            <div style={styles.container}>
                <h1 style={styles.title}>🎤 Voice Agent Demo</h1>
                <p style={styles.description}>
                    Click the microphone button to ask a question using your voice.
                </p>
                
                <VoiceMicReact
                    apiUrl="http://localhost:9000"
                    onTranscript={handleTranscript}
                    onResponse={handleResponse}
                    onError={handleError}
                />
                
                <div style={styles.instructions}>
                    <h3>How to Use:</h3>
                    <ol>
                        <li>Click the microphone button to start recording</li>
                        <li>Speak your question clearly</li>
                        <li>Click again to stop recording</li>
                        <li>Wait for the response</li>
                    </ol>
                </div>
            </div>
        </div>
    );
}

const styles = {
    app: {
        fontFamily: 'Arial, sans-serif',
        maxWidth: '800px',
        margin: '50px auto',
        padding: '20px',
        background: '#f5f5f5'
    },
    container: {
        background: 'white',
        padding: '30px',
        borderRadius: '10px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        textAlign: 'center'
    },
    title: {
        color: '#333',
        marginBottom: '10px'
    },
    description: {
        color: '#666',
        marginBottom: '30px'
    },
    instructions: {
        textAlign: 'left',
        background: '#f8f9fa',
        padding: '20px',
        borderRadius: '5px',
        marginTop: '30px'
    }
};

export default App;
