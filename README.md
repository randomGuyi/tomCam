# TomCam

A custom-designed, 3D-printed accessibility camera prototype built around a **Raspberry Pi 3 B+** and an **800×480 touchscreen**, running a lightweight **PySDL2** UI (`kmsdrm` by default—no Tkinter or Pygame).

## Purpose & Vision

TomCam is designed to empower disabled users to take and create images independently through accessible physical and touch controls.

- **Current Scope:** Home, camera, library, settings, Wi-Fi, and voice-to-image screens, supporting rotary encoder navigation, touch input, and keyboard testing.
- **Custom Hardware:** The camera enclosure/body was custom-designed and 3D-printed by the creator.
- **Voice to Image:** Records speech, transcribes it with Google's speech recognition service, sends the text to the configured image API, and previews/saves the returned image.
- **Still in progress:** Camera capture and physical printing.

---

## Hardware & Input Setup

- **Compute:** Raspberry Pi 3 B+
- **Display:** 800×480 touchscreen
- **Printer:** PM290 (BT-Printer)
- **Rotary Encoder (BCM GPIO defaults):**
  - **A:** GPIO `17`
  - **B:** GPIO `18`
  - **Push button:** GPIO `27`
  - *(Configurable in `config/theme.py`)*
- **Camera:** USB-Webcam

---

## Installation

Install the Pi's SDL2, audio, and OpenCV packages, then create a virtual environment that can use those system packages:

```bash
sudo apt update
sudo apt install -y libsdl2-2.0-0 libsdl2-dev libsdl2-ttf-2.0-0 \
  fonts-dejavu-core alsa-utils python3-opencv python3-numpy python3-venv
cd ~/tomCam
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -r src/requirements.txt
```

Set `IMAGE_API_URL` and `IMAGE_API_KEY` in `.env` at the repository root or in `src/.env`. Start the interface from the repository root:

```bash
python src/main.py
```

On the voice-to-image screen, select **Start Recording**, describe the image, select **Stop Recording**, then select **Generate Image**. Transcription and generation run in the background so the display remains responsive. Speech recognition and image generation both require network access. The default Pi microphone is `plughw:1,0`; override it with `TOMCAM_AUDIO_DEVICE` if the microphone uses a different ALSA device.

