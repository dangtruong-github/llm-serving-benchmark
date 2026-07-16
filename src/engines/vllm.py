from __future__ import annotations

import subprocess
import time
import os
from dotenv import load_dotenv

from .base import BaseEngine

# Load environment variables from .env file
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
        # Retrieve token from environment variables
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
        ]

        print("Launching:", " ".join(cmd))

        self.process = subprocess.Popen(cmd)

        # later we'll replace with health checking
        time.sleep(5)

    def stop(self) -> None:
        if self.process is not None:
            self.process.terminate()
            self.process.wait()
