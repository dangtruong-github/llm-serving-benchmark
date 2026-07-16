from __future__ import annotations

from abc import ABC, abstractmethod


class BaseMonitor(ABC):
    @abstractmethod
    def start(self) -> None:
        ...

    @abstractmethod
    def stop(self) -> None:
        ...

    @abstractmethod
    def results(self):
        ...