"""Provider abstraction reserved for a future approved LLM integration."""
from __future__ import annotations

from abc import ABC, abstractmethod

from schemas import StudentObservation


class RecordProvider(ABC):
    @abstractmethod
    def generate(self, student: StudentObservation) -> str:
        raise NotImplementedError
