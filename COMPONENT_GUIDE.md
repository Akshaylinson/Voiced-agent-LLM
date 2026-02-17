# Microphone Component Usage Guide

## Overview

The Voice Mic component is a reusable, plug-and-play microphone widget that can be embedded into any webpage. It handles audio recording, API communication, and response playback automatically.

Available in two versions:
- **Web Component** (vanilla JavaScript) - Works anywhere
- **React Component** - For React applications

---

## Web Component (Vanilla JS)

### Installation

#### Option 1: Direct Include

```html
<script src="mic-button.js"></script>
```

#### Option 2: CDN (if published)

```html
<script src="https://cdn.example.com/voice-mic/1.0.0/mic-button.js"></script>
```

#### Option 3: NPM (if published)

```bash
npm install voice-mic-component
```

```javascript
import 'voice-mic-component';
```

### Basic Usage

```html
<!DOCTYPE html>
<html>
<head>
    <title>My Website</title>
</head>
<body>
    <h1>Ask a Question</h1>
    
    <!-- Add the component -->
    <voice-mic api="http://localhost:9000"></voice-mic>
    
    <!-- Load the script -->
    <script src="mic-button.js"></script>
</body>
</html>
```

### Configuration

#### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `api` | String | `http://localhost:9000` | Backend API URL |

**Example:**

```html
<voice-mic api="https://api.myapp.com"></voice-mic>
```

### Events

The component emits custom events you can listen to:

#### transcript

Fired when transcription is received.

```javascript
const voiceMic = document.querySelector('voice-mic');

voiceMic.addEventListener('transcript', (event) => {
    console.log('User said:', event.detail);
    // event.detail contains the transcript text
});
```

#### response

Fired when LLM response is received.

```javascript
voiceMic.addEventListener('response', (event) => {
    console.log('Assistant replied:', event.detail);
    // event.detail contains the response text
});
```

#### error

Fired when an error occurs.

```javascript
voiceMic.addEventListener('error', (event) => {
    console.error('Error:', event.detail);
    // event.detail contains the error message
});
```

### Complete Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>Voice Assistant</title>
    <style>
        .container {
            max-width: 600px;
            margin: 50px auto;
            text-align: center;
        }
        .log {
            margin-top: 20px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 5px;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Voice Assistant</h1>
        <voice-mic api="http://localhost:9000"></voice-mic>
        <div class="log" id="log"></div>
    </div>

    <script src="mic-button.js"></script>
    <script>
        const voiceMic = document.querySelector('voice-mic');
        const log = document.getElementById('log');

        voiceMic.addEventListener('transcript', (e) => {
            log.innerHTML += `<p><strong>You:</strong> ${e.detail}</p>`;
        });

        voiceMic.addEventListener('response', (e) => {
            log.innerHTML += `<p><strong>Assistant:</strong> ${e.detail}</p>`;
        });

        voiceMic.addEventListener('error', (e) => {
            log.innerHTML += `<p style="color: red;"><strong>Error:</strong> ${e.detail}</p>`;
        });
    </script>
</body>
</html>
```

---

## React Component

### Installation

Copy `VoiceMicReact.jsx` to your project:

```bash
cp mic-component/VoiceMicReact.jsx src/components/
```

### Basic Usage

```jsx
import React from 'react';
import VoiceMicReact from './components/VoiceMicReact';

function App() {
    return (
        <div>
            <h1>Voice Assistant</h1>
            <VoiceMicReact api="http://localhost:9000" />
        </div>
    );
}

export default App;
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `apiUrl` | String | `http://localhost:9000` | Backend API URL |
| `onTranscript` | Function | `() => {}` | Callback when transcript received |
| `onResponse` | Function | `() => {}` | Callback when response received |
| `onError` | Function | `() => {}` | Callback when error occurs |

### Event Handlers

```jsx
import React, { useState } from 'react';
import VoiceMicReact from './components/VoiceMicReact';

function App() {
    const [transcript, setTranscript] = useState('');
    const [response, setResponse] = useState('');

    const handleTranscript = (text) => {
        console.log('Transcript:', text);
        setTranscript(text);
    };

    const handleResponse = (text) => {
        console.log('Response:', text);
        setResponse(text);
    };

    const handleError = (error) => {
        console.error('Error:', error);
        alert(`Error: ${error}`);
    };

    return (
        <div>
            <h1>Voice Assistant</h1>
            
            <VoiceMicReact
                apiUrl="http://localhost:9000"
                onTranscript={handleTranscript}
                onResponse={handleResponse}
                onError={handleError}
            />
            
            {transcript && (
                <div>
                    <h3>You said:</h3>
                    <p>{transcript}</p>
                </div>
            )}
            
            {response && (
                <div>
                    <h3>Assistant replied:</h3>
                    <p>{response}</p>
                </div>
            )}
        </div>
    );
}

export default App;
```

### Styling

The component uses inline styles by default. To customize:

```jsx
import VoiceMicReact from './components/VoiceMicReact';
import './VoiceMic.css';

// Modify the component to accept className prop
<VoiceMicReact 
    apiUrl="http://localhost:9000"
    className="custom-voice-mic"
/>
```

---

## Advanced Usage

### Custom Styling (Web Component)

The Web Component uses Shadow DOM. To style it, modify `mic-button.js`:

```javascript
// In mic-button.js, update the <style> section
this.shadowRoot.innerHTML = `
    <style>
        .mic-button {
            background: #your-color;
            /* your custom styles */
        }
    </style>
    ...
`;
```

### Multiple Instances

You can have multiple mic components on the same page:

```html
<div class="section-1">
    <h2>General Questions</h2>
    <voice-mic api="http://localhost:9000" id="mic1"></voice-mic>
</div>

<div class="section-2">
    <h2>Technical Support</h2>
    <voice-mic api="http://localhost:9000" id="mic2"></voice-mic>
</div>

<script>
    document.getElementById('mic1').addEventListener('response', (e) => {
        console.log('General:', e.detail);
    });
    
    document.getElementById('mic2').addEventListener('response', (e) => {
        console.log('Support:', e.detail);
    });
</script>
```

### Integration with Forms

```html
<form id="queryForm">
    <voice-mic api="http://localhost:9000"></voice-mic>
    
    <input type="text" id="transcriptInput" name="transcript" readonly>
    <input type="text" id="responseInput" name="response" readonly>
    
    <button type="submit">Submit</button>
</form>

<script src="mic-button.js"></script>
<script>
    const voiceMic = document.querySelector('voice-mic');
    
    voiceMic.addEventListener('transcript', (e) => {
        document.getElementById('transcriptInput').value = e.detail;
    });
    
    voiceMic.addEventListener('response', (e) => {
        document.getElementById('responseInput').value = e.detail;
    });
    
    document.getElementById('queryForm').addEventListener('submit', (e) => {
        e.preventDefault();
        // Handle form submission
    });
</script>
```

### WordPress Integration

```php
<!-- In your WordPress theme -->
<div class="voice-assistant">
    <voice-mic api="<?php echo get_site_url(); ?>/voice-api"></voice-mic>
</div>

<script src="<?php echo get_template_directory_uri(); ?>/js/mic-button.js"></script>
```

### Vue.js Integration

```vue
<template>
    <div>
        <h1>Voice Assistant</h1>
        <voice-mic 
            ref="voiceMic"
            api="http://localhost:9000"
        ></voice-mic>
    </div>
</template>

<script>
import 'voice-mic-component';

export default {
    name: 'VoiceAssistant',
    mounted() {
        this.$refs.voiceMic.addEventListener('transcript', this.handleTranscript);
        this.$refs.voiceMic.addEventListener('response', this.handleResponse);
    },
    methods: {
        handleTranscript(event) {
            console.log('Transcript:', event.detail);
        },
        handleResponse(event) {
            console.log('Response:', event.detail);
        }
    }
}
</script>
```

### Angular Integration

```typescript
// app.component.ts
import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';

@Component({
    selector: 'app-root',
    template: `
        <h1>Voice Assistant</h1>
        <voice-mic #voiceMic api="http://localhost:9000"></voice-mic>
    `
})
export class AppComponent implements OnInit {
    @ViewChild('voiceMic') voiceMic!: ElementRef;

    ngOnInit() {
        // Load the web component
        import('voice-mic-component');
    }

    ngAfterViewInit() {
        this.voiceMic.nativeElement.addEventListener('transcript', (e: any) => {
            console.log('Transcript:', e.detail);
        });

        this.voiceMic.nativeElement.addEventListener('response', (e: any) => {
            console.log('Response:', e.detail);
        });
    }
}
```

---

## Browser Compatibility

### Supported Browsers

- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

### Required Features

- MediaRecorder API
- Web Components (Custom Elements)
- Fetch API
- Promises

### Polyfills

For older browsers, include:

```html
<script src="https://unpkg.com/@webcomponents/webcomponentsjs@2.6.0/webcomponents-loader.js"></script>
<script src="https://unpkg.com/whatwg-fetch@3.6.2/dist/fetch.umd.js"></script>
```

---

## Troubleshooting

### Microphone Permission Denied

```javascript
voiceMic.addEventListener('error', (e) => {
    if (e.detail.includes('denied')) {
        alert('Please allow microphone access in your browser settings');
    }
});
```

### CORS Issues

Ensure your backend has CORS enabled:

```python
# In gateway/app.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### HTTPS Required

Modern browsers require HTTPS for microphone access (except localhost):

```javascript
if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
    alert('HTTPS is required for microphone access');
}
```

### Audio Not Playing

Check browser autoplay policies:

```javascript
// In mic-button.js, modify audio playback
audioPlayer.play().catch(error => {
    console.log('Autoplay prevented. User interaction required.');
    // Show play button
});
```

---

## Performance Tips

1. **Optimize Audio Format**: Use WebM for smaller file sizes
2. **Debounce Requests**: Prevent multiple simultaneous requests
3. **Show Loading States**: Provide visual feedback during processing
4. **Cache Responses**: Cache common queries client-side
5. **Lazy Load**: Load the component only when needed

---

## Security Considerations

1. **Validate Audio Files**: Server-side validation
2. **Rate Limiting**: Prevent abuse
3. **Authentication**: Add API keys for production
4. **HTTPS Only**: Require secure connections
5. **Content Security Policy**: Configure CSP headers

---

## Examples Repository

Find more examples at:
- `mic-component/embed-example.html` - Basic HTML example
- `mic-component/App.jsx` - React example

---

## Support

For issues or questions:
1. Check the [README.md](README.md)
2. Review [API.md](API.md)
3. Open a GitHub issue
