#!/bin/bash

cd /home/truongchd/projects/llm_serving_proj

python -m src.benchmark \
    --engine vllm \
    --model Qwen/Qwen3.5-0.8B \
    --workload replay \
    --concurrency 20 \
    --trace data/traces/requests.jsonl