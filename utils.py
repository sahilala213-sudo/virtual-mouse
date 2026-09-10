"""Small, testable mathematical functions used by gesture detection."""
from __future__ import annotations

import math
from typing import Protocol


class Point(Protocol):
    x: float
    y: float


def get_distance(point_a: Point, point_b: Point) -> float:
    """Return the 2D Euclidean distance between two normalized landmarks."""
    return math.hypot(point_b.x - point_a.x, point_b.y - point_a.y)


def get_angle(point_a: Point, point_b: Point, point_c: Point) -> float:
    """Return angle ABC in degrees; B is the joint/bend point."""
    first = math.atan2(point_a.y - point_b.y, point_a.x - point_b.x)
    second = math.atan2(point_c.y - point_b.y, point_c.x - point_b.x)
    degrees = abs(math.degrees(second - first))
    return 360.0 - degrees if degrees > 180.0 else degrees
