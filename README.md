````markdown
# 🎧 Multi Audio Streamer

**Stream your PC audio to multiple devices simultaneously — wirelessly over Wi-Fi**

Break the limits of your operating system.

---

## 🔥 What is Multi Audio Streamer?

**Multi Audio Streamer** is a lightweight Windows application that streams your **system audio** to multiple devices (phones, tablets, etc.) over **Wi-Fi**, with each device able to use its **own Bluetooth earbuds** or headphones.

> ❌ No OS supports this natively — not Windows, not macOS, not Linux.  
> ✅ Multi Audio Streamer makes it possible — with zero setup on listener devices.

---

## ✨ Key Features

- ✅ **Connect Unlimited Devices**  
  Stream to 2, 3, or more phones at once — no special app required.

- ✅ **No App Needed on Phones**  
  Listeners just open a browser and tap "Play" — no installations.

- ✅ **Works With Bluetooth**  
  Each phone can connect to its own Bluetooth earbuds or speaker.

- ✅ **Low-Latency Streaming**  
  Built with `WebRTC + WebSockets` for real-time, synced audio.

- ✅ **Fully Local**  
  No internet needed. Entirely offline. Your data stays on your network.

- ✅ **Cross-Browser Compatible**  
  Works with Chrome, Safari, Firefox, and more.

---

## 🧠 How It Works

1. Run the provided `.exe` on your **Windows 10/11** PC.
2. The app starts a local web server and displays an IP address (e.g. `http://192.168.1.5:8000`).
3. On any phone/tablet connected to the **same Wi-Fi**, open that link in a browser.
4. Tap ▶ **Play** — the system audio from your PC streams directly to the device.
5. Connect Bluetooth headphones to the phone (optional).
6. Repeat the process on multiple devices — all stay in sync!

---

## 🔧 Requirements

### 🖥️ PC (Host)
- Windows 10 or 11
- `Stereo Mix` enabled and selected as input device
- Stable Wi-Fi connection
- Audio output (speakers/headphones)
- Run the `.exe` — no installation needed

### 📱 Phones/Tablets (Listeners)
- Any modern smartphone or tablet
- Browser: Chrome, Safari, Firefox, etc.
- Connected to the **same Wi-Fi**
- (Optional) Bluetooth headphones

---

## 💡 Example Use Cases

- 🎬 **Quiet Movie Nights** — Stream audio to multiple earbuds without disturbing others
- 🎧 **Couples Watching Together** — No need to share a single pair of earbuds
- 📚 **Study or Lecture Sharing** — Share a single PC’s audio with multiple students
- 🧑‍🏫 **Classroom Training** — Synchronized audio across multiple devices

---

## 📥 Download

> 💡 Replace this with your actual download link.

[➡️ Download Multi Audio Streamer](#)

---

## 🛠️ Build Instructions (For Developers)

If you're building from source:

### 🔗 Dependencies

- Python 3.10+
- FastAPI
- Uvicorn
- aiortc
- av
- sounddevice
- numpy

Install dependencies:

```bash
pip install -r requirements.txt
````

Or manually:

```bash
pip install fastapi uvicorn aiortc av sounddevice numpy
```

### ▶️ Run Locally

```bash
python server.py
```

Then open `http://<your-wifi-ip>:8000` on any device connected to the same Wi-Fi.

---

## 📦 Packaging to EXE

Build with **PyInstaller**:

```bash
pyinstaller advanced/server.py --icon=audio.webp --onefile \
  --hidden-import fastapi --hidden-import uvicorn --hidden-import starlette \
  --hidden-import anyio --hidden-import aiortc --hidden-import av \
  --clean --log-level=DEBUG
```

Resulting `.exe` will run without any installation needed.

---

## 🧪 Optional: Hardware Locking (Disabled by Default)

This app includes (commented-out) logic to restrict execution to authorized machines using:

* Motherboard serial number
* System UUID
* SHA-256 + HMAC verification

If needed, you can uncomment and configure the `AUTHORIZED_MB_HASH` and `AUTHORIZED_UUID_HASH` to enable licensing or machine-lock.

---

## 🔐 Privacy & Security

* No data leaves your network
* No third-party servers or analytics
* No installation required

---

## 📌 Notes

* If audio doesn't stream, ensure **Stereo Mix** is enabled in Windows Sound Settings.
* If `ipconfig` fails to return your IP, manually check your IPv4 under the **Wi-Fi adapter** section.
* The app uses `sounddevice` with `WASAPI` loopback for system audio capture.

---

## ❤️ Credits

* Built with [FastAPI](https://fastapi.tiangolo.com/), [aiortc](https://github.com/aiortc/aiortc), and [AV](https://github.com/PyAV-Org/PyAV)
* Developed by [Aryan Chauhan]
* Icons and UI inspired by modern audio tools

---

## 👂 Share Your Sound.

Feel free to use, modify, and distribute with credit.
🎧 Stay in Sync.
📱 Connect Without Limits.

---
