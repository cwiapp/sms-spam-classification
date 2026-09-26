"""A small, explainable SMS screening prototype for phase 1."""

from .rules import Classification, classify_sms

__all__ = ["Classification", "classify_sms"]
