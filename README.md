# Virtual Mouse Using Hand Gestures

Control the mouse through a webcam using OpenCV, MediaPipe Hands, landmark geometry, `pynput`, and PyAutoGUI.

## Features

| Gesture | Rule | Action |
|---|---|---|
| Move | Thumb closed + index straight | Move cursor with index tip |
| Left click | Thumb open + index bent + middle straight | Left click |
| Right click | Thumb open + index straight + middle bent | Right click |
| Double click | Thumb open + index bent + middle bent | Double click |
| Screenshot | Thumb closed + index bent + middle bent | Save a screenshot |

It includes smoothing, action debounce, stable-frame validation, on-screen feedback, debug information, configurable thresholds, and math tests.

## Architecture

```text
Webcam → OpenCV BGR frame → RGB conversion → MediaPipe 21 landmarks
       → angles/distances → GestureDetector → MouseController → operating system
```

- `main.py`: application loop and visual feedback.
- `hand_tracker.py`: MediaPipe detection and landmark drawing.
- `gesture_detector.py`: converts landmark angles/distances into gestures.
- `mouse_controller.py`: cursor, click, and screenshot actions.
- `utils.py`: Euclidean distance and three-point-angle math.
- `config.py`: thresholds and all changeable settings.

## Install (macOS)

This tutorial-style project needs **Python 3.10 or 3.11**. With Homebrew Python 3.11:

```zsh
cd "/Users/sahilalam/Desktop/Virtual Mouse  "
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

Allow Camera access when macOS asks. For real mouse clicks, allow the terminal/Python app in **System Settings → Privacy & Security → Accessibility**. Screenshot saving may also need **Screen Recording** permission.

## Easiest way to use the web app

1. Complete the one-time install above.
2. Double-click `start_virtual_mouse.command`. It starts the local mouse-control server and opens the app in your browser.
3. In **System Settings → Privacy & Security → Accessibility**, enable the terminal application that opened the server. Without this macOS permission, websites cannot move or click your cursor.
4. Click **Start Camera**. Point your index finger to move, pinch thumb + index to left-click, thumb + middle to right-click, and pinch all three to double-click.

The public GitHub Pages URL is a hand-tracking interface. For safety, a hosted browser page cannot control your computer directly; it connects only to the companion server running on your own Mac.

Press `q` to stop and `d` to show/hide angle and distance debugging data.

## Configuration

Edit `config.py`; for example, raise `SMOOTHING_ALPHA` for a steadier but slower cursor. Gesture thresholds are approximations, not universal constants: hand size, distance from camera, light, and camera angle matter.

## Maths

Euclidean distance is `sqrt((x2-x1)^2 + (y2-y1)^2)`. For A=(2,3) and B=(5,7), the distance is `sqrt(3²+4²)=5`.

The index angle uses landmarks `5 → 6 → 8`: base → joint → tip. Three points are needed because landmark 6 is the bend point. A straight finger is near 180°, while a bent finger moves closer to 90°. `atan2` measures each line direction; subtracting the directions gives the joint angle.

## Tests

```zsh
python -m pytest
```

Real-time detection still needs manual testing because a unit test cannot reproduce lighting, camera position, and hand movement.

## Limitations and future work

One hand is intentionally used for a predictable demo. Fixed gesture thresholds need calibration for different users. A future version can add adaptive calibration, two-hand gestures, and a modern MediaPipe Tasks-API migration.

## Viva quick answer

"This project captures webcam frames using OpenCV, detects the 21 MediaPipe hand landmarks, calculates finger angles and thumb distance, classifies these into gestures, then uses pynput and PyAutoGUI to control the operating-system mouse. Smoothing reduces cursor jitter and debounce prevents repeated clicks."
