from __future__ import annotations

from .hf import HFEngine
from .llamacpp import LlamaCppEngine
from .ollama import OllamaEngine
from .vllm import VLLMEngine


def create_engine(engine: str, model: str):
    if engine == "vllm":
        return VLLMEngine(model)

    if engine == "ollama":
        return OllamaEngine(model)

    if engine == "hf":
        return HFEngine(model)

    if engine == "llamacpp":
        return LlamaCppEngine(model)

    raise ValueError(f"Unknown engine: {engine}")
