from __future__ import annotations

from .loader import load_jsonl


class ReplayWorkload:

    def __init__(self, trace_path):
        self.requests = load_jsonl(trace_path)

    def __iter__(self):
        previous = 0

        for req in self.requests:
            delay = (req.timestamp_ms - previous) / 1000
            previous = req.timestamp_ms

            yield delay, req
