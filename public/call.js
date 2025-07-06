const socket = io({
  transports: ['websocket'],
  upgrade: false,
  forceNew: true,
  reconnection: true,
  timeout: 60000
});

const localAudio = document.getElementById("localAudio");
const remoteAudio = document.getElementById("remoteAudio");
const transcriptionBox = document.getElementById("transcription");
const callPopup = document.getElementById("callPopup");
const btnCall = document.getElementById("btnCall");

let localStream = null;
let mediaRecorder = null;
let peerConnection = null;

document.getElementById('btnCall').addEventListener('click', handleCallButton);
document.getElementById('btnStopCall').addEventListener('click', stopCall);
document.getElementById('btnMute').addEventListener('click', function() {
  toggleMute(this);
});
document.getElementById('btnShowText').addEventListener('click', showTranscription);
// document.getElementById('btnClosePopup').addEventListener('click', closeCallPopup);

const config = { iceServers: [{ urls: "stun:stun.l.google.com:19302" }] };

// Lấy media stream âm thanh của bạn
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    localStream = stream;
    localAudio.srcObject = stream;
  })
  .catch(err => {
    alert("Không thể truy cập microphone: " + err);
  });

// Socket nhận offer từ người khác
socket.on("offer", async (offer) => {
  openCallPopup();
  peerConnection = new RTCPeerConnection(config);
  setupPeerEvents();

  try {
    await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);
    socket.emit("answer", answer);
  } catch (err) {
    console.error("Lỗi xử lý offer:", err);
  }
});

// Socket nhận answer
socket.on("answer", async (answer) => {
  if (!peerConnection) return;
  try {
    await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
  } catch (err) {
    console.error("Lỗi xử lý answer:", err);
  }
});

// Socket nhận ICE candidate
socket.on("ice", (candidate) => {
  if (peerConnection) {
    peerConnection.addIceCandidate(new RTCIceCandidate(candidate))
      .catch(e => console.error("Lỗi thêm ICE candidate:", e));
  }
});

// Socket nhận transcript text
socket.on("transcript", (data) => {
    console.log("Nhận transcript:", data);

    // Lấy references một lần
    const container = document.getElementById("transcription-container");
    const output = document.getElementById("transcription-output");

    if (!container || !output) {
        console.error("Không tìm thấy elements transcription");
        return;
    }

    // Hiển thị container nếu đang ẩn
    if (container.style.display === "none") {
        container.style.display = "block";
    }

    // Xử lý dữ liệu nhận được
    if (typeof data === 'string') {
        // Nếu nhận trực tiếp string
        output.value += ' ' + data;
    } else if (data.text) {
        // Nếu nhận object có field text
        output.value += ' ' + data.text;
    } else if (data.error) {
        // Nếu có lỗi
        output.value += '\n🔴 Lỗi: ' + data.error;
        console.error('Transcript error:', data.error);
    } else {
        console.warn('Định dạng transcript không hợp lệ:', data);
        return;
    }

    // Auto scroll xuống dưới
    output.scrollTop = output.scrollHeight;
});

// Sửa lại function showTranscription chỉ để toggle hiển thị
function showTranscription() {
  if (transcriptionBox.style.display === "none") {
    transcriptionBox.style.display = "block";
  } else {
    transcriptionBox.style.display = "none"; 
  }
}

async function startSendingAudioStream() {
  if (!localStream) return;

  const audioContext = new AudioContext({
    sampleRate: 16000
  });

  const source = audioContext.createMediaStreamSource(localStream);
  const processor = audioContext.createScriptProcessor(8192, 1, 1);

  source.connect(processor);
  processor.connect(audioContext.destination);

  let chunkIndex = 0;
  const MAX_CHUNKS = 5;
  const audioChunks = [];

  const VOLUME_THRESHOLD = 0.02; // Có thể điều chỉnh

  processor.onaudioprocess = (e) => {
    const inputData = e.inputBuffer.getChannelData(0);

    // Tính RMS để phát hiện tiếng nói
    const rms = Math.sqrt(inputData.reduce((sum, sample) => sum + sample * sample, 0) / inputData.length);
    const isSpeaking = rms > VOLUME_THRESHOLD;

    if (isSpeaking) {
      console.log("🗣️ User is speaking");

      const wavBuffer = createWAVBuffer(inputData, audioContext.sampleRate);
      const base64String = arrayBufferToBase64(wavBuffer);
      audioChunks.push(base64String);

      if (audioChunks.length >= MAX_CHUNKS) {
        audioChunks.forEach((chunk, index) => {
          socket.emit('audio', {
            data: chunk,
            chunkIndex: index,
            totalChunks: audioChunks.length
          });
        });

        audioChunks.length = 0;
        chunkIndex = 0;
      }
    } else {
      console.log("🤫 Silence detected, not sending");
    }
  };

  function createWAVBuffer(audioData, sampleRate) {
    const buffer = new ArrayBuffer(44 + audioData.length * 2);
    const view = new DataView(buffer);

    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + audioData.length * 2, true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeString(view, 36, 'data');
    view.setUint32(40, audioData.length * 2, true);

    let index = 44;
    for (let i = 0; i < audioData.length; i++) {
      view.setInt16(index, audioData[i] * 0x7FFF, true);
      index += 2;
    }

    return buffer;
  }

  function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  }

  function arrayBufferToBase64(buffer) {
    const bytes = new Uint8Array(buffer);
    const binary = bytes.reduce((acc, byte) => acc + String.fromCharCode(byte), '');
    return btoa(binary);
  }

  return () => {
    if (audioChunks.length > 0) {
      audioChunks.forEach((chunk, index) => {
        socket.emit('audio', {
          data: chunk,
          chunkIndex: index,
          totalChunks: audioChunks.length
        });
      });
    }

    processor.disconnect();
    source.disconnect();
    audioContext.close();
  };
}

function stopCall() {
  if (peerConnection) {
    peerConnection.close();
    peerConnection = null;
    remoteAudio.srcObject = null;
    
    // Dọn dẹp audio processing
    if (this.audioCleanup) {
      this.audioCleanup();
      this.audioCleanup = null;
    }
  }
  closeCallPopup();
}
function setupPeerEvents() {
  if (!peerConnection) return;

  peerConnection.onicecandidate = (e) => {
    if (e.candidate) socket.emit("ice", e.candidate);
  };

  peerConnection.ontrack = (e) => {
    remoteAudio.srcObject = e.streams[0];
  };

  if (localStream) {
    localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));
  }
}

// Hàm bật popup và bắt đầu gọi
function startCall() {
  peerConnection = new RTCPeerConnection(config);
  setupPeerEvents();

  peerConnection.createOffer()
    .then(offer => peerConnection.setLocalDescription(offer).then(() => offer))
    .then(offer => {
      socket.emit("offer", offer);
    })
    .catch(err => {
      alert("Lỗi khi tạo offer: " + err);
      console.error(err);
    });
}

// Xử lý nút gọi
function handleCallButton() {
  openCallPopup();
  startCall();
  startSendingAudioStream();
}

// Bật / tắt tiếng micro
function toggleMute(button) {
  if (!localStream) return;

  localStream.getAudioTracks().forEach(track => {
    track.enabled = !track.enabled;
  });

  if (button.innerText === "🔇 Tắt tiếng") {
    button.innerText = "🎤 Bật tiếng";
  } else {
    button.innerText = "🔇 Tắt tiếng";
  }
}

// Mở popup cuộc gọi
function openCallPopup() {
  callPopup.classList.remove("hidden");
  btnCall.disabled = true;
  btnCall.style.backgroundColor = "gray";
}

// Đóng popup cuộc gọi
function closeCallPopup() {
  callPopup.classList.add("hidden");
  btnCall.disabled = false;
  btnCall.style.backgroundColor = "";
}
