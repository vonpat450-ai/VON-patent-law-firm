"""One-off, operator-triggered Gemini publication outside the daily queue.

This is deliberately separate from the scheduled one-column-per-day pipeline.
It permits one additional live test column per KST date and is idempotent.
"""

from __future__ import annotations

import argparse
from datetime import date
import os
from pathlib import Path
import time

from build_column import read_article
from column_automation import DIST, draft_one, fetch_source, recent_articles, topic_order
from generate_sitemap import main as build_sitemap
from make_thumbnail import create_thumbnail
from publish_daily_column import build_columns, now_kst, serialize, site_visible


def manual_articles(day: date) -> list[Path]:
    return sorted((DIST / "articles").glob(f"daily-{day.isoformat()}-manual-*.md"))


def prepare(day: date, *, api_key: str | None = None, fetcher=fetch_source,
            drafter=draft_one) -> Path:
    existing = manual_articles(day)
    if len(existing) > 1:
        raise RuntimeError("More than one manual column exists for this date")
    if existing:
        print(f"Manual column already prepared: {existing[0].name}")
        return existing[0]

    api_key = api_key if api_key is not None else os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing")
    recent = recent_articles(day)
    errors = []
    for topic in topic_order(day, recent):
        try:
            source = fetcher(topic["source"])
            article = drafter(day, topic, source, recent, api_key)
            if any(path.stem.endswith("-" + article["slug"])
                   for path in (DIST / "articles").glob("*.md")):
                raise ValueError("Generated slug is already published")
            path = DIST / "articles" / f"daily-{day.isoformat()}-manual-{article['slug']}.md"
            thumbnail = create_thumbnail(path.stem, article["title"], article["category"], article["summary"])
            path.write_text(serialize(day.isoformat(), {
                "topic_key": topic["key"], "source": source, "article": article,
            }, thumbnail), encoding="utf-8")
            read_article(path)
            build_columns()
            build_sitemap()
            print(f"Gemini generated and validated manual column: {path.name}")
            return path
        except (RuntimeError, ValueError, OSError) as exc:
            errors.append(f"{topic['key']}: {type(exc).__name__}: {exc}")
    raise RuntimeError("No new column passed source and claim verification; " + "; ".join(errors[:3]))


def verify(day: date, *, wait_seconds: int = 540, visibility=site_visible) -> Path:
    paths = manual_articles(day)
    if len(paths) != 1:
        raise RuntimeError("Expected exactly one manual column for this date")
    path = paths[0]
    metadata, lines = read_article(path)
    title = lines[0][2:].strip()
    deadline = time.monotonic() + wait_seconds
    while True:
        if visibility(path, title, metadata.get("thumbnail", "")):
            print(f"PUBLICATION VERIFIED: https://vonpatglobalpt.net/column-{path.stem}")
            return path
        if time.monotonic() >= deadline:
            raise RuntimeError("GitHub content exists but the public site has not shown the column")
        time.sleep(min(20, max(1, deadline - time.monotonic())))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "verify"))
    parser.add_argument("--wait-seconds", type=int, default=540)
    args = parser.parse_args()
    day = now_kst().date()
    if args.command == "prepare":
        prepare(day)
    else:
        verify(day, wait_seconds=args.wait_seconds)


if __name__ == "__main__":
    main()
