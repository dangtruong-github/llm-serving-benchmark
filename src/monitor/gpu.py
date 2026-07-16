from __future__ import annotations

import subprocess
import threading
import time

from .base import BaseMonitor


class GPUMonitor(BaseMonitor):
    def __init__(self, interval: float = 0.5):
        self.interval = interval
        self._running = False
        self._thread: threading.Thread | None = None
        self._samples: list[dict] = []

    def start(self) -> None:
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._running = False

        if self._thread is not None:
            self._thread.join()

    def results(self) -> list[dict]:
        return self._samples

    def _run(self) -> None:
        query = ",".join(
            [
                "timestamp",
                "utilization.gpu",
                "utilization.memory",
                "memory.used",
                "memory.total",
                "temperature.gpu",
                "power.draw",
            ]
        )

        while self._running:
            try:
                output = subprocess.check_output(
                    [
                        "nvidia-smi",
                        f"--query-gpu={query}",
                        "--format=csv,noheader,nounits",
                    ],
                    text=True,
                ).strip()

                values = [v.strip() for v in output.split(",")]

                self._samples.append(
                    {
                        "timestamp": values[0],
                        "gpu_util": float(values[1]),
                        "mem_util": float(values[2]),
                        "mem_used_mb": float(values[3]),
                        "mem_total_mb": float(values[4]),
                        "temperature_c": float(values[5]),
                        "power_w": float(values[6]),
                    }
                )

            except Exception:
                pass

            time.sleep(self.interval)
