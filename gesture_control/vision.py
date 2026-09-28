"""MediaPipe landmark conversion and the original gesture feature math."""

import math
from types import SimpleNamespace


def landmark_pixels(image, landmarks):
    width, height = image.shape[1], image.shape[0]
    return [[int(point.x * width), int(point.y * height)] for point in landmarks.landmark]


def which_hand(points):
    return "LEFT" if points[20][0] - points[16][0] < 0 else "RIGHT"


def fingers_up(points, hand):
    fingers = [int(points[tip][1] < points[joint][1]) for tip, joint in
               ((8, 6), (12, 10), (16, 14), (20, 18))]
    fingers.append(int((hand == "RIGHT" and points[4][0] < points[5][0]) or
                       (hand == "LEFT" and points[4][0] > points[5][0])))
    return fingers


def model_features(points):
    """Return the exact 42 values used by the released model.

    The original normalizer only subtracts the wrist from point zero before
    flattening and scaling. This is unusual, but changing it would invalidate
    the trained weights and gesture dataset.
    """
    # The original function also changed the wrist in the caller's list. The
    # later open-hand calibration observes that zeroed wrist, so retain it.
    points[0][0] = 0
    points[0][1] = 0
    flat = [value for point in points for value in point]
    maximum = max(map(abs, flat))
    return [value / maximum for value in flat]


def distance(x1, y1, x2, y2):
    return int(math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))


def hand_size(points):
    """Preserve the original open-hand calibration formula."""
    wrist_x, wrist_y = points[0]
    middle_x, middle_y = points[12]
    return math.sqrt((wrist_x - wrist_y) ** 2 + (middle_x - middle_y) ** 2)


def create_hand_landmarker(mp, model_path, detection_confidence, tracking_confidence):
    vision = mp.tasks.vision
    options = vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=detection_confidence,
        min_tracking_confidence=tracking_confidence,
    )
    return vision.HandLandmarker.create_from_options(options)


def detect_hands(image, hand_landmarker, mp, cv2, timestamp_ms):
    """Run the current MediaPipe Tasks API and adapt its result to this app's API."""
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = hand_landmarker.detect_for_video(
        mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), timestamp_ms
    )
    landmarks = [SimpleNamespace(landmark=hand) for hand in result.hand_landmarks]
    handedness = [SimpleNamespace(classification=[SimpleNamespace(label=labels[0].category_name)])
                  for labels in result.handedness]
    return image, SimpleNamespace(multi_hand_landmarks=landmarks, multi_handedness=handedness)


def draw_hand_landmarks(image, landmarks, cv2):
    height, width = image.shape[:2]
    connections = ((0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8),
                   (5, 9), (9, 10), (10, 11), (11, 12), (9, 13), (13, 14), (14, 15),
                   (15, 16), (13, 17), (17, 18), (18, 19), (19, 20), (0, 17))
    points = [(int(point.x * width), int(point.y * height)) for point in landmarks.landmark]
    for start, end in connections:
        cv2.line(image, points[start], points[end], (0, 255, 0), 2)
    for point in points:
        cv2.circle(image, point, 3, (0, 0, 255), -1)


def is_finger_extended(hand_landmarks, fingertip_id, handedness):
    if fingertip_id == 4:
        if handedness == "Right":
            return hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x
        return hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x
    return hand_landmarks.landmark[fingertip_id].y < hand_landmarks.landmark[fingertip_id - 2].y
