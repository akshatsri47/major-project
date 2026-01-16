const startBtn = document.getElementById("start");
const statusEl = document.getElementById("status");
const remoteAudio = document.getElementById("remoteAudio");

let pc;

// Extract room ID from URL
const pathParts = window.location.pathname.split("/");
const roomId = pathParts[1] === "call" ? pathParts[2] : "lobby";

function log(msg) {
  console.log(msg);
  statusEl.textContent = msg;
}

async function startCall() {
  startBtn.disabled = true;

  log("🎤 Requesting microphone...");
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

  pc = new RTCPeerConnection();

  // Send mic to server
  stream.getTracks().forEach((track) => pc.addTrack(track, stream));

  // Play incoming audio
  pc.ontrack = (event) => {
    log("🔊 Connected to caller in room: " + roomId);
    remoteAudio.srcObject = event.streams[0];
  };

  log("📡 Creating offer...");
  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);

  const response = await fetch("/offer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sdp: pc.localDescription.sdp,
      type: pc.localDescription.type,
      room: roomId,
    }),
  });

  const answer = await response.json();
  await pc.setRemoteDescription(answer);

  log("⏳ Waiting for partner in room: " + roomId);
}

startBtn.onclick = startCall;
