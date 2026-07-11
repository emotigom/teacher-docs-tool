"""Small, transparent similarity heuristic for review only."""
from __future__ import annotations

from difflib import SequenceMatcher


def similarity_percent(text: str, prior_texts: list[str]) -> int:
    if not prior_texts:
        return 0
    return round(max(SequenceMatcher(None, text, other).ratio() for other in prior_texts) * 100)
