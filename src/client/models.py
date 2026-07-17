from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GenerationResponse:
    """
    Raw response returned by the serving engine.
    """

    request_id: int

    text: str

    prompt_tokens: int
    completion_tokens: int

    finish_reason: str | None = None

@dataclass(slots=True)
class RequestMetrics:
    """
    Timing information collected for one request.
    """

    submit_time: float

    start_time: float

    first_token_time: float

    finish_time: float

    queue_time: float

    ttft: float

    latency: float

    tpot: float

@dataclass(slots=True)
class BenchmarkResult:
    """
    Final benchmark record for one request.
    """

    request_id: int

    response: GenerationResponse

    metrics: RequestMetrics

@dataclass
class GenerationRequest:
    request_id: int
    messages: list[dict[str, str]]
    max_tokens: int = 128
    temperature: float = 0.0
    top_p: float = 1.0
