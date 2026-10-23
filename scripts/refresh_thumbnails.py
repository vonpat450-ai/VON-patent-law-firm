"""Rebuild existing article thumbnails with the current shared visual rules.

The Magnific key is read only from the workflow environment. A clean original
photo is retained for inexpensive future layout changes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

from build_column import read_article
from make_thumbnail import ASSETS, THUMB_SIZE, create_thumbnail


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "automation" / "thumbnail_backfill_plan.json"


def refresh(*, require_ai: bool) -> int:
    items = json.loads(PLAN.read_text(encoding="utf-8"))["items"]
    changed = 0
    for entry in items:
        article_path = ROOT / entry["article"]
        metadata, lines = read_article(article_path)
        slug = article_path.stem
        title = lines[0][2:].strip()
        target = ROOT / entry["thumbnail"]
        if target.parent != ASSETS or target.name != f"{slug}-thumb.webp":
            raise ValueError(f"Unexpected thumbnail destination for {slug}")

        # This approved Canva image is already a clean subject photo.
        if slug == "daily-2026-10-22-first-steps-for-foreign-patent-protection":
            source = ASSETS / f"{slug}-canva.webp"
            raw = ASSETS / f"{slug}-photo.webp"
            if not raw.is_file():
                with Image.open(source) as image:
                    from PIL import ImageOps
                    ImageOps.fit(image.convert("RGB"), THUMB_SIZE, Image.Resampling.LANCZOS).save(
                        raw, "WEBP", quality=88, method=6)

        path = create_thumbnail(
            slug, title, metadata["category"], metadata.get("list_summary", metadata.get("description", "")),
            label=entry["label"], visual=entry["visual"],
            require_ai=require_ai, reuse_photo=True,
        )
        source_text = article_path.read_text(encoding="utf-8")
        old_value = f"thumbnail: {metadata['thumbnail']}"
        new_value = f"thumbnail: {path}"
        if old_value != new_value:
            article_path.write_text(source_text.replace(old_value, new_value, 1), encoding="utf-8")
        changed += 1
        print(f"Refreshed {slug}")
    return changed


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-ai", action="store_true")
    args = parser.parse_args()
    print(f"Refreshed {refresh(require_ai=args.require_ai)} article thumbnails")
