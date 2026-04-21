"""Input validation and cleanup helpers for the TTS project."""

from __future__ import annotations

import re
import unicodedata
import warnings


MAX_TEXT_LENGTH = 5000

# Characters that most TTS engines handle consistently across platforms.
_ALLOWED_PUNCTUATION = set(".,!?;:'\"()[]{}-/\\&%+$#@*=_\n\r\t ")
_WHITESPACE_RE = re.compile(r"\s+")
_REPEATED_SPECIAL_RE = re.compile(r"([^\w\s])\1{3,}")


def _is_supported_character(character: str) -> bool:
    """Return True if a character is safe to pass to common TTS engines."""
    if character.isalnum() or character in _ALLOWED_PUNCTUATION:
        return True

    category = unicodedata.category(character)

    # Drop control characters, surrogates, private-use characters, and emojis /
    # pictographic symbols. These commonly cause awkward reads or engine errors.
    if category.startswith(("C", "S")):
        return False

    # Keep letters and marks from non-English scripts where possible, so the
    # validator does not unintentionally erase multilingual input.
    return category.startswith(("L", "M", "N"))


def validate_text(text: str) -> str:
    """Validate and normalize text before speech generation.

    Args:
        text: Raw text supplied by the user.

    Raises:
        TypeError: If ``text`` is not a string.
        ValueError: If ``text`` is empty or only whitespace.

    Returns:
        A cleaned string that is safer for TTS engines.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Text cannot be empty or only whitespace.")

    cleaned = "".join(
        character if _is_supported_character(character) else " "
        for character in cleaned.replace("\x00", " ")
    )

    # Very long punctuation bursts are usually accidental and sound terrible,
    # so shorten them to a readable three-character sequence.
    cleaned = _REPEATED_SPECIAL_RE.sub(lambda match: match.group(1) * 3, cleaned)
    cleaned = _WHITESPACE_RE.sub(" ", cleaned).strip()

    if not cleaned:
        raise ValueError("Text does not contain any supported TTS characters.")

    if len(cleaned) > MAX_TEXT_LENGTH:
        warnings.warn(
            f"Text exceeds {MAX_TEXT_LENGTH} characters and was truncated.",
            RuntimeWarning,
            stacklevel=2,
        )
        cleaned = cleaned[:MAX_TEXT_LENGTH].rstrip()

    return cleaned
