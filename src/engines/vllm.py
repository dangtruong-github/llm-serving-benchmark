from __future__ import annotations

import os
import subprocess
import time

from dotenv import load_dotenv
from openai import AsyncOpenAI
import urllib
import asyncio

from src.client.models import (
    BenchmarkResult,
    GenerationRequest,
    GenerationResponse,
    RequestMetrics,
)
from src.workload.loader import (
    Request
)
from .base import BaseEngine

load_dotenv()


class VLLMEngine(BaseEngine):
    def __init__(
        self,
        model: str,
        host: str = "127.0.0.1",
        port: int = 8000,
    ):
        super().__init__(model)

        self.host = host
        self.port = port

        self.process: subprocess.Popen | None = None
        self.log_file = None
        self.client: AsyncOpenAI | None = None

        self.hf_token = os.getenv("HF_TOKEN")

    @property
    def endpoint(self) -> str:
        return f"http://{self.host}:{self.port}/v1"

    def start(self) -> None:
        cmd = [
            "vllm",
            "serve",
            self.model,
            "--host",
            self.host,
            "--port",
            str(self.port),
            "--max-model-len",
            "32768",
            "--gpu-memory-utilization",
            "0.97",
            "--enable-prefix-caching"
        ]

        print("Launching:", " ".join(cmd))

        self.log_file = open("vllm.log", "w", buffering=1)

        self.process = subprocess.Popen(
            cmd,
            stdout=self.log_file,
            stderr=subprocess.STDOUT,
            text=True,
        )

        time.sleep(5)

        self.client = AsyncOpenAI(
            base_url=self.endpoint,
            api_key="EMPTY",
        )

    def stop(self) -> None:
        if self.process is not None:
            self.process.terminate()
            self.process.wait()

        if self.log_file is not None:
            self.log_file.close()

    async def _wait_until_ready(
        self,
        timeout: float = 300.0,
        interval: float = 1.0,
    ) -> None:
        """
        Wait until vLLM OpenAI server is ready.
        """

        start = time.perf_counter()

        url = f"{self.endpoint}/models"

        while True:
            # Check timeout
            if time.perf_counter() - start > timeout:
                raise TimeoutError(
                    f"vLLM server did not become ready after {timeout}s"
                )

            # Check if process died
            if self.process is not None:
                ret = self.process.poll()
                if ret is not None:
                    raise RuntimeError(
                        f"vLLM process exited early with code {ret}"
                    )

            try:
                with urllib.request.urlopen(
                    url,
                    timeout=2,
                ) as response:
                    if response.status == 200:
                        return

            except (urllib.error.URLError, TimeoutError):
                pass

            await asyncio.sleep(interval)

    async def _stream_generate(
        self,
        request: Request,
    ) -> tuple[str, int, int, str | None, float]:

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=request.body["messages"],
                max_tokens=1024,
                temperature=1.0,
                top_p=0.6,
                stream=True,
                stream_options={"include_usage": True},
            )

            pieces = []

            first_token_time = None
            finish_reason = None

            prompt_tokens = 0
            completion_tokens = 0

            async for chunk in stream:
                now = time.perf_counter()

                if chunk.usage:
                    prompt_tokens = chunk.usage.prompt_tokens
                    completion_tokens = chunk.usage.completion_tokens

                if not chunk.choices:
                    continue

                choice = chunk.choices[0]

                if choice.delta.content:
                    if first_token_time is None:
                        first_token_time = now

                    pieces.append(choice.delta.content)

                if choice.finish_reason:
                    finish_reason = choice.finish_reason

            if first_token_time is None:
                first_token_time = time.perf_counter()

            return (
                "".join(pieces),
                prompt_tokens,
                completion_tokens,
                finish_reason,
                first_token_time,
            )

        except Exception as e:
            import traceback

            print("=" * 80)
            print("ASYNC ERROR")
            print(type(e).__name__)
            print(str(e))

            if hasattr(e, "body"):
                print("BODY:")
                print(e.body)

            traceback.print_exc()
            print("=" * 80)

            raise

    async def generate(
        self,
        request: GenerationRequest,
    ) -> BenchmarkResult:
        if self.process is None:
            raise RuntimeError("vLLM process not started.")

        await self._wait_until_ready()

        if self.client is None:
            raise RuntimeError("Engine has not been started.")

        submit_time = time.perf_counter()

        (
            text,
            prompt_tokens,
            completion_tokens,
            finish_reason,
            first_token_time,
        ) = await self._stream_generate(request)

        finish_time = time.perf_counter()

        ttft = first_token_time - submit_time
        latency = finish_time - submit_time

        generation_time = finish_time - first_token_time

        tpot = (
            generation_time / max(completion_tokens - 1, 1)
            if completion_tokens > 1
            else 0.0
        )

        print(f"Request {request.request_id} finished", flush=True)
        return BenchmarkResult(
            request_id=request.request_id,
            response=GenerationResponse(
                request_id=request.request_id,
                text=text,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                finish_reason=finish_reason,
            ),
            metrics=RequestMetrics(
                submit_time=submit_time,
                start_time=submit_time,
                first_token_time=first_token_time,
                finish_time=finish_time,
                queue_time=0.0,
                ttft=ttft,
                latency=latency,
                tpot=tpot,
            ),
        )
