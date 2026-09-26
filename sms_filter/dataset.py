"""Validated loading, grouped splitting and baseline metrics for phase 2."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Iterable
import hashlib
import math
import random
import re
import unicodedata
import zipfile

from .rules import classify_sms


EXPECTED_SHA256 = "1587ea43e58e82b14ff1f5425c88e17f8496bfcdb67a583dbff9eefaf9963ce3"
SOURCE_URL = "https://archive.ics.uci.edu/static/public/228/sms%2Bspam%2Bcollection.zip"
SEED = 42
RATIOS = (0.70, 0.15, 0.15)


@dataclass(frozen=True)
class Message:
    row_id: int  # One-based source line number.
    label: str
    text: str


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_uci_zip(path: Path, *, verify_hash: bool = True) -> list[Message]:
    if verify_hash and sha256(path) != EXPECTED_SHA256:
        raise ValueError("UCI ZIP checksum differs from the pinned phase-2 snapshot")
    with zipfile.ZipFile(path) as archive:
        raw = archive.read("SMSSpamCollection")
    lines = raw.decode("utf-8").splitlines()
    rows = []
    for row_id, line in enumerate(lines, start=1):
        if "\t" not in line:
            raise ValueError(f"line {row_id}: missing label separator")
        label, text = line.split("\t", 1)
        if label not in {"spam", "ham"}:
            raise ValueError(f"line {row_id}: unknown label {label!r}")
        if not text.strip():
            raise ValueError(f"line {row_id}: empty message")
        rows.append(Message(row_id=row_id, label=label, text=text))
    if not rows:
        raise ValueError("empty dataset")
    return rows


def group_key(text: str) -> str:
    """Case- and whitespace-insensitive key for exact text duplication."""
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def _group_rows(rows: Iterable[Message]) -> dict[str, list[Message]]:
    groups: dict[str, list[Message]] = defaultdict(list)
    for row in rows:
        groups[group_key(row.text)].append(row)
    for key, members in groups.items():
        if len({row.label for row in members}) > 1:
            raise ValueError(f"conflicting labels for group hash {hashlib.sha256(key.encode()).hexdigest()[:12]}")
    return groups


def split_groups(rows: list[Message], *, seed: int = SEED) -> dict[str, list[int]]:
    """Deterministic 70/15/15, stratified by label at normalized-text group level."""
    if len({row.row_id for row in rows}) != len(rows):
        raise ValueError("source row IDs must be unique")
    groups = _group_rows(rows)
    by_label: dict[str, list[str]] = defaultdict(list)
    for key, members in groups.items():
        by_label[members[0].label].append(key)

    rng = random.Random(seed)
    assignment: dict[str, str] = {}
    for label in sorted(by_label):
        keys = sorted(by_label[label])
        rng.shuffle(keys)
        n_train = round(len(keys) * RATIOS[0])
        n_val = round(len(keys) * RATIOS[1])
        for key in keys[:n_train]:
            assignment[key] = "train"
        for key in keys[n_train:n_train + n_val]:
            assignment[key] = "validation"
        for key in keys[n_train + n_val:]:
            assignment[key] = "test"

    result = {name: [] for name in ("train", "validation", "test")}
    for row in rows:
        result[assignment[group_key(row.text)]].append(row.row_id)
    all_ids = [row_id for ids in result.values() for row_id in ids]
    if set(all_ids) != {r.row_id for r in rows}:
        raise AssertionError("split does not cover each source row")
    if len(all_ids) != len(set(all_ids)):
        raise AssertionError("split contains duplicate source rows")
    return result


def percentile(values: list[int], fraction: float) -> int:
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * fraction)]


def describe(rows: list[Message], splits: dict[str, list[int]]) -> dict:
    groups = _group_rows(rows)
    labels = Counter(row.label for row in rows)
    lengths = {label: [len(row.text) for row in rows if row.label == label] for label in ("ham", "spam")}
    url_pattern = re.compile(r"(?:https?://|www\.)", flags=re.IGNORECASE)
    by_id = {row.row_id: row for row in rows}
    return {
        "source_rows": len(rows),
        "label_counts": dict(labels),
        "label_fraction_spam": labels["spam"] / len(rows),
        "unique_normalized_texts": len(groups),
        "duplicate_rows": len(rows) - len(groups),
        "conflicting_label_groups": 0,
        "missing_text_or_label": 0,
        "length_characters": {
            label: {"median": median(values), "p90": percentile(values, .90), "max": max(values)}
            for label, values in lengths.items()
        },
        "url_count": {label: sum(row.label == label and bool(url_pattern.search(row.text)) for row in rows)
                      for label in ("ham", "spam")},
        "han_character_rows": sum(any("\u3400" <= ch <= "\u9fff" for ch in row.text) for row in rows),
        "splits": {
            name: {"rows": len(ids), "ham": sum(by_id[i].label == "ham" for i in ids),
                   "spam": sum(by_id[i].label == "spam" for i in ids),
                   "unique_groups": len({group_key(by_id[i].text) for i in ids})}
            for name, ids in splits.items()
        },
    }


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> list[float] | None:
    if total == 0:
        return None
    p = successes / total
    z2 = z * z
    center = (p + z2 / (2 * total)) / (1 + z2 / total)
    half = z * math.sqrt(p * (1 - p) / total + z2 / (4 * total * total)) / (1 + z2 / total)
    return [max(0.0, center - half), min(1.0, center + half)]


def evaluate_rules(rows: list[Message], row_ids: list[int]) -> dict:
    """Evaluate fixed phase-1 rules on one split, recording unsupported inputs."""
    by_id = {row.row_id: row for row in rows}
    counts = Counter()
    abstentions = Counter()
    errors = []
    for row_id in row_ids:
        row = by_id[row_id]
        try:
            prediction = classify_sms(row.text).label
        except (TypeError, ValueError):
            abstentions[row.label] += 1
            continue
        kind = (row.label, prediction)
        counts[kind] += 1
        if row.label != prediction:
            errors.append({"row_id": row_id, "true": row.label, "predicted": prediction})
    tp = counts[("spam", "spam")]
    fn = counts[("spam", "ham")]
    fp = counts[("ham", "spam")]
    tn = counts[("ham", "ham")]
    covered = tp + fn + fp + tn
    return {
        "evaluated_split": "validation",
        "threshold": 3,
        "total": len(row_ids),
        "covered": covered,
        "coverage": covered / len(row_ids),
        "abstentions": dict(abstentions),
        "confusion": {"tp": tp, "fn": fn, "fp": fp, "tn": tn},
        "spam_recall": tp / (tp + fn) if tp + fn else None,
        "spam_recall_95pct_wilson": wilson_interval(tp, tp + fn),
        "ham_false_positive_rate": fp / (fp + tn) if fp + tn else None,
        "ham_fpr_95pct_wilson": wilson_interval(fp, fp + tn),
        "spam_precision": tp / (tp + fp) if tp + fp else None,
        "accuracy_on_covered": (tp + tn) / covered if covered else None,
        "error_rows": errors,
    }
