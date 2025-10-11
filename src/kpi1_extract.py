"""KPI1: Extract core listing attributes from Yahoo Auctions."""
from __future__ import annotations

from typing import Dict, List

from bs4 import Tag

from .helpers import BeautifulSoup, FetchError, clean_text, fetch_html


def _extract_title(soup: BeautifulSoup) -> str:
    title = soup.find("h1")
    if not title:
        title = soup.find("title")
    return clean_text(title.get_text() if title else None)


def _extract_price(soup: BeautifulSoup) -> str:
    candidates = [
        {"name": "span", "attrs": {"itemprop": "price"}},
        {"name": "span", "attrs": {"class": lambda c: c and "Price" in c}},
        {"name": "div", "attrs": {"class": lambda c: c and "Price" in c}},
    ]
    for query in candidates:
        node = soup.find(query["name"], query.get("attrs"))
        if node:
            return clean_text(node.get_text())
    return "不明"


def _extract_shipping(soup: BeautifulSoup) -> str:
    labels = ["送料", "Shipping"]
    for label in labels:
        cell = soup.find(lambda tag: isinstance(tag, Tag) and tag.get_text(strip=True) == label)
        if cell and cell.next_sibling:
            return clean_text(getattr(cell.next_sibling, "get_text", lambda **_: str(cell.next_sibling))())
    candidates = soup.select(".ProductDetail__shipping, .Shipping__value")
    for node in candidates:
        text = clean_text(node.get_text())
        if text != "不明":
            return text
    return "不明"


def _extract_description(soup: BeautifulSoup) -> str:
    description_candidates = [
        "#ProductExplanation",
        "#ProductDescription",
        ".ProductExplanation",
        "section[itemprop='description']",
        "div[class*='Description']",
    ]
    for selector in description_candidates:
        node = soup.select_one(selector)
        if node:
            return node.decode_contents()
    return "不明"


def _extract_photos(soup: BeautifulSoup) -> List[str]:
    photos: List[str] = []
    gallery_selectors = [
        "#ProductPhoto",
        "#ProductImage",
        ".ProductImage",
        "div[class*='Image']",
    ]
    for selector in gallery_selectors:
        container = soup.select_one(selector)
        if not container:
            continue
        for img in container.find_all("img"):
            src = img.get("src") or img.get("data-src") or img.get("data-lazy")
            if not src:
                continue
            photos.append(_ensure_absolute_url(src, soup))
        if photos:
            break

    if not photos:
        for img in soup.find_all("img"):
            src = img.get("src")
            if src:
                photos.append(_ensure_absolute_url(src, soup))
            if len(photos) >= 3:
                break
    return photos


def _ensure_absolute_url(src: str, soup: BeautifulSoup) -> str:
    if src.startswith("http"):
        return src
    base_tag = soup.find("base")
    base_url = base_tag["href"] if base_tag and base_tag.has_attr("href") else ""
    if base_url and not base_url.endswith("/"):
        base_url += "/"
    return f"{base_url}{src.lstrip('./')}" if base_url else src


def extract_listing(url: str) -> Dict[str, object]:
    """Extract title, price, shipping, description and photos from *url*."""

    try:
        soup = fetch_html(url)
    except FetchError:
        return {
            "title": "不明",
            "price": "不明",
            "shipping": "不明",
            "photos": [],
            "description_html": "不明",
        }

    return {
        "title": _extract_title(soup),
        "price": _extract_price(soup),
        "shipping": _extract_shipping(soup),
        "photos": _extract_photos(soup),
        "description_html": _extract_description(soup),
    }


__all__ = ["extract_listing"]
