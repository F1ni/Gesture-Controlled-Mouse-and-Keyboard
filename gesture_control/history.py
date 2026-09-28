"""Recent recognized actions shown in the UI."""

from collections import deque


class GestureHistory:
    def __init__(self, capacity: int = 5) -> None:
        self.items: deque[str] = deque(maxlen=capacity)
        self.previous_gesture = ""

    def add(self, gesture: str) -> None:
        if gesture != self.previous_gesture:
            self.items.append(gesture)
            self.previous_gesture = gesture

    def recent(self) -> list[str]:
        return list(reversed(self.items))
