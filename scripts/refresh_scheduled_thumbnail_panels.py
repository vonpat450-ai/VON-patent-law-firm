"""Apply the current title panel to prepublished columns using saved photos.

Only scheduled columns dated on or after PANEL_OPACITY_START are touched.
No image service is called, and published thumbnails are never rewritten.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from build_column import read_article
from make_thumbnail import ASSETS, PANEL_OPACITY_START, panel_opacity_for_slug, render_thumbnail, short_label


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "automation" / "queue"
DIST = ROOT / "dist"


def refresh() -> list[str]:
    updated: list[str] = []
    for queue_path in sorted(QUEUE.glob("*.json")):
        item = json.loads(queue_path.read_text(encoding="utf-8"))
        if item.get("status") != "scheduled" or item.get("target_date", "") < PANEL_OPACITY_START.isoformat():
            continue
        relative = item.get("article_path", "")
        article_path = DIST / relative
        if not relative or article_path.parent != DIST / "articles" or not article_path.is_file():
            raise ValueError(f"Unsafe or missing scheduled article: {queue_path.name}")
        metadata, lines = read_article(article_path)
        if metadata["published"] != item["target_date"]:
            raise ValueError(f"Scheduled date mismatch: {queue_path.name}")
        slug = article_path.stem
        raw = ASSETS / f"{slug}-photo.webp"
        thumbnail = ASSETS / f"{slug}-thumb.webp"
        if metadata.get("thumbnail") != f"assets/{thumbnail.name}" or not raw.is_file():
            raise ValueError(f"Scheduled thumbnail or original photo is missing: {slug}")
        article = item["article"]
        label = short_label(lines[0][2:].strip(), metadata["category"], article.get("thumbnail_label", ""))
        with Image.open(raw) as photo:
            render_thumbnail(photo, label, thumbnail, panel_opacity=panel_opacity_for_slug(slug))
        updated.append(slug)
    return updated


if __name__ == "__main__":
    for slug in refresh():
        print(f"Updated scheduled thumbnail: {slug}")
