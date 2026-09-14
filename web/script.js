import {
  FilesetResolver,
  HandLandmarker,
  DrawingUtils
} from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/+esm";

const video = document.getElementById("video");
const canvas = document.getElementById("overlay");
const ctx = canvas.getContext("2d");

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");

const cameraStatus = document.getElementById("cameraStatus");
const handStatus = document.getElementById("handStatus");
const gestureStatus = document.getElementById("gestureStatus");
const errorMessage = document.getElementById("errorMessage");
const placeholder = document.getElementById("placeholder");
const serverStatus = document.getElementById("serverStatus");

// The hosted page talks only to a companion server running on this computer.
// A browser cannot directly control the operating-system cursor.
const isLocalApp = ["127.0.0.1", "localhost"].includes(window.location.hostname);
const serverUrl = new URLSearchParams(window.location.search).get("server") ||
  (isLocalApp ? window.location.origin : "http://127.0.0.1:8765");

let stream = null;
let handLandmarker = null;
let animationId = null;
let cameraRunning = false;

let lastMouseTime = 0;
const mouseUpdateInterval = 35;

let lastGestureTime = 0;
let gestureLocked = false;
const gestureCooldown = 600;


function showError(message) {
  errorMessage.textContent = message;
  console.error(message);
}


async function loadHandModel() {
  cameraStatus.textContent = "Loading model...";

  const vision = await FilesetResolver.forVisionTasks(
    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm"
  );

  handLandmarker = await HandLandmarker.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath:
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
      delegate: "GPU"
    },
    runningMode: "VIDEO",
    numHands: 1,
    minHandDetectionConfidence: 0.6,
    minHandPresenceConfidence: 0.6,
    minTrackingConfidence: 0.6
  });
}


async function sendMousePosition(x, y) {
  try {
    const response = await fetch(`${serverUrl}/move`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        x: x,
        y: y
      })
    });
    if (!response.ok) throw new Error("Mouse server rejected movement");
    serverStatus.textContent = "Local mouse control: connected";
  } catch (error) {
    serverStatus.textContent = "Local mouse control: unavailable";
    console.error("Mouse movement request failed:", error);
  }
}


async function sendClick(button) {
  try {
    const response = await fetch(`${serverUrl}/click`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        button: button
      })
    });
    if (!response.ok) throw new Error("Mouse server rejected click");
    serverStatus.textContent = "Local mouse control: connected";
  } catch (error) {
    serverStatus.textContent = "Local mouse control: unavailable";
    console.error("Click request failed:", error);
  }
}


async function sendDoubleClick() {
  try {
    const response = await fetch(`${serverUrl}/double-click`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      }
    });
    if (!response.ok) throw new Error("Mouse server rejected double click");
    serverStatus.textContent = "Local mouse control: connected";
  } catch (error) {
    serverStatus.textContent = "Local mouse control: unavailable";
    console.error("Double click request failed:", error);
  }
}


function landmarkDistance(first, second) {
  return Math.hypot(first.x - second.x, first.y - second.y);
}


function moveCursorWithIndexFinger(landmarks) {
  const now = performance.now();

  if (now - lastMouseTime < mouseUpdateInterval) {
    return;
  }

  lastMouseTime = now;

  const indexFinger = landmarks[8];

  // Camera mirror hone ki wajah se X reverse kiya gaya hai
  const x = 1 - indexFinger.x;
  const y = indexFinger.y;

  sendMousePosition(x, y);
}


function detectGesture(landmarks) {
  const thumbTip = landmarks[4];
  const indexTip = landmarks[8];
  const indexPip = landmarks[6];
  const middleTip = landmarks[12];
  const middlePip = landmarks[10];

  // Scale the pinch threshold to the user's hand size.
  const handScale = landmarkDistance(landmarks[0], landmarks[9]);
  const pinchThreshold = handScale * 0.48;
  const indexPinched = landmarkDistance(thumbTip, indexTip) < pinchThreshold;
  const middlePinched = landmarkDistance(thumbTip, middleTip) < pinchThreshold;

  const indexStraight = indexTip.y < indexPip.y - 0.02;
  const middleStraight = middleTip.y < middlePip.y - 0.02;

  let currentGesture = "None";

  if (indexPinched && middlePinched) {
    currentGesture = "Double Click";
  } else if (indexPinched) {
    currentGesture = "Left Click";
  } else if (middlePinched) {
    currentGesture = "Right Click";
  } else if (indexStraight && !middleStraight) {
    currentGesture = "Move";
  }

  gestureStatus.textContent = currentGesture;

  const now = performance.now();

  if (
    currentGesture !== "Move" &&
    currentGesture !== "None" &&
    !gestureLocked &&
    now - lastGestureTime > gestureCooldown
  ) {
    gestureLocked = true;
    lastGestureTime = now;

    if (currentGesture === "Left Click") {
      sendClick("left");
    } else if (currentGesture === "Right Click") {
      sendClick("right");
    } else if (currentGesture === "Double Click") {
      sendDoubleClick();
    }
  }

  if (currentGesture === "Move" || currentGesture === "None") {
    gestureLocked = false;
  }

  if (currentGesture === "Move") {
    moveCursorWithIndexFinger(landmarks);
  }
}


async function startCamera() {
  try {
    errorMessage.textContent = "";
    startBtn.disabled = true;
    cameraStatus.textContent = "Starting camera...";

    if (!handLandmarker) {
      await loadHandModel();
    }

    stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: 640,
        height: 480,
        facingMode: "user"
      },
      audio: false
    });

    video.srcObject = stream;

    video.onloadedmetadata = () => {
      video.play();

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      placeholder.style.display = "none";

      cameraRunning = true;

      cameraStatus.textContent = "Camera running";
      handStatus.textContent = "Searching...";
      gestureStatus.textContent = "None";

      stopBtn.disabled = false;

      detectHands();
    };
  } catch (error) {
    startBtn.disabled = false;
    cameraStatus.textContent = "Camera stopped";
    showError(error.message);
  }
}


function stopCamera() {
  cameraRunning = false;

  if (animationId) {
    cancelAnimationFrame(animationId);
    animationId = null;
  }

  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
    stream = null;
  }

  video.srcObject = null;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  placeholder.style.display = "flex";

  cameraStatus.textContent = "Camera stopped";
  handStatus.textContent = "Not detected";
  gestureStatus.textContent = "None";

  startBtn.disabled = false;
  stopBtn.disabled = true;

  gestureLocked = false;
  lastGestureTime = 0;
}


function detectHands() {
  if (!cameraRunning || !handLandmarker) {
    return;
  }

  if (video.readyState >= 2) {
    const result = handLandmarker.detectForVideo(
      video,
      performance.now()
    );

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const drawingUtils = new DrawingUtils(ctx);

    if (result.landmarks && result.landmarks.length > 0) {
      const landmarks = result.landmarks[0];

      drawingUtils.drawConnectors(
        landmarks,
        HandLandmarker.HAND_CONNECTIONS,
        {
          color: "#00ff00",
          lineWidth: 3
        }
      );

      drawingUtils.drawLandmarks(landmarks, {
        color: "#ff0000",
        lineWidth: 1,
        radius: 4
      });

      handStatus.textContent = "Detected";

      detectGesture(landmarks);
    } else {
      handStatus.textContent = "Not detected";
      gestureStatus.textContent = "None";
    }
  }

  animationId = requestAnimationFrame(detectHands);
}


startBtn.addEventListener("click", startCamera);
stopBtn.addEventListener("click", stopCamera);

cameraStatus.textContent = "Camera stopped";
stopBtn.disabled = true;

fetch(`${serverUrl}/health`, { method: "GET" })
  .then((response) => {
    serverStatus.textContent = response.ok
      ? "Local mouse control: connected"
      : "Local mouse control: unavailable";
  })
  .catch(() => {
    serverStatus.textContent = "Local mouse control: start mouse_server.py to enable";
  });
