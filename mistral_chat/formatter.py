"""Response formatting helpers used by the CLI and web app."""

from __future__ import annotations

import re


LIST_PATTERN = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+", re.MULTILINE)
SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+")


def _split_sentences(text: str) -> list[str]:
    """Split prose into sentence-like chunks without losing short fragments."""
    parts = SENTENCE_PATTERN.split(text.strip())
    return [part.strip() for part in parts if part.strip()]


def _as_bullets(items: list[str]) -> str:
    return "\n".join(f"• {item}" for item in items)


def _as_numbered(items: list[str]) -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(items, start=1))


def format_response(text: str, style: str) -> str:
    """Format an assistant response as plain text, bullets, numbers, or auto."""
    normalized_style = (style or "plain").strip().lower()
    clean_text = text.strip()

    if normalized_style == "plain" or not clean_text:
        return text

    if normalized_style == "auto":
        return clean_text if LIST_PATTERN.search(clean_text) else text

    sentences = _split_sentences(clean_text)
    if not sentences:
        return text

    if normalized_style == "bullets":
        return _as_bullets(sentences)

    if normalized_style == "numbered":
        return _as_numbered(sentences)

    return text
