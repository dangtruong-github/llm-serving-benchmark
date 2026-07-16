#!/bin/bash

cd /home/truongchd/projects/llm_serving_proj

python -m src.benchmark \
    --engine vllm \
    --model qwen2.5-1.5b \
    --workload replay \
    --trace data/traces/requests.jsonl