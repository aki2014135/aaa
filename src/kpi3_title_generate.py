"""KPI3: Generate listing titles from structured specifications."""
from __future__ import annotations

from typing import Dict

from .helpers import clean_text


def generate_title(specs: Dict[str, str]) -> Dict[str, str]:
    """Return a JSON-friendly dictionary containing the formatted title."""

    brand = clean_text(specs.get("brand") if isinstance(specs, dict) else None)
    model = clean_text(specs.get("model") if isinstance(specs, dict) else None)
    inch = clean_text(specs.get("inch") if isinstance(specs, dict) else None)
    width = clean_text(specs.get("width") if isinstance(specs, dict) else None)
    holes = clean_text(specs.get("holes") if isinstance(specs, dict) else None)
    pcd = clean_text(specs.get("pcd") if isinstance(specs, dict) else None)
    offset = clean_text(specs.get("offset") if isinstance(specs, dict) else None)

    title_parts = [brand, model]

    if inch != "不明":
        title_parts.append(f"{inch}")
    if width != "不明":
        title_parts.append(f"{width}")
    if holes != "不明":
        title_parts.append(f"{holes}H")
    if pcd != "不明":
        title_parts.append(f"PCD{pcd}")
    if offset != "不明":
        title_parts.append(f"OFFSET{offset}")

    structured_title = " ".join(part for part in title_parts if part and part != "不明")
    structured_title = structured_title or "不明"

    return {"title": structured_title}


__all__ = ["generate_title"]
