from __future__ import annotations

from .base import BaseEngine


class HFEngine(BaseEngine):
    @property
    def endpoint(self) -> str:
        return ""

    def start(self) -> None:
        print("HF engine initialized.")

    def stop(self) -> None:
        pass
