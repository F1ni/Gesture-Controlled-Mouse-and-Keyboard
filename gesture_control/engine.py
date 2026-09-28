"""Camera loop and gesture routing from the last working application version."""

from dataclasses import dataclass
from pathlib import Path
import threading
import time
from typing import Callable

from .config import HAND_LANDMARKER_PATH, MODEL_PATH, Settings
from .history import GestureHistory
from .keyboard import KeyboardTracker
from .mouse_control import MouseState, scroll
from .vision import (create_hand_landmarker, detect_hands, draw_hand_landmarks, fingers_up,
                     hand_size, landmark_pixels, model_features, which_hand)


@dataclass(frozen=True)
class Feedback:
    camera: str = "Disconnected"
    mode: str = "Idle"
    gesture: str = "—"
    action: str = "—"
    calibration: str = "Not calibrated"
    history: tuple[str, ...] = ()


class ControlEngine:
    CAMERA_WIDTH = 1280
    CAMERA_HEIGHT = 720
    FRAME_MARGIN = 200
    DETECTION_CONFIDENCE = 0.5
    TRACKING_CONFIDENCE = 0.5

    def __init__(self, settings: Settings, on_feedback: Callable[[Feedback], None],
                 on_error: Callable[[str], None], on_done: Callable[[], None]) -> None:
        self.settings = settings
        self.on_feedback = on_feedback
        self.on_error = on_error
        self.on_done = on_done
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.history = GestureHistory()

    def start(self) -> None:
        if self.thread and self.thread.is_alive():
            return
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run, name="gesture-camera", daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()

    def _load_model(self, model_path: Path):
        import torch
        from .model import GestureModel

        if not model_path.is_file():
            raise FileNotFoundError(f"Gesture model missing: {model_path}. Restore model.pth from the release.")
        model = GestureModel(input_size=42, num_classes=4)
        try:
            model.load_state_dict(torch.load(model_path, map_location="cpu", weights_only=True))
        except (RuntimeError, ValueError, OSError) as exc:
            raise RuntimeError(f"Cannot load gesture model {model_path}: {exc}") from exc
        model.eval()
        return model

    def _run(self) -> None:
        try:
            self._capture()
        except (OSError, RuntimeError, ValueError, ImportError) as exc:
            self.on_error(str(exc))
        except Exception as exc:
            # OpenCV and device backends expose their own exception types.
            # Surface these failures in the GUI instead of losing the worker.
            self.on_error(f"{type(exc).__name__}: {exc}")
        finally:
            self.on_done()

    def _capture(self) -> None:
        try:
            import cv2
            import mediapipe as mp
            import mouse
            import numpy as np
            import pyautogui
            import torch
        except ImportError as exc:
            raise ImportError(f"Missing application dependency: {exc}. Run pip install -r requirements.txt") from exc

        model = self._load_model(MODEL_PATH)
        cap = cv2.VideoCapture(self.settings.camera_index)
        if not cap.isOpened():
            cap.release()
            raise RuntimeError(f"Camera {self.settings.camera_index} is unavailable. Check its connection and camera index.")
        cap.set(3, self.CAMERA_WIDTH)
        cap.set(4, self.CAMERA_HEIGHT)
        if not HAND_LANDMARKER_PATH.is_file():
            raise FileNotFoundError(f"Hand landmarker model missing: {HAND_LANDMARKER_PATH}")
        mouse_state = MouseState()
        keyboard = KeyboardTracker()
        normal_threshold = 30
        drag_threshold = 30
        middle_finger_up = False
        previous_time = 0
        feedback = Feedback(camera="Connected", mode="Tracking")
        self.on_feedback(feedback)
        try:
            with create_hand_landmarker(mp, HAND_LANDMARKER_PATH, self.DETECTION_CONFIDENCE,
                                        self.TRACKING_CONFIDENCE) as hands:
                while cap.isOpened() and not self.stop_event.is_set():
                    if cv2.waitKey(10) == 27:  # Esc in the camera preview.
                        break
                    success, image = cap.read()
                    if not success:
                        raise RuntimeError("The camera stopped providing frames. Check its connection.")
                    if self.settings.topviewvalue == 0:
                        image = cv2.flip(image, 1)
                    image, results = detect_hands(image, hands, mp, cv2, int(time.monotonic() * 1000))
                    mode, gesture, action = "Tracking", "No hand", "—"

                    if results.multi_hand_landmarks and len(results.multi_hand_landmarks) <= 1:
                        mode = "Mouse"
                        for hand_landmarks in results.multi_hand_landmarks:
                            draw_hand_landmarks(image, hand_landmarks, cv2)
                            points = landmark_pixels(image, hand_landmarks)
                            features = model_features(points)
                            xindex, yindex = points[8]
                            xmiddle, ymiddle = points[12]
                            xlowerindex, ylowerindex = points[6]
                            xthumbtip, ythumbtip = points[4]
                            fingers = fingers_up(points, which_hand(points))
                            cv2.rectangle(image, (100, 100),
                                          (self.CAMERA_WIDTH - self.FRAME_MARGIN,
                                           self.CAMERA_HEIGHT - self.FRAME_MARGIN), (255, 0, 255), 2)

                            if fingers[0] == 1 and fingers[1] == 0 and fingers[4] == 1 and fingers[3] == 0:
                                middle_finger_up = False
                                gesture = "Pointer pose"
                                action = self.settings.pointer
                                cv2.line(image, (xthumbtip, ythumbtip), (xlowerindex, ylowerindex), (0, 0, 255), 4)
                                self.history.add(action)
                                mouse_state.action(action, "pointer", image, points, normal_threshold,
                                                   drag_threshold, self.settings, self.CAMERA_WIDTH,
                                                   self.CAMERA_HEIGHT, self.FRAME_MARGIN, mouse, pyautogui, cv2)
                            elif fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[4] == 1:
                                middle_finger_up = False
                                gesture = "Index + middle pose"
                                action = self.settings.drag_click
                                cv2.line(image, (xindex, yindex), (xmiddle, ymiddle), (0, 0, 255), 4)
                                self.history.add(action)
                                mouse_state.action(action, "indexandmiddle", image, points,
                                                   normal_threshold, drag_threshold, self.settings,
                                                   self.CAMERA_WIDTH, self.CAMERA_HEIGHT,
                                                   self.FRAME_MARGIN, mouse, pyautogui, cv2)
                            elif (fingers[0] == 1 and fingers[1] == 0 and fingers[3] == 1
                                  and fingers[4] == 1 and not mouse_state.right_click):
                                gesture, action = "Right-click pose", "Right click"
                                self.history.add(action)
                                mouse_state.right_click = True
                                mouse.right_click()
                            elif (fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 0
                                  and fingers[3] == 0 and fingers[4] == 0):
                                gesture, action = "Middle-finger pose", "Close active window"
                                if not middle_finger_up:
                                    middle_finger_up = True
                                    self.history.add("Middle Finger")
                                    pyautogui.hotkey("alt", "f4")
                            else:
                                input_data = torch.tensor(np.array(features, dtype=np.float32).reshape(1, -1),
                                                          dtype=torch.float32)
                                with torch.no_grad():
                                    prediction = torch.argmax(model(input_data)).item()
                                if prediction == 0:
                                    gesture, action = "Learned scroll pose 1", self.settings.scroll_up
                                    self.history.add(action)
                                    scroll(self.settings.scrollingspeed, action, mouse)
                                elif prediction == 1:
                                    gesture, action = "Learned scroll pose 2", self.settings.scroll_down
                                    self.history.add(action)
                                    scroll(self.settings.scrollingspeed, action, mouse)
                                elif prediction == 2:
                                    gesture, action = "Open hand", "Calibrate"
                                    size = hand_size(points)
                                    normal_threshold = int(size * 0.3)
                                    drag_threshold = int(size * 0.2)
                                else:
                                    gesture, action = "Closed hand", "—"
                                middle_finger_up = False
                            if self.history.items:
                                cv2.putText(image, self.history.items[-1], (20, 100),
                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))

                    elif results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
                        mode, gesture = "Keyboard", "Two hands"
                        pressed = keyboard.process(image, results, cv2, pyautogui)
                        if pressed:
                            action = f"Typed {pressed}"

                    now = time.time()
                    fps = 1 / (now - previous_time) if now != previous_time else 0
                    previous_time = now
                    cv2.putText(image, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
                    cv2.putText(image,
                                f"Calibration: {normal_threshold}   Current: {mouse_state.thumb_distance}",
                                (70, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    cv2.imshow("Gesture Recog", image)
                    new_feedback = Feedback(camera="Connected", mode=mode, gesture=gesture,
                                            action=action, calibration=str(normal_threshold),
                                            history=tuple(self.history.recent()))
                    if new_feedback != feedback:
                        feedback = new_feedback
                        self.on_feedback(feedback)
        finally:
            mouse_state.release_drag(mouse)
            cap.release()
            cv2.destroyAllWindows()
