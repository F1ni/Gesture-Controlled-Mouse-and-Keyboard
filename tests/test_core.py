import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from gesture_control.config import Settings, load_settings, save_settings
from gesture_control.history import GestureHistory
from gesture_control.keyboard import KeyboardButton, emit_key, make_buttons
from gesture_control.mouse_control import MouseState, cursor_position, scroll
from gesture_control.vision import distance, fingers_up, hand_size, is_finger_extended, model_features


class FakeMouse:
    def __init__(self):
        self.calls = []

    def move(self, *args):
        self.calls.append(("move", *args))

    def click(self):
        self.calls.append(("click",))

    def press(self, **kwargs):
        self.calls.append(("press", kwargs["button"]))

    def release(self, **kwargs):
        self.calls.append(("release", kwargs["button"]))

    def wheel(self, **kwargs):
        self.calls.append(("wheel", kwargs["delta"]))


class FakePyAuto:
    def __init__(self):
        self.calls = []

    def size(self):
        return (1920, 1080)

    def press(self, key):
        self.calls.append(("press", key))

    def typewrite(self, key):
        self.calls.append(("typewrite", key))


class FakeCV:
    def circle(self, *args, **kwargs):
        pass


class CoreTests(unittest.TestCase):
    def test_settings_round_trip_and_legacy_names(self):
        settings = Settings(sensitivity=3, drag_click="pointer", camera_index=2)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            save_settings(settings, path)
            self.assertEqual(json.loads(path.read_text())["drag click"], "pointer")
            self.assertEqual(load_settings(path), settings)
        with self.assertRaisesRegex(ValueError, "smoothness"):
            Settings(smoothness=0).validate()

    def test_feature_vector_preserves_released_normalization(self):
        points = [[10, 20]] + [[30, 40] for _ in range(20)]
        result = model_features(points)
        self.assertEqual(len(result), 42)
        self.assertEqual(result[:4], [0, 0, 0.75, 1])
        self.assertEqual(points[0], [0, 0])
        self.assertEqual(hand_size(points), 10)

    def test_cursor_smoothing_and_scroll_direction(self):
        x, y = cursor_position(640, 360, 200, 1280, 720,
                               1920, 1080, 0, 0, 4, 1)
        self.assertAlmostEqual(x, 240)
        self.assertAlmostEqual(y, 135)
        mouse = FakeMouse()
        scroll(2, "scroll up", mouse)
        scroll(2, "scroll down", mouse)
        self.assertEqual(mouse.calls, [("wheel", 2), ("wheel", -2)])

    def test_pointer_click_is_debounced(self):
        points = [[0, 0] for _ in range(21)]
        points[8] = [640, 360]
        points[6] = [620, 350]
        points[4] = [625, 350]
        mouse, state = FakeMouse(), MouseState()
        args = ("pointer", "pointer", None, points, 30, 30, Settings(),
                1280, 720, 200, mouse, FakePyAuto(), FakeCV())
        state.action(*args)
        state.action(*args)
        self.assertEqual(mouse.calls.count(("click",)), 1)

    def test_keyboard_layout_and_key_mapping(self):
        buttons = make_buttons()
        self.assertEqual(len(buttons), 29)
        self.assertTrue(KeyboardButton("Q", 150, 200).contains(150, 200))
        fake = FakePyAuto()
        for label in ("A", "SPACE", "ENTER", "Remove"):
            emit_key(label, fake)
        self.assertEqual(fake.calls, [("typewrite", "a"), ("press", "space"),
                                      ("press", "enter"), ("press", "backspace")])

    def test_gesture_helpers_and_history(self):
        points = [[0, 0] for _ in range(21)]
        points[8] = [0, 1]
        points[6] = [0, 2]
        points[12] = [0, 3]
        points[10] = [0, 2]
        points[20] = [0, 4]
        points[18] = [0, 2]
        points[16] = [0, 4]
        points[14] = [0, 2]
        points[4] = [1, 0]
        points[5] = [2, 0]
        self.assertEqual(fingers_up(points, "RIGHT"), [1, 0, 0, 0, 1])
        self.assertEqual(distance(0, 0, 3, 4), 5)
        self.assertEqual(hand_size(points), 3)
        landmarks = SimpleNamespace(landmark=[SimpleNamespace(x=0, y=0) for _ in range(21)])
        landmarks.landmark[8].y = 0.2
        landmarks.landmark[6].y = 0.4
        self.assertTrue(is_finger_extended(landmarks, 8, "Right"))
        history = GestureHistory(2)
        for gesture in ("pointer", "pointer", "scroll up", "right click"):
            history.add(gesture)
        self.assertEqual(history.recent(), ["right click", "scroll up"])


if __name__ == "__main__":
    unittest.main()
