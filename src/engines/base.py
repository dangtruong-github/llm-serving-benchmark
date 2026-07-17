from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class RequestResult:
    request_id: int

    prompt_tokens: int
    completion_tokens: int

    submit_time: float
    start_time: float
    first_token_time: float
    finish_time: float

    ttft: float
    latency: float
    tpot: float

    output_text: str


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

    @abstractmethod
    async def generate(self, request) -> RequestResult:
        """Generation"""
        raise NotImplementedError
