from __future__ import annotations

import random
from pathlib import Path

from .base import BaseWorkload


class PoissonWorkload(BaseWorkload):
    """
    Generate arrivals from a Poisson process.

    rate:
        Average requests per second.
    """

    def __init__(
        self,
        trace: str | Path,
        rate: float,
        seed: int | None = 42,
    ):
        self.rate = rate

        if seed is not None:
            random.seed(seed)

        super().__init__(trace)

    def _prepare(self) -> None:
        current_ms = 0.0

        for req in self.requests:
            interval = random.expovariate(self.rate)
            current_ms += interval * 1000.0
            req.timestamp_ms = int(current_ms)
