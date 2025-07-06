import os
os.environ['EVENTLET_NO_GREENDNS'] = '1'
import eventlet
eventlet.monkey_patch()

import base64
import json
from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, emit
from eventlet.queue import Queue
import requests

# ============================
# Audio Chunk Manager
# ============================
class AudioChunkManager:
    def __init__(self):
        self.chunks = {}

    def add_chunk(self, client_id, chunk_data, chunk_index, total_chunks):
        if client_id not in self.chunks:
            self.chunks[client_id] = {'data': {}, 'total': total_chunks}
        self.chunks[client_id]['data'][chunk_index] = chunk_data

        if len(self.chunks[client_id]['data']) == total_chunks:
            return self.combine_chunks(client_id)
        return None

    def combine_chunks(self, client_id):
        if client_id not in self.chunks:
            return None
        client_chunks = self.chunks[client_id]
        sorted_chunks = [client_chunks['data'][i] for i in range(client_chunks['total'])]
        combined_base64 = ''.join(sorted_chunks)
        del self.chunks[client_id]
        return combined_base64

    def clear_client(self, client_id):
        if client_id in self.chunks:
            del self.chunks[client_id]

# ============================
# Flask & SocketIO Setup
# ============================
chunk_manager = AudioChunkManager()
audio_queue = Queue()
app = Flask(__name__, static_folder="public")
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',
    logger=False,
    engineio_logger=False,
    ping_timeout=20,
    ping_interval=25
)
clients = set()

# ============================
# Worker Function
# ============================
def audio_worker():
    while True:
        client_id, combined_audio = audio_queue.get()
        try:
            print(f"🎧 Xử lý audio từ {client_id}")
            res = requests.post(
                "https://localhost:8000/transcribe",
                json={"audio_base64": combined_audio, "file_ext": "wav"}
            )
            if not res.ok:
                raise Exception(f"API error: {res.status_code}")
            task_data = res.json()
            task_id = task_data.get('task_id')
            if not task_id:
                raise Exception("No task_id in response")

            for _ in range(20):
                result_res = requests.get(f"https://localhost:8000/result/{task_id}")
                result_json = result_res.json()
                print(result_json) 
                status = result_json.get("status")

                if status == "done":
                    socketio.emit('transcript',{ 'text': result_json['transcription'] }, room=client_id)
                    print(f"✅ Transcription complete for {client_id}")
                    break
                elif status == "failed":
                    socketio.emit('transcript', {
                        'error': result_json.get('error', 'Unknown error'),
                        'status': 'failed'
                    }, room=client_id)
                    print(f"❌ Task failed for {client_id}")
                    break
                else:
                    print(f"⏳ [{client_id}] Waiting for result...")
                    eventlet.sleep(2)
            else:
                socketio.emit('transcript', {
                    'error': 'Timeout waiting for transcription',
                    'status': 'timeout'
                }, room=client_id)
        except Exception as e:
            print(f"Error processing audio for {client_id}: {str(e)}")
            socketio.emit('transcript', {'error': str(e), 'status': 'error'}, room=client_id)

# ============================
# Flask Routes
# ============================
@app.route("/", methods=["GET"])
def index():
    return send_from_directory("public", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("public", path)

# ============================
# SocketIO Handlers
# ============================
@socketio.on("connect")
def handle_connect():
    clients.add(request.sid)
    print(f"Client connected: {request.sid}")
    emit("connect", {"sid": request.sid})

@socketio.on("disconnect")
def handle_disconnect():
    clients.discard(request.sid)
    print(f"Client disconnected: {request.sid}")

@socketio.on("audio")
def handle_audio(data_audio):
    try:
        client_id = request.sid
        chunk_data = data_audio.get('data')
        chunk_index = data_audio.get('chunkIndex', 0)
        total_chunks = data_audio.get('totalChunks', 5)

        print(f"📦 Nhận chunk {chunk_index + 1}/{total_chunks} từ {client_id}")
        combined_audio = chunk_manager.add_chunk(client_id, chunk_data, chunk_index, total_chunks)

        if combined_audio:
            print(f"🔄 Ghép {total_chunks} chunks từ {client_id}")
            audio_queue.put((client_id, combined_audio))

    except Exception as e:
        print(f"Error processing chunk: {str(e)}")
        emit('transcript', {'error': str(e), 'status': 'error'})

@socketio.on("offer")
def handle_offer(data):
    for sid in clients:
        if sid != request.sid:
            emit("offer", data, room=sid)

@socketio.on("answer")
def handle_answer(data):
    for sid in clients:
        if sid != request.sid:
            emit("answer", data, room=sid)

@socketio.on("ice")
def handle_ice(data):
    for sid in clients:
        if sid != request.sid:
            emit("ice", data, room=sid)

# ============================
# Main Entry
# ============================
if __name__ == "__main__":
    eventlet.spawn(audio_worker)
    port = int(os.environ.get("PORT", 8001))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
