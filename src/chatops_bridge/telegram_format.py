"""Helpers to format text for Telegram plain-text messages."""

from __future__ import annotations

import re


def to_plain_text(text: str) -> str:
    """Convert markdown-like content into plain text for Telegram readability."""
    if not text:
        return ""

    out = text
    out = out.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", "\t")

    out = re.sub(r"```(?:\\w+)?\n", "", out)
    out = out.replace("```", "")
    out = re.sub(r"^#{1,6}\\s*", "", out, flags=re.MULTILINE)
    out = re.sub(r"\\*\\*(.*?)\\*\\*", r"\\1", out, flags=re.DOTALL)
    out = re.sub(r"__(.*?)__", r"\\1", out, flags=re.DOTALL)
    out = re.sub(r"`([^`]+)`", r"\\1", out)
    out = re.sub(r"\\[([^\\]]+)\\]\\(([^)]+)\\)", r"\\1 (\\2)", out)
    out = re.sub(r"^>\\s?", "", out, flags=re.MULTILINE)
    out = re.sub(r"^[ \\t]*[-*+]\\s+", "- ", out, flags=re.MULTILINE)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip()


def section(title: str, body: str) -> str:
    """Build a simple titled section for Telegram plain text."""
    clean_body = to_plain_text(body)
    if not clean_body:
        return title
    return f"{title}:\n{clean_body}"


def compact_lines(lines: list[str]) -> str:
    cleaned = [line for line in lines if line is not None and str(line).strip() != ""]
    return "\n".join(cleaned).strip()
