"""KPI4: Generate HTML description blocks from specs and raw copy."""
from __future__ import annotations

from typing import Dict

from .helpers import clean_text


def generate_description(specs: Dict[str, str], raw_description: str) -> Dict[str, str]:
    """Return HTML content using a standard template."""

    brand = clean_text(specs.get("brand") if isinstance(specs, dict) else None)
    model = clean_text(specs.get("model") if isinstance(specs, dict) else None)
    inch = clean_text(specs.get("inch") if isinstance(specs, dict) else None)
    width = clean_text(specs.get("width") if isinstance(specs, dict) else None)
    holes = clean_text(specs.get("holes") if isinstance(specs, dict) else None)
    pcd = clean_text(specs.get("pcd") if isinstance(specs, dict) else None)
    offset = clean_text(specs.get("offset") if isinstance(specs, dict) else None)
    description = clean_text(raw_description)

    spec_rows = [
        ("ブランド", brand),
        ("モデル", model),
        ("リム径", inch),
        ("リム幅", width),
        ("穴数", holes),
        ("PCD", pcd),
        ("オフセット", offset),
    ]

    spec_html = "".join(
        f"<tr><th>{label}</th><td>{value}</td></tr>" for label, value in spec_rows
    )

    html = f"""
<section class=\"kpi-description\">
  <h2>商品仕様</h2>
  <table class=\"kpi-specs\">
    <tbody>
      {spec_html}
    </tbody>
  </table>
  <h2>商品説明</h2>
  <div class=\"kpi-raw-description\">{description}</div>
</section>
""".strip()

    return {"description_html": html}


__all__ = ["generate_description"]
