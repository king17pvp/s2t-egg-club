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
# Flask & SocketIO Setup
# ============================
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
    nums = 0
    while True:
        client_id, combined_audio = audio_queue.get()
        try:
            print(f"🎧 Xử lý audio từ {client_id}")
            res = requests.post(
                "http://backend:8000/transcribe/",
                json={"audio_base64": combined_audio, "file_ext": "wav"}
            )
            if not res.ok:
                raise Exception(f"API error: {res.status_code}")
            task_data = res.json()
            task_id = task_data.get('task_id')
            if not task_id:
                raise Exception("No task_id in response")

            for _ in range(20):
                result_res = requests.get(f"http://backend:8000/result/{task_id}")
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

        print(f"🎧 Nhận audio từ {client_id}")
        audio_queue.put((client_id, chunk_data))

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
