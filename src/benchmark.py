#!/usr/bin/env python3
"""
benchmark.py

Main entry point for the RTX4050 LLM Serving Benchmark.

Example:
    python src/benchmark.py \
        --engine vllm \
        --workload replay \
        --trace data/traces/requests.jsonl
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path
import asyncio

from src.engines import create_engine
from src.workload import (
    ReplayWorkload,
    BurstWorkload,
    PoissonWorkload,
)
from src.monitor import GPUMonitor


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="RTX4050 LLM Serving Benchmark"
    )

    parser.add_argument(
        "--engine",
        required=True,
        choices=["hf", "vllm", "ollama", "llamacpp"],
        help="Serving backend",
    )

    parser.add_argument(
        "--model",
        required=True,
        choices=[
            "Qwen/Qwen3.5-0.8B"
        ],
        help="Model to benchmark",
    )

    parser.add_argument(
        "--workload",
        required=True,
        choices=["replay", "burst", "poisson"],
        help="Workload type",
    )

    parser.add_argument(
        "--trace",
        type=Path,
        default=None,
        help="Path to JSONL trace (required for replay workload)",
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Maximum concurrent requests",
    )

    parser.add_argument(
        "--rate",
        type=float,
        default=1.0,
        help="Arrival rate (requests/sec) for Poisson workload",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/results"),
        help="Output directory",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("=" * 60)
    print("RTX4050 LLM Serving Benchmark")
    print("=" * 60)

    print(f"Engine      : {args.engine}")
    print(f"Workload    : {args.workload}")
    print(f"Concurrency : {args.concurrency}")

    if args.trace:
        print(f"Trace       : {args.trace}")

    if args.workload == "poisson":
        print(f"Rate        : {args.rate:.2f} req/s")

    print()

    # --------------------------------------------------
    # Create serving engine
    # --------------------------------------------------

    print("[1/5] Initializing serving engine...")

    engine = create_engine(args.engine, args.model)
    engine.start()

    time.sleep(0.5)

    # --------------------------------------------------
    # Create workload
    # --------------------------------------------------
        
    print("[2/5] Loading workload...")

    if args.trace is None:
        raise ValueError(
            "--trace must be provided for replay, burst, and poisson workloads."
        )

    if not args.trace.exists():
        raise FileNotFoundError(args.trace)

    if args.workload == "replay":
        workload = ReplayWorkload(args.trace)

    elif args.workload == "burst":
        workload = BurstWorkload(args.trace)

    elif args.workload == "poisson":
        workload = PoissonWorkload(
            args.trace,
            rate=args.rate,
        )

    else:
        raise ValueError(f"Unknown workload: {args.workload}")

    print(f"Loaded {len(workload)} requests")

    time.sleep(0.5)

    # --------------------------------------------------
    # Start monitoring
    # --------------------------------------------------

    print("[3/5] Starting monitor...")

    monitor = GPUMonitor(interval=0.5)
    monitor.start()

    time.sleep(0.5)

    # --------------------------------------------------
    # Run benchmark
    # --------------------------------------------------

    print("[4/5] Running benchmark...")

    start = time.perf_counter()
    print("[4/5] Running benchmark...")

    async def run_benchmark():
        semaphore = asyncio.Semaphore(args.concurrency)
        tasks = []

        async def submit(request):
            async with semaphore:
                return await engine.generate(request)

        benchmark_start = time.perf_counter()

        for request in workload:
            # workload specifies arrival time in seconds\
            elapsed_time = (time.perf_counter() - benchmark_start) * 1000
            delay = request.timestamp_ms - elapsed_time

            if delay > 0:
                await asyncio.sleep(delay / 1000)

            tasks.append(asyncio.create_task(submit(request)))

        return await asyncio.gather(*tasks)

    start = time.perf_counter()

    results = asyncio.run(run_benchmark())

    elapsed = time.perf_counter() - start

    # --------------------------------------------------
    # Save results
    # --------------------------------------------------

    print("[5/5] Saving results...")

    args.output.mkdir(parents=True, exist_ok=True)

    # TODO:
    #
    # save_results(results)

    print()
    print("=" * 60)
    print("Benchmark completed")
    print("=" * 60)
    print(f"Elapsed time : {elapsed:.2f} s")
    print(f"Results dir  : {args.output}")


if __name__ == "__main__":
    main()
