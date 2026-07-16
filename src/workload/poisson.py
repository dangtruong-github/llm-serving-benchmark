from __future__ import annotations

import random

from .loader import load_jsonl


class PoissonWorkload:

    def __init__(self, trace_path, rate: float):
        self.requests = load_jsonl(trace_path)
        self.rate = rate

    def __iter__(self):
        for req in self.requests:
            delay = random.expovariate(self.rate)
            yield delay, req
