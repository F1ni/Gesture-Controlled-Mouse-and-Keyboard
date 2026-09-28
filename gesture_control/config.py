"""User settings and paths, with the original control defaults preserved."""

from dataclasses import asdict, dataclass
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "model.pth"
HAND_LANDMARKER_PATH = PROJECT_ROOT / "hand_landmarker.task"
SETTINGS_PATH = PROJECT_ROOT / "settings.json"
GESTURES_PATH = PROJECT_ROOT / "Model" / "gestures.csv"


@dataclass
class Settings:
    sensitivity: int = 1
    smoothness: int = 4
    scrollingspeed: int = 2
    pointer: str = "pointer"
    drag_click: str = "drag click"
    scroll_up: str = "scroll up"
    scroll_down: str = "scroll down"
    topviewvalue: int = 0
    camera_index: int = 0

    @classmethod
    def from_dict(cls, values: dict) -> "Settings":
        settings = cls(
            sensitivity=values.get("sensitivity", 1),
            smoothness=values.get("smoothness", 4),
            scrollingspeed=values.get("scrollingspeed", 2),
            pointer=values.get("pointer", "pointer"),
            drag_click=values.get("drag click", "drag click"),
            scroll_up=values.get("scroll up", "scroll up"),
            scroll_down=values.get("scroll down", "scroll down"),
            topviewvalue=values.get("topviewvalue", 0),
            camera_index=values.get("camera_index", 0),
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        for name, low, high in (("sensitivity", 1, 10), ("smoothness", 1, 10),
                                ("scrollingspeed", 1, 5)):
            value = getattr(self, name)
            if not isinstance(value, int) or not low <= value <= high:
                raise ValueError(f"{name} must be an integer from {low} to {high}")
        if not isinstance(self.camera_index, int) or self.camera_index < 0:
            raise ValueError("camera_index must be a non-negative integer")
        if self.topviewvalue not in (0, 1):
            raise ValueError("topviewvalue must be 0 or 1")
        for name in ("pointer", "drag_click"):
            if getattr(self, name) not in ("pointer", "drag click"):
                raise ValueError(f"{name} must be 'pointer' or 'drag click'")
        for name in ("scroll_up", "scroll_down"):
            if getattr(self, name) not in ("scroll up", "scroll down"):
                raise ValueError(f"{name} must be 'scroll up' or 'scroll down'")

    def to_dict(self) -> dict:
        result = asdict(self)
        result["drag click"] = result.pop("drag_click")
        result["scroll up"] = result.pop("scroll_up")
        result["scroll down"] = result.pop("scroll_down")
        return result


def load_settings(path: Path = SETTINGS_PATH) -> Settings:
    if not path.exists():
        return Settings()
    try:
        return Settings.from_dict(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, TypeError, KeyError, ValueError) as exc:
        raise ValueError(f"Could not load settings from {path}: {exc}") from exc


def save_settings(settings: Settings, path: Path = SETTINGS_PATH) -> None:
    settings.validate()
    path.write_text(json.dumps(settings.to_dict(), indent=2) + "\n", encoding="utf-8")
