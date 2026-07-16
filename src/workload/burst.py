from __future__ import annotations

from .loader import load_jsonl


class BurstWorkload:

    def __init__(self, trace_path):
        self.requests = load_jsonl(trace_path)

    def __iter__(self):
        for req in self.requests:
            yield 0.0, req
