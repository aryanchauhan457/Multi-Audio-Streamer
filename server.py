import uvicorn

import asyncio
import logging
import fractions
import sounddevice as sd
import numpy as np

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack, MediaStreamError
from aiortc.contrib.media import MediaRelay
from av import AudioFrame

# --- Validation Imports and Logic ---
# import hmac
# import subprocess
# import re
# import hashlib
# from typing import Optional, Dict
# import sys

# Replace with your authorized hashes
# AUTHORIZED_MB_HASH = "a"
# AUTHORIZED_UUID_HASH = "b"

# def _try_wmi():
#     try:
#         import wmi  # type: ignore
#         return wmi.WMI()
#     except ImportError:
#         return None

# def _wmic_get(classname: str, prop: str) -> Optional[str]:
#     try:
#         output = subprocess.check_output(
#             ["wmic", classname, "get", prop, "/value"],
#             stderr=subprocess.DEVNULL,
#             text=True
#         )
#         match = re.search(rf"{prop}=(.+)", output)
#         if match:
#             return match.group(1).strip()
#     except Exception:
#         pass
#     return None

# def get_motherboard_serial() -> Optional[str]:
#     c = _try_wmi()
#     if c:
#         try:
#             for board in c.Win32_BaseBoard():
#                 sn = getattr(board, "SerialNumber", None)
#                 if sn:
#                     return str(sn).strip()
#         except Exception:
#             pass
#     return _wmic_get("baseboard", "SerialNumber")

# def get_system_uuid() -> Optional[str]:
#     c = _try_wmi()
#     if c:
#         try:
#             for sys in c.Win32_ComputerSystemProduct():
#                 uuid = getattr(sys, "UUID", None)
#                 if uuid and not uuid.startswith("00000000"):
#                     return str(uuid).strip()
#         except Exception:
#             pass
#     return _wmic_get("computersystemproduct", "UUID")

# def get_identifiers() -> Dict[str, Optional[str]]:
#     return {
#         "motherboard_serial": get_motherboard_serial(),
#         "system_uuid": get_system_uuid()
#     }

# def hash_value(value: str) -> str:
#     return hashlib.sha256(value.encode("utf-8")).hexdigest()

# def is_authorized(ids: dict) -> bool:
#     mb = ids.get("motherboard_serial")
#     uuid = ids.get("system_uuid")
#     if not mb or not uuid:
#         return False
#     mb_hash = hash_value(mb)
#     uuid_hash = hash_value(uuid)
#     return (
#         hmac.compare_digest(mb_hash, AUTHORIZED_MB_HASH) and
#         hmac.compare_digest(uuid_hash, AUTHORIZED_UUID_HASH)
#     )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("audio-stream")

app = FastAPI()

HTML_CONTENT = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>System Audio Stream</title>
  <style>
    /* Global Styles */
    body {
      margin: 0;
      padding: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #1f1c2c, #928dab);
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
    }

    /* Card Container */
    .container {
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(12px);
      border-radius: 16px;
      padding: 40px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
      text-align: center;
      max-width: 400px;
      width: 90%;
    }

    h1 {
      font-size: 1.8em;
      margin-bottom: 10px;
    }

    p {
      font-size: 1em;
      margin-bottom: 24px;
      color: #dcdcdc;
    }

    /* Buttons */
    button {
      padding: 12px 24px;
      font-size: 1em;
      font-weight: bold;
      border: none;
      border-radius: 8px;
      margin: 0 8px;
      cursor: pointer;
      transition: all 0.3s ease;
      background: #ffffff22;
      color: #fff;
    }

    button:hover {
      background: #ffffff44;
    }

    /* Hide audio bar */
    audio {
      display: none;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>System Audio Stream</h1>
    <p>Click Play to listen to system audio from this PC.</p>
    <button id="play">▶ Play</button>
    <button id="stop" style="display:none;">⏹ Stop</button>
    <audio id="audio" autoplay></audio>
  </div>

  <script>
    const wsUrl = `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`;
    let pc = null;
    let ws = null;
    const audioEl = document.getElementById("audio");
    const playBtn = document.getElementById("play");
    const stopBtn = document.getElementById("stop");

    async function start() {
      ws = new WebSocket(wsUrl);
      pc = new RTCPeerConnection();

      pc.onicecandidate = (evt) => {
        if (evt.candidate && ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: "candidate", candidate: evt.candidate }));
        }
      };

      pc.ontrack = (event) => {
        audioEl.srcObject = event.streams[0];
      };

      ws.onopen = async () => {
        const offer = await pc.createOffer({ offerToReceiveAudio: true });
        await pc.setLocalDescription(offer);
        ws.send(JSON.stringify({ type: pc.localDescription.type, sdp: pc.localDescription.sdp }));
      };

      ws.onmessage = async (evt) => {
        const msg = JSON.parse(evt.data);
        if (!pc) return;

        if (msg.type === "answer") {
          await pc.setRemoteDescription({ type: "answer", sdp: msg.sdp });
        } else if (msg.type === "candidate") {
          try {
            await pc.addIceCandidate(msg.candidate);
          } catch (e) { console.warn("addIceCandidate error", e); }
        }
      };

      playBtn.style.display = "none";
      stopBtn.style.display = "inline-block";
    }

    async function stop() {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "bye" }));
        ws.close();
      }
      ws = null;

      if (pc) {
        try {
          pc.getSenders().forEach(s => { try { s.track && s.track.stop(); } catch(e) {} });
          pc.getTransceivers().forEach(t => { try { t.stop(); } catch(e) {} });
          pc.close();
        } catch (e) {}
      }
      pc = null;

      audioEl.srcObject = null;
      playBtn.style.display = "inline-block";
      stopBtn.style.display = "none";
    }

    playBtn.addEventListener("click", start);
    stopBtn.addEventListener("click", stop);
  </script>
</body>
</html>

'''

@app.get("/")
async def index():
    return HTMLResponse(content=HTML_CONTENT)


class SystemAudioTrack(MediaStreamTrack):
    """
    MediaStreamTrack that reads system audio with sounddevice (low latency).
    """

    kind = "audio"

    def __init__(self):
        super().__init__()
        self.sample_rate = 48000
        self.channels = 2
        self.samples_per_frame = 960  # 20 ms at 48kHz
        self.timestamp = 0
        self.q = asyncio.Queue()

        # Open sounddevice WASAPI loopback or default input
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
            blocksize=self.samples_per_frame,
            callback=self._callback
        )
        self.stream.start()

    def _callback(self, indata, frames, time, status):
        if status:
            print("Sounddevice status:", status)
        # Put audio block into async queue
        try:
            self.q.put_nowait(indata.copy())
        except asyncio.QueueFull:
            pass  # drop if overloaded

    async def recv(self):
        try:
            data = await self.q.get()
        except Exception:
            raise MediaStreamError

        frame = AudioFrame(format="s16", layout="stereo", samples=len(data))
        frame.planes[0].update(data.tobytes())
        frame.sample_rate = self.sample_rate
        frame.pts = self.timestamp
        frame.time_base = fractions.Fraction(1, self.sample_rate)
        self.timestamp += len(data)
        return frame

    def stop(self):
        super().stop()
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None


relay = MediaRelay()
peer_connections = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info(f"Client connected: {websocket.client}")

    pc = RTCPeerConnection()
    peer_connections.add(pc)

    local_audio = SystemAudioTrack()
    pc.addTrack(relay.subscribe(local_audio))

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        if pc.connectionState in ["failed", "closed"]:
            await pc.close()
            peer_connections.discard(pc)

    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "offer":
                offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                await pc.setRemoteDescription(offer)
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                await websocket.send_json(
                    {"type": pc.localDescription.type, "sdp": pc.localDescription.sdp}
                )
            elif data["type"] == "bye":
                break
    except WebSocketDisconnect:
        pass
    finally:
        await pc.close()
        peer_connections.discard(pc)

import subprocess
import re

def get_wifi_ip_windows():
    try:
        output = subprocess.check_output("ipconfig", text=True, encoding="utf-8")
        
        # Look for the Wi-Fi adapter section
        wifi_section = re.search(r"Wireless LAN adapter Wi-Fi(.+?)(?=\n\S|\Z)", output, re.DOTALL | re.IGNORECASE)
        if not wifi_section:
            return None

        # Look for IPv4 Address inside that section
        ip_match = re.search(r"IPv4 Address[.\s]*: ([\d.]+)", wifi_section.group(1))
        if ip_match:
            return ip_match.group(1)
    except Exception as e:
        print(f"Error getting Wi-Fi IP: {e}")
    
    return None

if __name__ == "__main__":
    # ids = get_identifiers()
    # if not is_authorized(ids):
    #     print("❌ Unauthorized machine. Access denied.")
    #     sys.exit(1)

    # ip = get_wifi_ip_windows()
    # if not ip:
    #     ip = "localhost"
    #     print("⚠️ Could not determine Wi-Fi IPv4. Defaulting to localhost.\nEnter ipconfig in CMD and get your ip. then try http://your-ip:8000")
    # else:
    #     #✅ Authorized machine. 
    #     print(f"Server will be accessible at: http://{ip}:8000")
    print("\n**********************************\nEnter ipconfig in CMD and get your WiFi IPv4. then try http://your-ip:8000\n**********************************\n")

    import uvicorn
    uvicorn.run(app, port=8000, log_level=None)

# if __name__ == "__main__":
#     ids = get_identifiers()
#     if not is_authorized(ids):
#         print("❌ Unauthorized machine. Access denied.")
#         sys.exit(1)  # Exit the script if machine is not authorized
#     print("✅ Authorized machine. Starting server...")

#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


#pyinstaller advanced/server.py --icon=audio.webp --onefile --hidden-import fastapi --hidden-import uvicorn --hidden-import starlette --hidden-import anyio --hidden-import aiortc --hidden-import av --clean --log-level=DEBUG
