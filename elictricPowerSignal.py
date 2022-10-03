import math
import time


class AlternativeVoltage():
    def __init__(self, max, freq):
        self.startNanoTime = time.perf_counter_ns()
        self.preTime = self.startNanoTime
        self.vMax = max
        self.freq = freq

    def __iter__(self):
        return self

    def __next__(self):
        self.now = time.perf_counter_ns()
        self.interval = (self.now - self.preTime)
        self.vout = self.vMax * math.sin()



while True: print(time.perf_counter_ns())