from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Request:
    request_id: int
    timestamp_ms: int
    body: dict


def load_jsonl(path: str | Path) -> list[Request]:
    path = Path(path)

    requests = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            obj = json.loads(line)

            requests.append(
                Request(
                    request_id=obj.get("request_id", 0),
                    timestamp_ms=obj.get("timestamp_ms", 0),
                    body=obj["body"],
                )
            )

    return requests