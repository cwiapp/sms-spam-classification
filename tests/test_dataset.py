"""Checks for parser, split leakage and interval calculations."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import zipfile

from sms_filter.dataset import Message, group_key, load_uci_zip, split_groups, wilson_interval


class DatasetTests(unittest.TestCase):
    def test_group_key_normalizes_case_width_and_space(self):
        self.assertEqual(group_key("  ＦＲＥＥ   prize "), group_key("free prize"))

    def test_split_keeps_duplicates_together(self):
        rows = [Message(i, "ham" if i < 11 else "spam", f"Message {i}") for i in range(1, 21)]
        rows.append(Message(21, "ham", "  MESSAGE   1 "))
        result = split_groups(rows)
        location = {row_id: name for name, ids in result.items() for row_id in ids}
        self.assertEqual(location[1], location[21])
        self.assertEqual(len(location), len(rows))

    def test_split_is_deterministic(self):
        rows = [Message(i, "ham" if i < 11 else "spam", f"Message {i}") for i in range(1, 21)]
        self.assertEqual(split_groups(rows), split_groups(rows))

    def test_conflicting_duplicate_labels_rejected(self):
        rows = [Message(1, "ham", "Same text"), Message(2, "spam", "same  text")]
        with self.assertRaises(ValueError):
            split_groups(rows)

    def test_parser_rejects_missing_separator(self):
        with TemporaryDirectory() as temp:
            path = Path(temp) / "bad.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("SMSSpamCollection", "ham no tab\n")
            with self.assertRaises(ValueError):
                load_uci_zip(path, verify_hash=False)

    def test_parser_rejects_invalid_label(self):
        with TemporaryDirectory() as temp:
            path = Path(temp) / "bad.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("SMSSpamCollection", "unknown\ttext\n")
            with self.assertRaises(ValueError):
                load_uci_zip(path, verify_hash=False)

    def test_wilson_interval_contains_observed_proportion(self):
        lower, upper = wilson_interval(9, 10)
        self.assertLess(lower, .9)
        self.assertGreater(upper, .9)

    def test_wilson_interval_handles_zero_denominator(self):
        self.assertIsNone(wilson_interval(0, 0))


if __name__ == "__main__":
    unittest.main()
