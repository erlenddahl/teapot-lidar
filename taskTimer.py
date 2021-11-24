import time

class TaskTimer:

    def __init__(self):
        self.timings = {}
        self.reset()

    def reset(self):
        self.last = time.perf_counter()

    def time(self, key):
        if not key in self.timings:
            self.timings[key] = 0

        new_time = time.perf_counter()
        self.timings[key] += new_time - self.last
        self.last = new_time