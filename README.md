# TomCam

A custom-designed, 3D-printed accessibility camera prototype built around a **Raspberry Pi 3 B+** and an **800×480 touchscreen**, running a lightweight **PySDL2** UI (`kmsdrm` by default—no Tkinter or Pygame).

## Purpose & Vision

TomCam is designed to empower disabled users to take and create images independently through accessible physical and touch controls.

- **Current Scope (UI Prototype):** A focused two-screen interface containing **Home** and **Take Picture** views, supporting rotary encoder navigation, touch input, and keyboard testing.
- **Custom Hardware:** The camera enclosure/body was custom-designed and 3D-printed by the creator.
- **Planned / Future Directions:**
  - Camera capture pipeline
  - AI image generation / processing features
  - Physical printing support (e.g., `touch_printer`)
  - Optional future sharing/linking to an Instagram account

> **Note:** Camera capture, AI generation, and printer logic are intentionally outside this UI prototype for now—**Shoot Picture** is currently a placeholder.

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

Install the required SDL2 system libraries and DejaVu fonts, then set up the Python virtual environment and dependencies:

```bash
sudo apt update
sudo apt install -y libsdl2-2.0-0 libsdl2-dev libsdl2-ttf-2.0-0 fonts-dejavu-core
cd ~/tomCam
source .venv/bin/activate
pip install -r src/requirements.txt
```

