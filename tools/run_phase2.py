"""Rebuild phase-2 data summary, split manifest and validation baseline."""

from pathlib import Path
import json
import re

from sms_filter.rules import classify_sms

from sms_filter.dataset import (
    EXPECTED_SHA256, RATIOS, SEED, SOURCE_URL, describe, evaluate_rules,
    group_key, load_uci_zip, split_groups,
)


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "sms_spam_collection_uci.zip"
OUT = ROOT / "artifacts"
OUT.mkdir(exist_ok=True)

rows = load_uci_zip(RAW)
splits = split_groups(rows)
id_to_key = {row.row_id: group_key(row.text) for row in rows}
key_sets = {name: {id_to_key[row_id] for row_id in ids} for name, ids in splits.items()}
for left, right in (("train", "validation"), ("train", "test"), ("validation", "test")):
    if key_sets[left] & key_sets[right]:
        raise AssertionError(f"normalized text leakage between {left} and {right}")

summary = describe(rows, splits)
baseline = evaluate_rules(rows, splits["validation"])
errors = baseline.pop("error_rows")
summary["source"] = {"url": SOURCE_URL, "sha256": EXPECTED_SHA256,
                     "dataset_page": "https://archive.ics.uci.edu/dataset/228/sms+spam+collection",
                     "license": "CC BY 4.0"}
summary["split_policy"] = {"seed": SEED, "ratios": RATIOS,
                           "method": "stratify by label at normalized-text group level"}
summary["baseline_validation"] = baseline
summary["validation_error_ids"] = errors

by_id = {row.row_id: row for row in rows}
validation_rows = [by_id[row_id] for row_id in splits["validation"]]
representatives = {}
for row in validation_rows:
    representatives.setdefault(group_key(row.text), row.row_id)
unique_baseline = evaluate_rules(rows, list(representatives.values()))
unique_baseline.pop("error_rows")
summary["baseline_validation_unique_text"] = unique_baseline
score_histogram = {"ham": {}, "spam": {}}
for row in validation_rows:
    try:
        score = classify_sms(row.text).score
    except (TypeError, ValueError):
        continue
    score_histogram[row.label][str(score)] = score_histogram[row.label].get(str(score), 0) + 1
false_negatives = [by_id[item["row_id"]] for item in errors if item["true"] == "spam"]
summary["validation_diagnostics"] = {
    "score_histogram_by_true_label": score_histogram,
    "false_negatives_with_explicit_url": sum(bool(re.search(r"(?:https?://|www\.)", r.text, re.I))
                                              for r in false_negatives),
    "false_negatives_with_digit": sum(any(ch.isdigit() for ch in r.text) for r in false_negatives),
    "all_ham_reference_accuracy": sum(r.label == "ham" for r in validation_rows) / len(validation_rows),
}

manifest = {"source_sha256": EXPECTED_SHA256, "seed": SEED, "splits": splits}
for name, content in (("phase2_summary.json", summary), ("split_manifest.json", manifest)):
    (OUT / name).write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"rows": summary["source_rows"], "labels": summary["label_counts"],
                  "duplicate_rows": summary["duplicate_rows"], "splits": summary["splits"],
                  "validation_baseline": baseline}, ensure_ascii=False, indent=2))
