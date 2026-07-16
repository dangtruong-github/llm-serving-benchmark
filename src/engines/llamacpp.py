from __future__ import annotations

from .base import BaseEngine


class LlamaCppEngine(BaseEngine):
    @property
    def endpoint(self) -> str:
        return "http://127.0.0.1:8080/v1"

    def start(self) -> None:
        print("Launching llama.cpp server...")

    def stop(self) -> None:
        pass
