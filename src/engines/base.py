from __future__ import annotations

from abc import ABC, abstractmethod


class BaseEngine(ABC):
    """Abstract serving engine."""

    def __init__(self, model: str):
        self.model = model

    @abstractmethod
    def start(self) -> None:
        """Start the inference server."""
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        """Stop the inference server."""
        raise NotImplementedError

    @property
    @abstractmethod
    def endpoint(self) -> str:
        """HTTP endpoint of the server."""
        raise NotImplementedError
