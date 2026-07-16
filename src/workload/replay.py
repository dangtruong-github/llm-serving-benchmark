from __future__ import annotations

from .base import BaseWorkload


class ReplayWorkload(BaseWorkload):
    """Replay requests using original timestamps."""

    def _prepare(self) -> None:
        # Nothing to modify.
        pass
