"""Virtual keyboard geometry and finger press state."""

from dataclasses import dataclass


@dataclass(frozen=True)
class KeyboardButton:
    label: str
    x: int
    y: int
    w: int = 80
    h: int = 80

    def contains(self, px: int, py: int) -> bool:
        return self.x <= px <= self.x + self.w and self.y <= py <= self.y + self.h

    def draw(self, image, cv2, color=(255, 255, 255), pressed=False) -> None:
        if pressed:
            color = (0, 255, 0)
        cv2.rectangle(image, (self.x, self.y), (self.x + self.w, self.y + self.h), color, 2)
        cv2.putText(image, self.label, (self.x + 10, self.y + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)


def make_buttons() -> list[KeyboardButton]:
    buttons = []
    for row_index, row in enumerate(("QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM")):
        for col_index, key in enumerate(row):
            x = 150 + (0, 40, 80)[row_index] + col_index * 90
            y = 200 + row_index * 90
            buttons.append(KeyboardButton(key, x, y))
    buttons.extend((KeyboardButton("SPACE", 250, 470, 400),
                    KeyboardButton("ENTER", 670, 470, 150),
                    KeyboardButton("Remove", 840, 470, 175)))
    return buttons


def emit_key(label: str, pyautogui) -> str:
    key = label.lower()
    if key == "remove":
        pyautogui.press("backspace")
    elif key in ("space", "enter"):
        pyautogui.press(key)
    else:
        pyautogui.typewrite(key)
    return key


class KeyboardTracker:
    def __init__(self) -> None:
        self.buttons = make_buttons()
        self.last_hovered: dict[tuple[str, int], str | None] = {}
        self.extended: dict[tuple[str, int], bool] = {}

    def process(self, image, results, cv2, pyautogui) -> str | None:
        height, width, _ = image.shape
        states = {button.label: {"pressed": False, "hovered": False} for button in self.buttons}
        last_key = None
        for hand_id, hand_landmarks in enumerate(results.multi_hand_landmarks):
            handedness = results.multi_handedness[hand_id].classification[0].label
            from .vision import draw_hand_landmarks
            draw_hand_landmarks(image, hand_landmarks, cv2)
            for fingertip_id in (4, 8, 12, 16, 20):
                from .vision import is_finger_extended
                finger = hand_landmarks.landmark[fingertip_id]
                identity = (handedness, fingertip_id)
                x, y = int(finger.x * width), int(finger.y * height)
                hovered = None
                for button in self.buttons:
                    if button.contains(x, y):
                        states[button.label]["hovered"] = True
                        hovered = button.label
                        break
                extended_now = is_finger_extended(hand_landmarks, fingertip_id, handedness)
                if identity not in self.extended:
                    self.extended[identity] = False
                    self.last_hovered[identity] = None
                if extended_now:
                    self.last_hovered[identity] = hovered
                if self.extended[identity] and not extended_now and self.last_hovered[identity]:
                    label = self.last_hovered[identity]
                    states[label]["pressed"] = True
                    self.last_hovered[identity] = None
                    last_key = emit_key(label, pyautogui)
                self.extended[identity] = extended_now
        for button in self.buttons:
            state = states[button.label]
            if state["pressed"]:
                button.draw(image, cv2, pressed=True)
            elif state["hovered"]:
                button.draw(image, cv2, (144, 213, 255))
            else:
                button.draw(image, cv2)
        return last_key
