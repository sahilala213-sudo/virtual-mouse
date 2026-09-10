"""Safe OS mouse operations and screenshot saving."""
from __future__ import annotations

from datetime import datetime

import pyautogui
from pynput.mouse import Button, Controller

import config
from gesture_detector import Gesture


class MouseController:
    def __init__(self) -> None:
        self._mouse = Controller()
        self._screen_width, self._screen_height = pyautogui.size()
        self._previous_x, self._previous_y = self._screen_width / 2, self._screen_height / 2
        config.SCREENSHOTS_DIRECTORY.mkdir(exist_ok=True)

    def move_from_normalized(self, x: float, y: float) -> None:
        margin = config.ACTIVE_FRAME_MARGIN
        usable_range = 1 - 2 * margin
        x = min(max((x - margin) / usable_range, 0.0), 1.0)
        y = min(max((y - margin) / usable_range, 0.0), 1.0)
        target_x, target_y = x * (self._screen_width - 1), y * (self._screen_height - 1)
        alpha = config.SMOOTHING_ALPHA
        smooth_x = self._previous_x * alpha + target_x * (1 - alpha)
        smooth_y = self._previous_y * alpha + target_y * (1 - alpha)
        self._mouse.position = (int(smooth_x), int(smooth_y))
        self._previous_x, self._previous_y = smooth_x, smooth_y

    def perform_action(self, gesture: Gesture) -> None:
        if gesture is Gesture.LEFT_CLICK:
            self._mouse.click(Button.left, 1)
        elif gesture is Gesture.RIGHT_CLICK:
            self._mouse.click(Button.right, 1)
        elif gesture is Gesture.DOUBLE_CLICK:
            self._mouse.click(Button.left, 2)
        elif gesture is Gesture.SCREENSHOT:
            path = config.SCREENSHOTS_DIRECTORY / datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
            pyautogui.screenshot(str(path))
            print(f"Screenshot saved: {path}")
