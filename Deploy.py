import os
os.environ['EVENTLET_NO_GREENDNS'] = '1'

import eventlet
eventlet.monkey_patch()

from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, emit

# Khởi tạo Flask và SocketIO
app = Flask(__name__, static_folder="public")
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',
    logger=True,
    engineio_logger=True,
    ping_timeout=20,  # Tăng timeout để tránh ngắt kết nối sớm
    ping_interval=25
)

# Lưu trữ danh sách client
clients = set()

# Route phục vụ index.html và các file tĩnh
@app.route("/", methods=["GET", "POST"])
def index():
    return send_from_directory("public", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("public", path)

# WebSocket events
@socketio.on("connect")
def handle_connect():
    clients.add(request.sid)
    print(f"Client connected: {request.sid}")
    emit("connect", {"sid": request.sid})  # Gửi SID về client

@socketio.on("disconnect")
def handle_disconnect():
    if request.sid in clients:
        clients.remove(request.sid)
    print(f"Client disconnected: {request.sid}")

@socketio.on("offer")
def handle_offer(data):
    print(f"Received offer from {request.sid}: {data}")
    for sid in clients:
        if sid != request.sid:  # Không gửi lại cho client gửi offer
            emit("offer", data, room=sid)

@socketio.on("answer")
def handle_answer(data):
    print(f"Received answer from {request.sid}: {data}")
    for sid in clients:
        if sid != request.sid:  # Không gửi lại cho client gửi answer
            emit("answer", data, room=sid)

@socketio.on("ice")
def handle_ice(data):
    print(f"Received ICE candidate from {request.sid}: {data}")
    for sid in clients:
        if sid != request.sid:  # Không gửi lại cho client gửi ICE
            emit("ice", data, room=sid)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))  # Sử dụng cổng 5000 mặc định thay vì 3000
    socketio.run(app, host='0.0.0.0', port=port, debug=False)