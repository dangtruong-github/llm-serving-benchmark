from __future__ import annotations

from .base import BaseEngine


class OllamaEngine(BaseEngine):
    @property
    def endpoint(self) -> str:
        return "http://127.0.0.1:11434/v1"

    def start(self) -> None:
        print("Using existing Ollama server.")

    def stop(self) -> None:
        pass
