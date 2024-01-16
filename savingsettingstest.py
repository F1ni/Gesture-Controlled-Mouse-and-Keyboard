import json

config = {"sensitivity": 1, "smoothness": 4,
          "scrollingspeed": 4, "pointer": "pointer",
          "drag click": "drag click", "scroll up": "scroll up",
          "scroll down": "scroll down"}

with open('settings.json', 'w') as f:
    json.dump(config, f)
