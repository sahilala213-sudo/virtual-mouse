"""Turn landmark geometry into clear, configurable hand gestures."""
from __future__ import annotations

from enum import Enum
import time

import config
from utils import get_angle, get_distance


class Gesture(str, Enum):
    NONE = "NONE"
    MOVE = "MOVE"
    LEFT_CLICK = "LEFT CLICK"
    RIGHT_CLICK = "RIGHT CLICK"
    DOUBLE_CLICK = "DOUBLE CLICK"
    SCREENSHOT = "SCREENSHOT"


class GestureDetector:
    def __init__(self) -> None:
        self._candidate = Gesture.NONE
        self._candidate_frames = 0
        self._last_action_time = 0.0
        self._last_triggered = Gesture.NONE

    def detect(self, landmarks):
        """Classify a frame using the requested baseline gesture rules."""
        index_angle = get_angle(landmarks[5], landmarks[6], landmarks[8])
        middle_angle = get_angle(landmarks[9], landmarks[10], landmarks[12])
        thumb_distance = get_distance(landmarks[4], landmarks[5])
        index_straight = index_angle >= config.FINGER_STRAIGHT_ANGLE
        index_bent = index_angle <= config.FINGER_BENT_ANGLE
        middle_straight = middle_angle >= config.FINGER_STRAIGHT_ANGLE
        middle_bent = middle_angle <= config.FINGER_BENT_ANGLE
        thumb_closed = thumb_distance <= config.THUMB_CLOSED_DISTANCE
        thumb_open = thumb_distance >= config.THUMB_OPEN_DISTANCE

        if thumb_closed and index_bent and middle_bent:
            gesture = Gesture.SCREENSHOT
        elif thumb_closed and index_straight:
            gesture = Gesture.MOVE
        elif thumb_open and index_bent and middle_bent:
            gesture = Gesture.DOUBLE_CLICK
        elif thumb_open and index_bent and middle_straight:
            gesture = Gesture.LEFT_CLICK
        elif thumb_open and index_straight and middle_bent:
            gesture = Gesture.RIGHT_CLICK
        else:
            gesture = Gesture.NONE
        return gesture, {"index_angle": index_angle, "middle_angle": middle_angle, "thumb_distance": thumb_distance}

    def should_trigger(self, gesture: Gesture) -> bool:
        """Require stable frames and cooldown; stops one held pose making many clicks."""
        if gesture in (Gesture.NONE, Gesture.MOVE):
            self.reset()
            return False
        if gesture == self._candidate:
            self._candidate_frames += 1
        else:
            self._candidate, self._candidate_frames = gesture, 1
        ready = self._candidate_frames >= config.STABLE_FRAMES_REQUIRED
        cooled_down = time.monotonic() - self._last_action_time >= config.ACTION_COOLDOWN_SECONDS
        if ready and cooled_down and gesture != self._last_triggered:
            self._last_action_time = time.monotonic()
            self._last_triggered = gesture
            return True
        return False

    def reset(self) -> None:
        self._candidate, self._candidate_frames = Gesture.NONE, 0
        self._last_triggered = Gesture.NONE
