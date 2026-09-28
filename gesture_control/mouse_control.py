"""Original cursor, click, drag and wheel behavior."""

from dataclasses import dataclass

from .vision import distance


def cursor_position(xindex, yindex, frame_margin, camera_width, camera_height,
                    screen_width, screen_height, previous_x, previous_y,
                    smoothness, sensitivity):
    """Original linear extrapolation and smoothing, including unclamped edges."""
    import numpy as np
    x = float(np.interp(xindex, (frame_margin, camera_width - frame_margin), (0, screen_width)))
    y = float(np.interp(yindex, (frame_margin, camera_height - frame_margin), (0, screen_height)))
    return (previous_x + (x - previous_x) / (smoothness * sensitivity),
            previous_y + (y - previous_y) / (smoothness * sensitivity))


@dataclass
class MouseState:
    previous_x: float = 0
    previous_y: float = 0
    normal_click: bool = False
    drag_click: bool = False
    right_click: bool = False
    thumb_distance: int | None = None

    def action(self, name, gesture, image, points, normal_threshold, drag_threshold,
               settings, camera_width, camera_height, frame_margin, mouse, pyautogui, cv2):
        xindex, yindex = points[8]
        xmiddle, ymiddle = points[12]
        xlowerindex, ylowerindex = points[6]
        xthumbtip, ythumbtip = points[4]
        screen_width, screen_height = pyautogui.size()
        current_x, current_y = cursor_position(
            xindex, yindex, frame_margin, camera_width, camera_height,
            screen_width, screen_height, self.previous_x, self.previous_y,
            settings.smoothness, settings.sensitivity)
        self.thumb_distance = distance(xlowerindex, ylowerindex, xthumbtip, ythumbtip)
        middle_distance = distance(xmiddle, ymiddle, xindex, yindex)
        cv2.circle(image, center=(xindex, yindex), radius=10, color=(0, 255, 0))
        mouse.move(current_x, current_y)
        self.previous_x, self.previous_y = current_x, current_y

        if name == "pointer":
            self.right_click = False
            if gesture == "pointer":
                # The released pointer click used 70 pixels, even after calibration.
                if self.thumb_distance < 70:
                    if not self.normal_click:
                        self.normal_click = True
                        mouse.click()
                else:
                    self.normal_click = False
            elif gesture == "drag click":
                if middle_distance < drag_threshold:
                    if not self.normal_click:
                        self.normal_click = True
                        mouse.click()
                else:
                    self.normal_click = False
        elif name == "drag click":
            if gesture == "pointer":
                if self.thumb_distance < normal_threshold:
                    self.drag_click = True
                    mouse.press(button="left")
                elif self.drag_click:
                    mouse.release(button="left")
                    self.drag_click = False
            elif gesture == "indexandmiddle":
                if middle_distance < drag_threshold:
                    self.drag_click = True
                    mouse.press(button="left")
                elif self.drag_click:
                    mouse.release(button="left")
                    self.drag_click = False

    def release_drag(self, mouse) -> None:
        if self.drag_click:
            mouse.release(button="left")
            self.drag_click = False


def scroll(speed, option, mouse) -> None:
    mouse.wheel(delta=speed if option == "scroll up" else -speed)
