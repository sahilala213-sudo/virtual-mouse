from types import SimpleNamespace

from utils import get_angle, get_distance


def point(x, y):
    return SimpleNamespace(x=x, y=y)


def test_distance_uses_pythagoras():
    assert get_distance(point(2, 3), point(5, 7)) == 5.0


def test_straight_line_is_180_degrees():
    assert get_angle(point(0, 0), point(1, 0), point(2, 0)) == 180.0


def test_right_angle_is_90_degrees():
    assert get_angle(point(0, 0), point(0, 1), point(1, 1)) == 90.0
