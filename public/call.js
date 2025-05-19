const socket = io({
  transports: ['websocket'],
  upgrade: false,
  forceNew: true,
  reconnection: true,
  timeout: 60000
});


const localAudio = document.getElementById("localAudio");
const remoteAudio = document.getElementById("remoteAudio");
const recordedAudio = document.getElementById("recordedAudio");
const transcriptionBox = document.getElementById("transcription");
const callPopup = document.getElementById("callPopup");
const btnCall = document.getElementById("btnCall");

document.getElementById('btnCall').addEventListener('click', handleCallButton);
document.getElementById('btnStopCall').addEventListener('click', stopCall);
document.getElementById('btnMute').addEventListener('click', function() {
  toggleMute(this);
});
document.getElementById('btnS2T').addEventListener('click', speechtoText);
document.getElementById('btnShowText').addEventListener('click', showTranscription);
document.getElementById('btnClosePopup').addEventListener('click', closeCallPopup);

let localStream, mediaRecorder, recordedChunks = [];
let peerConnection;

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

  await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
  const answer = await peerConnection.createAnswer();
  await peerConnection.setLocalDescription(answer);

  socket.emit("answer", answer);
});

// Socket nhận answer
socket.on("answer", async (answer) => {
  if (!peerConnection) return;
  await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
});

// Socket nhận ICE candidate
socket.on("ice", (candidate) => {
  if (peerConnection) {
    peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
  }
});

function setupPeerEvents() {
  if (!peerConnection) return;

  peerConnection.onicecandidate = (e) => {
    if (e.candidate) socket.emit("ice", e.candidate);
  };

  peerConnection.ontrack = (e) => {
    remoteAudio.srcObject = e.streams[0];
  };

  // Thêm track audio từ localStream vào kết nối
  if (localStream) {
    localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));
  }
}

// Hàm bật popup và bắt đầu gọi
function handleCallButton() {
  openCallPopup();
  startCall();
  
}

// Bắt đầu cuộc gọi: tạo offer, gửi qua socket, bắt đầu ghi âm
function startCall() {
  peerConnection = new RTCPeerConnection(config);
  setupPeerEvents();

  peerConnection.createOffer()
    .then(offer => {
      return peerConnection.setLocalDescription(offer).then(() => offer);
    })
    .then(offer => {
      socket.emit("offer", offer);
    })
    .catch(err => {
      alert("Lỗi khi tạo offer: " + err);
    });
  if (localStream) {
    mediaRecorder = new MediaRecorder(localStream);
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) recordedChunks.push(e.data);
    };
  
    mediaRecorder.onstop = () => {
      const blob = new Blob(recordedChunks, { type: "audio/webm" });
      recordedAudio.src = URL.createObjectURL(blob);
    };
  
    mediaRecorder.start();  
  }
}

// Dừng cuộc gọi, đóng kết nối, dừng stream, ẩn popup
function stopCall() {
  if (peerConnection) {
    if (localStream) {
      localStream.getTracks().forEach(track => track.stop());
    }

    peerConnection.close();
    peerConnection = null;

    remoteAudio.srcObject = null;

    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
    }
  }
  closeCallPopup();
}

// Bật / tắt tiếng micro
function toggleMute(button) {
  if (!localStream) return;

  localStream.getAudioTracks().forEach(track => {
    track.enabled = !track.enabled;
  });

  // Đổi icon hoặc màu nút
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

// Chuyển giọng nói thành văn bản (speech-to-text)
function speechtoText() {
  if (!('webkitSpeechRecognition' in window)) {
    alert("Trình duyệt không hỗ trợ nhận diện giọng nói");
    return;
  }

  const recognition = new webkitSpeechRecognition();
  recognition.lang = "vi-VN";  
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    transcriptionBox.value += transcript + "\n";
  };

  recognition.onerror = (event) => {
    alert("Lỗi nhận diện giọng nói: " + event.error);
  };

  recognition.start();
}

// Hiển thị khung transcription nếu đang ẩn
function showTranscription() {
  transcriptionBox.style.display = "block";
  transcriptionBox.focus();
}