"""MediaPipe wrapper: converts a webcam frame into 21 hand landmarks."""
from __future__ import annotations

import cv2
import mediapipe as mp

import config


class HandTracker:
    def __init__(self) -> None:
        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=config.MAX_NUM_HANDS,
            model_complexity=1,
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )
        self._drawer = mp.solutions.drawing_utils

    def process(self, frame):
        """MediaPipe needs RGB, while OpenCV camera frames arrive as BGR."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        return self._hands.process(rgb_frame)

    def get_landmarks(self, result):
        if not result.multi_hand_landmarks:
            return None
        return result.multi_hand_landmarks[0].landmark

    def draw_landmarks(self, frame, result) -> None:
        if result.multi_hand_landmarks:
            for hand in result.multi_hand_landmarks:
                self._drawer.draw_landmarks(frame, hand, self._mp_hands.HAND_CONNECTIONS)

    def close(self) -> None:
        self._hands.close()
