"""KPI2: Parse structured specifications from listing content."""
from __future__ import annotations

from typing import Dict, Iterable

from .helpers import clean_text, run_regexes


BRAND_PATTERNS: Iterable[str] = (
    r"(?:メーカー|brand)[:：\s]*([A-Za-z0-9\- ]{2,})",
    r"\b(ENKEI|BBS|RAYS|WORK|WEDS)\b",
)

MODEL_PATTERNS: Iterable[str] = (
    r"(?:モデル|model)[:：\s]*([A-Za-z0-9\- ]{2,})",
    r"\b(TE37|CE28|G25|LM|VS-?XX)\b",
)

INCH_PATTERNS: Iterable[str] = (
    r"(1[4-9]|2[0-4])\s?インチ",
    r"(1[4-9]|2[0-4])\s?inch",
    r"(1[4-9]|2[0-4])\s?\"",
)

WIDTH_PATTERNS: Iterable[str] = (
    r"(\d{1,2}\.\d)J",
    r"(\d{1,2})J",
)

HOLE_PATTERNS: Iterable[str] = (
    r"(\d{1,2})H",
    r"(\d{1,2})穴",
)

PCD_PATTERNS: Iterable[str] = (
    r"PCD[:：\s]*(\d{2,3}\.\d)",
    r"PCD[:：\s]*(\d{2,3})",
    r"(\d{3}\.\d)\s?PCD",
)

OFFSET_PATTERNS: Iterable[str] = (
    r"ET[:：\s]*([+-]?\d{1,2})",
    r"オフセット[:：\s]*([+-]?\d{1,2})",
    r"(?:OFFSET|オフセット)[^\d]*([+-]?\d{1,2})",
)


def _combine_text(title: str, description_html: str) -> str:
    parts = [title or "", description_html or ""]
    return "\n".join(part for part in parts if part)


def parse_specs(data: Dict[str, object]) -> Dict[str, str]:
    """Return wheel specifications from listing data.

    Args:
        data: Dictionary containing at least the listing title, description and photos.
    """

    title = clean_text(data.get("title") if isinstance(data, dict) else None)
    description = clean_text(str(data.get("description_html", "")) if isinstance(data, dict) else None)
    text_blob = _combine_text(title, description)

    brand = run_regexes(text_blob, BRAND_PATTERNS)
    model = run_regexes(text_blob, MODEL_PATTERNS)
    inch = run_regexes(text_blob, INCH_PATTERNS)
    width = run_regexes(text_blob, WIDTH_PATTERNS)
    holes = run_regexes(text_blob, HOLE_PATTERNS)
    pcd = run_regexes(text_blob, PCD_PATTERNS)
    offset = run_regexes(text_blob, OFFSET_PATTERNS)

    return {
        "brand": brand,
        "model": model,
        "inch": inch,
        "width": width,
        "holes": holes,
        "pcd": pcd,
        "offset": offset,
    }


__all__ = ["parse_specs"]
