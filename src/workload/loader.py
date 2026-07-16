from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Request:
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
                    timestamp_ms=obj.get("timestamp_ms", 0),
                    body=obj["body"],
                )
            )

    return requests