from __future__ import annotations

from .base import BaseWorkload


class BurstWorkload(BaseWorkload):
    """All requests arrive at time zero."""

    def _prepare(self) -> None:
        for req in self.requests:
            req.timestamp_ms = 0
