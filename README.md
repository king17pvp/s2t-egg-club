# Speech-to-Text Egg Club (s2t-egg-club)

A real-time speech-to-text application using Flask-SocketIO for WebSocket communication and audio streaming.

## Features

- Real-time audio streaming
- WebSocket-based communication for instant transcription
- Chunked audio processing
- Event-driven architecture with Eventlet
- Docker support for easy deployment

## Prerequisites

- Python 3.10
- FFmpeg (for audio processing)
- Docker and Docker Compose (optional, for containerized deployment)

## Project Structure

```
s2t-egg-club/
├── Deploy.py                 # Main application server
├── pipeline.py               # Audio processing pipeline
├── requirements.txt          # Python dependencies
├── public/                   # Static files
├── stt_scic/                 # Core application code
├── Dockerfile                # Docker configuration
└── docker-compose.yaml       # Docker Compose configuration
```

## Installation

1. Using Docker Compose (recommended):
```bash

# If run for the first time
docker-compose up -d --build

# Build and start the service in detached mode (if run for the second time)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The API for development will be available at `http://localhost:8000`

The demo application will be available at `http://localhost:8001`

## Environment Variables

- `PORT`: Server port (default: 3000)
- `PYTHONUNBUFFERED`: Python output buffering (set to 1 in Docker)

## API Endpoints

- `GET /`: Serves the main application interface
- `WebSocket /`: WebSocket endpoint for real-time audio streaming

## WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `connect` | Client ← Server | Connection established |
| `audio` | Client → Server | Send audio chunk |
| `transcript` | Client ← Server | Receive transcription |
| `offer` | Client ↔ Server | WebRTC offer |
| `answer` | Client ↔ Server | WebRTC answer |
| `ice` | Client ↔ Server | ICE candidate |

## Development

The project uses Eventlet for asynchronous processing and Flask-SocketIO for WebSocket communication. Audio processing is handled in chunks to optimize performance and memory usage.

### Key Components:

- `AudioChunkManager`: Manages audio chunk assembly
- `audio_worker`: Background worker for audio processing
- WebSocket handlers for real-time communication
