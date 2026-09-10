"""Virtual Mouse Using Hand Gestures. Press q to quit; d toggles debug mode."""
from __future__ import annotations

import time

import cv2

import config
from gesture_detector import Gesture, GestureDetector
from hand_tracker import HandTracker
from mouse_controller import MouseController


def draw_status(frame, gesture: Gesture, hand_found: bool, fps: float, details: dict) -> None:
    hand_text = "HAND: DETECTED" if hand_found else "HAND: NOT DETECTED"
    hand_colour = (0, 220, 0) if hand_found else (0, 0, 255)
    cv2.putText(frame, hand_text, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, hand_colour, 2)
    cv2.putText(frame, f"GESTURE: {gesture.value}", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"FPS: {fps:.1f}", (20, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, "q: quit | d: debug", (20, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1)
    if config.DEBUG_MODE and details:
        for line, text in enumerate((
            f"Index angle: {details['index_angle']:.1f}",
            f"Middle angle: {details['middle_angle']:.1f}",
            f"Thumb distance: {details['thumb_distance']:.3f}",
        )):
            cv2.putText(frame, text, (20, 125 + line * 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1)


def run_virtual_mouse() -> None:
    camera = cv2.VideoCapture(config.CAMERA_INDEX)
    if not camera.isOpened():
        raise RuntimeError("Could not open webcam. Check camera permission and close other camera apps.")
    tracker, detector, mouse = HandTracker(), GestureDetector(), MouseController()
    previous_time = time.perf_counter()
    try:
        while True:
            success, frame = camera.read()
            if not success:
                print("Could not read a camera frame. Stopping safely.")
                break
            frame = cv2.flip(frame, 1)
            result = tracker.process(frame)
            landmarks = tracker.get_landmarks(result)
            hand_found, gesture, details = landmarks is not None, Gesture.NONE, {}
            if hand_found:
                tracker.draw_landmarks(frame, result)
                gesture, details = detector.detect(landmarks)
                if gesture is Gesture.MOVE:
                    mouse.move_from_normalized(landmarks[8].x, landmarks[8].y)
                elif detector.should_trigger(gesture):
                    mouse.perform_action(gesture)
            else:
                detector.reset()
            now = time.perf_counter()
            fps, previous_time = 1 / max(now - previous_time, 0.0001), now
            draw_status(frame, gesture, hand_found, fps, details)
            cv2.imshow(config.WINDOW_TITLE, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("d"):
                config.DEBUG_MODE = not config.DEBUG_MODE
    finally:
        tracker.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    run_virtual_mouse()
