"""Evaluation dataset management for golden Q&A pairs."""

import json
from pathlib import Path

from pydantic import BaseModel


class EvalSample(BaseModel):
    """A single evaluation sample with ground truth."""

    query: str
    expected_answer: str
    relevant_context: str
    category: str  # "benefits" or "claims"


class EvalDataset:
    """Loads and manages golden Q&A pairs for evaluation."""

    def __init__(self, samples: list[EvalSample] | None = None):
        self._samples = samples or []

    @classmethod
    def load(cls, path: Path) -> "EvalDataset":
        """Load evaluation samples from a JSON file."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        samples = [EvalSample(**item) for item in data["samples"]]
        return cls(samples)

    @property
    def samples(self) -> list[EvalSample]:
        return list(self._samples)

    def filter_by_category(self, category: str) -> list[EvalSample]:
        return [s for s in self._samples if s.category == category]

    def __len__(self) -> int:
        return len(self._samples)
