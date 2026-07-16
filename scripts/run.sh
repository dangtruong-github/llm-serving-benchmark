#!/bin/bash

cd /home/truongchd/projects/llm_serving_proj

python -m src.benchmark \
    --engine vllm \
    --model Qwen/Qwen3.5-0.8B \
    --workload replay \
    --trace data/traces/requests.jsonl