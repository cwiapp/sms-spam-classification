"""Behavior and boundary tests for the phase-1 prototype."""

import unittest

from sms_filter.rules import MAX_CHARS, classify_sms


class ClassifySmsTests(unittest.TestCase):
    def test_obvious_spam(self):
        self.assertEqual(classify_sms("You won a prize. Claim it now!").label, "spam")

    def test_normal_conversation(self):
        self.assertEqual(classify_sms("Can we meet at the library at 3 pm?").label, "ham")

    def test_case_insensitive(self):
        self.assertEqual(classify_sms("URGENT CASH offer").label, "spam")

    def test_fullwidth_letters_are_normalized(self):
        self.assertEqual(classify_sms("ＷＩＮ a prize, claim it!").label, "spam")

    def test_keyword_inside_longer_word_does_not_match(self):
        self.assertEqual(classify_sms("Winter begins tomorrow.").score, 0)

    def test_free_in_legitimate_message_is_not_enough(self):
        self.assertEqual(classify_sms("Are you free for lunch tomorrow?").label, "ham")

    def test_link_alone_is_not_enough(self):
        self.assertEqual(classify_sms("Please read https://example.org/notes").label, "ham")

    def test_explanations_are_returned(self):
        result = classify_sms("You won a prize. Claim it now!")
        self.assertIn("prize language", result.signals)
        self.assertIn("claim request", result.signals)

    def test_blank_input_is_rejected(self):
        with self.assertRaises(ValueError):
            classify_sms("  \n\t ")

    def test_non_string_input_is_rejected(self):
        with self.assertRaises(TypeError):
            classify_sms(None)  # type: ignore[arg-type]

    def test_overlong_input_is_rejected(self):
        with self.assertRaises(ValueError):
            classify_sms("a" * (MAX_CHARS + 1))

    def test_chinese_text_is_rejected_instead_of_called_ham(self):
        with self.assertRaises(ValueError):
            classify_sms("恭喜中奖")

    def test_numbers_only_are_rejected(self):
        with self.assertRaises(ValueError):
            classify_sms("123456")

    def test_deterministic_output(self):
        message = "Win a bonus prize at www.example.com"
        self.assertEqual(classify_sms(message), classify_sms(message))


if __name__ == "__main__":
    unittest.main()
