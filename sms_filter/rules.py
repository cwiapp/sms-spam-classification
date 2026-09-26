"""Deterministic English SMS screening rules.

The score is a rule score, not a calibrated probability. A positive result is
only a suggestion for human review; this module never deletes a message.
"""

from dataclasses import dataclass
import re
import unicodedata


MAX_CHARS = 1000
SPAM_THRESHOLD = 3


@dataclass(frozen=True)
class Classification:
    label: str
    score: int
    signals: tuple[str, ...]


_RULES: tuple[tuple[str, re.Pattern[str], int], ...] = (
    ("prize language", re.compile(r"\b(?:win|won|winner|prize|reward)\b"), 2),
    ("claim request", re.compile(r"\b(?:claim|redeem)\b"), 1),
    ("free/cash/bonus", re.compile(r"\b(?:free|cash|bonus)\b"), 1),
    ("urgency", re.compile(r"\b(?:urgent|act now|limited time)\b"), 2),
    ("call now", re.compile(r"\bcall\s+now\b"), 1),
    ("web link", re.compile(r"(?:https?://|www\.)\S+"), 1),
)


def _normalize(message: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", message).casefold().split())


def classify_sms(message: str) -> Classification:
    """Classify one English SMS as ``spam`` or ``ham``.

    Raises TypeError for non-string input and ValueError for unsupported text.
    The length limit is checked before normalization to bound processing cost.
    """
    if not isinstance(message, str):
        raise TypeError("message must be a string")
    if len(message) > MAX_CHARS:
        raise ValueError(f"message exceeds {MAX_CHARS} characters")

    normalized = _normalize(message)
    if not normalized:
        raise ValueError("message must not be blank")
    if re.search(r"[\u3400-\u9fff]", normalized):
        raise ValueError("this phase-1 prototype does not support Chinese text")
    if not re.search(r"[a-z]", normalized):
        raise ValueError("this phase-1 prototype requires English text")

    matched = []
    score = 0
    for name, pattern, weight in _RULES:
        if pattern.search(normalized):
            matched.append(name)
            score += weight
    signals = tuple(matched)
    label = "spam" if score >= SPAM_THRESHOLD else "ham"
    return Classification(label=label, score=score, signals=signals)
