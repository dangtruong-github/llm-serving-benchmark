from __future__ import annotations

from abc import ABC
from pathlib import Path

from .loader import Request, load_jsonl


class BaseWorkload(ABC):
    """Base class for all workloads."""

    def __init__(self, trace: str | Path):
        self.trace = Path(trace)
        self.requests: list[Request] = load_jsonl(self.trace)

        self._prepare()

    def _prepare(self) -> None:
        """Modify request timestamps if needed."""
        pass

    def __iter__(self):
        return iter(self.requests)

    def __len__(self):
        return len(self.requests)

    def __getitem__(self, idx: int) -> Request:
        return self.requests[idx]
