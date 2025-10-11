"""Common helper utilities for KPI scripts."""
from __future__ import annotations

import json
import time
from typing import Iterable, Optional

import httpx
from bs4 import BeautifulSoup

DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


class FetchError(RuntimeError):
    """Raised when HTML content cannot be fetched."""


def fetch_html(url: str, *, timeout: float = 10.0, retries: int = 3, backoff: float = 1.5) -> BeautifulSoup:
    """Fetch HTML from *url* and return a BeautifulSoup document.

    Args:
        url: The HTTP URL to load.
        timeout: Request timeout in seconds.
        retries: Maximum number of attempts.
        backoff: Multiplicative backoff applied between retries.

    Returns:
        BeautifulSoup: Parsed HTML document.

    Raises:
        FetchError: If the request ultimately fails.
    """

    last_exc: Optional[Exception] = None
    delay = 0.0
    headers = {"User-Agent": DESKTOP_UA}

    for attempt in range(1, retries + 1):
        if delay:
            time.sleep(delay)
        try:
            with httpx.Client(timeout=timeout, headers=headers) as client:
                response = client.get(url, follow_redirects=True)
                response.raise_for_status()
                return BeautifulSoup(response.text, "lxml")
        except Exception as exc:  # pragma: no cover - safety net
            last_exc = exc
            delay = delay * backoff if delay else backoff

    raise FetchError(f"Failed to fetch HTML from {url!r}: {last_exc}")


def clean_text(value: Optional[str]) -> str:
    """Normalize whitespace in *value*.

    Empty or missing values return the literal "不明".
    """

    if not value:
        return "不明"
    return " ".join(value.strip().split()) or "不明"


def run_regexes(text: str, patterns: Iterable[str]) -> str:
    """Run regex *patterns* against *text* and return the first match.

    If no pattern matches, "不明" is returned.
    """

    import re

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = [g for g in match.groups() if g]
            if groups:
                return clean_text(groups[0])
            return clean_text(match.group(0))
    return "不明"


__all__ = [
    "BeautifulSoup",
    "FetchError",
    "clean_text",
    "fetch_html",
    "json",
    "run_regexes",
]
