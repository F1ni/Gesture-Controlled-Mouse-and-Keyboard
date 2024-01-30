import json

config = {"sensitivity": 1, "smoothness": 4,
          "scrollingspeed": 4, "pointer": "pointer",
          "drag click": "drag click", "scroll up": "scroll up",
          "scroll down": "scroll down", "topviewvalue": 0}

with open('settings.json', 'w') as f:
    json.dump(config, f)
# class CircularGestureQueue: # first in first out
#     def __init__(self, max_size):
#         self.max_size = max_size
#         self.gesture_history = [None] * max_size # intially set to none
#         self.front = 0 # Index of the front element
#         self.rear = 0   # Index where the next element will be inserted
#
#     def add_gesture(self, gesture):
#         # Check if the queue is full before inserting
#         if self.is_full():
#             self.front = (self.front + 1) % self.max_size  # Move the front index in a circular manner
#
#         # when the queue is full the front pointer will move such that the oldest gesture gets replaced by the latest
#
#         self.gesture_history[self.rear] = gesture
#         self.rear = (self.rear + 1) % self.max_size  # Move the rear index in a circular manner
#
#     def get_history(self):
#         # Extract the valid elements in the circular queue
#         history = []
#         for i in range(self.front, self.front + self.size()):
#             index = i % self.max_size
#             history.append(self.gesture_history[index])
#         return history
#
#     def is_full(self):
#         return (self.rear + 1) % self.max_size == self.front
#
#     def size(self):
#         return (self.rear - self.front + self.max_size) % self.max_size
#
#
#
# queue = CircularGestureQueue(6)
#
# for i in range(7):
#     queue.add_gesture(i)
#     print(i)
#     print(queue.get_history())
#     print(queue.front, queue.rear)
#

# def test(value):
#     print(value+1)
#     return value + 1
#
# def main():
#     value = 1
#     print(value)
#     value = test(value)
#     print(value)
#
# main()