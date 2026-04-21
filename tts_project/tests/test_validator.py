"""Unit tests for text validation and cleanup."""

from __future__ import annotations

import pytest

from validator import MAX_TEXT_LENGTH, validate_text


def test_empty_string_raises_value_error() -> None:
    """Empty input should not be accepted."""
    with pytest.raises(ValueError):
        validate_text("")


def test_whitespace_only_string_raises_value_error() -> None:
    """Whitespace-only input should not be accepted."""
    with pytest.raises(ValueError):
        validate_text("   \n\t   ")


def test_special_characters_are_stripped_correctly() -> None:
    """Unsupported symbols, emojis, and null bytes should be removed."""
    assert validate_text("Hello 😊\x00 world!!!") == "Hello world!!!"


def test_normal_text_passes_through_cleaned() -> None:
    """Normal text should only receive leading/trailing whitespace cleanup."""
    assert validate_text("  Hello, world!  ") == "Hello, world!"


def test_text_over_5000_chars_gets_truncated() -> None:
    """Very long text should be truncated with a warning."""
    long_text = "a" * (MAX_TEXT_LENGTH + 100)

    with pytest.warns(RuntimeWarning):
        cleaned = validate_text(long_text)

    assert len(cleaned) == MAX_TEXT_LENGTH
    assert cleaned == "a" * MAX_TEXT_LENGTH
