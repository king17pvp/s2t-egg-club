# Speech-to-Text Egg Club (s2t-egg-club)

A real-time speech-to-text application using Flask-SocketIO for WebSocket communication and audio streaming.

## Features

- Real-time audio streaming
- WebSocket-based communication for instant transcription
- Chunked audio processing
- Event-driven architecture with Eventlet
- Docker support for easy deployment

## Prerequisites

- Python 3.11.9
- FFmpeg (for audio processing)
- Docker and Docker Compose (optional, for containerized deployment)

## Project Structure

```
s2t-egg-club/
├── Deploy.py           # Main application server
├── pipeline.py         # Audio processing pipeline
├── requirements.txt    # Python dependencies
├── public/            # Static files
├── stt_scic/          # Core application code
├── Dockerfile         # Docker configuration
└── compose.yaml       # Docker Compose configuration
```

## Installation

### Local Development Setup

1. Create a virtual environment:
```bash
python -m venv venv311
# On Windows:
.\venv311\Scripts\activate
# On Unix-like systems:
source venv311/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python Deploy.py
```

The application will be available at `http://localhost:3000`

### Docker Deployment

1. Using Docker Compose (recommended):
```bash
# Build and start the container
docker compose up -d

# View logs
docker compose logs -f

# Stop the container
docker compose down
```

2. Using Docker directly:
```bash
# Build the image
docker build -t s2t-egg-club .

# Run the container
docker run -p 3000:3000 s2t-egg-club
```

The application will be available at `http://localhost:3000`

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

## Troubleshooting

1. If the application fails to start, check:
   - Port 3000 is not in use
   - FFmpeg is installed
   - All dependencies are installed correctly

2. For Docker issues:
   - Ensure Docker daemon is running
   - Check logs with `docker compose logs`
   - Verify port mapping is correct

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]