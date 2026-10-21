"""Prepare verified drafts before 08:00 KST and publish at the scheduled slots.

The queue and state are committed to GitHub so the next Actions runner can
continue after a failed upload or Cloudflare deployment. Never log API keys or
unvalidated model output.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime
from html import escape
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib import parse, request
from zoneinfo import ZoneInfo

from build_column import main as build_columns, read_article
from column_automation import (
    AUTOMATION, BASE_URL, DIST, QUEUE, TOPICS, draft_one, fetch_source,
    recent_articles, source_is_current, topic_order,
)
from generate_sitemap import main as build_sitemap
from make_thumbnail import create_thumbnail


KST = ZoneInfo("Asia/Seoul")
STATE_PATH = AUTOMATION / "state.json"
SLOTS = ("0 8 * * *", "30 8 * * *", "0 9 * * *", "30 9 * * *", "0 10 * * *")


def now_kst() -> datetime:
    return datetime.now(KST)


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_state() -> dict:
    return json.loads(STATE_PATH.read_text(encoding="utf-8")) if STATE_PATH.exists() else {"days": {}}


def queue_items() -> list[tuple[Path, dict]]:
    QUEUE.mkdir(parents=True, exist_ok=True)
    result = [(path, json.loads(path.read_text(encoding="utf-8"))) for path in QUEUE.glob("*.json")]
    return sorted(result, key=lambda pair: (pair[1].get("created_at", ""), pair[0].name))


def slug_path(day: str, slug: str) -> Path:
    return DIST / "articles" / f"daily-{day}-{slug}.md"


def article_for_day(day: str) -> list[Path]:
    result = []
    for path in (DIST / "articles").glob("*.md"):
        metadata, _ = read_article(path)
        if metadata["published"] == day:
            result.append(path)
    return result


def source_label(source: dict) -> str:
    return f"{source['organization']} · {source['title']} · {source['published']}"


def serialize(day: str, item: dict, thumbnail: str) -> str:
    article = item["article"]
    topic = next(topic for topic in TOPICS if topic["key"] == item["topic_key"])
    source = item["source"]
    note = str(article["sources"][0]["verified_excerpt"]).replace("\n", " ").strip()[:220]
    safe = lambda value: str(value).replace("\r", " ").replace("\n", " ").strip()
    takeaway = re.search(r":::takeaway\s*\n(.*?)\n:::", article["body"], re.S)
    if not takeaway:
        raise ValueError("Article is missing its core answer")
    answer = " ".join(line.strip() for line in takeaway.group(1).splitlines() if line.strip())
    return (
        f"---\npublished: {day}\ncategory: {article['category']}\nlayout: guide\n"
        f"tags: {article['category']} · 특허 실무\nhero: assets/pct-column-hero.webp\n"
        f"thumbnail: {thumbnail}\n"
        f"list_summary: {safe(article['summary'])}\n"
        f"description: {safe(article['meta_description'])}\n"
        f"related_url: {topic['related_url']}\nrelated_label: {topic['related_label']}\n"
        f"source_1_label: {safe(source_label(source))}\nsource_1_url: {source['url']}\n"
        f"source_1_note: {safe(note)}\n"
        f"---\n# {safe(article['title'])}\n## {safe(answer)}\n\n{article['body'].strip()}\n"
    )


def prepare(day: date, *, dry_run: bool = False, api_key: str | None = None,
            fetcher=fetch_source, drafter=draft_one) -> list[Path]:
    api_key = api_key if api_key is not None else os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing")
    ready = [(path, item) for path, item in queue_items() if item.get("status") == "ready"]
    target_count = 1 if dry_run else 2
    if len(ready) >= target_count and not dry_run:
        print(f"Verified queue already has {len(ready)} drafts")
        return []
    recent = recent_articles(day)
    created: list[Path] = []
    errors: list[str] = []
    for topic in topic_order(day, recent)[:6]:
        if not dry_run and len(ready) + len(created) >= target_count:
            break
        try:
            source = fetcher(topic["source"])
            article = drafter(day, topic, source, recent, api_key)
            if any(path.stem.endswith("-" + article["slug"]) for path in (DIST / "articles").glob("*.md")):
                raise ValueError("Generated slug is already published")
            if any(item["article"]["slug"] == article["slug"] for _, item in queue_items()):
                raise ValueError("Generated slug is already queued")
            item = {
                "status": "ready", "created_at": now_kst().isoformat(),
                "topic_key": topic["key"], "article": article, "source": source,
                "article_path": "", "target_date": "", "attempt_slots": [], "last_error": "",
            }
            if dry_run:
                print(f"Dry run passed: {article['title']} ({len(article['body'])} characters)")
                return []
            filename = f"{day.isoformat()}-{topic['key']}-{article['slug']}.json"
            path = QUEUE / filename
            write_json(path, item)
            created.append(path)
            recent.append({"title": article["title"], "category": article["category"], "published": day.isoformat()})
            print(f"Prepared verified draft: {path.name}")
        except (RuntimeError, ValueError, OSError) as exc:
            errors.append(f"{topic['key']}: {type(exc).__name__}: {exc}")
    if not created and not ready:
        raise RuntimeError("No draft passed source and claim verification; " + "; ".join(errors[:3]))
    return created


def fetch_public(url: str, opener=request.urlopen) -> str:
    parts = parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname != "vonpatglobalpt.net":
        raise ValueError("Public verification is restricted to the site domain")
    req = request.Request(url, headers={"Cache-Control": "no-cache", "User-Agent": "VONPatentDeploymentCheck/1.0"})
    with opener(req, timeout=20) as response:
        if response.status != 200:
            raise RuntimeError(f"Site returned HTTP {response.status}")
        return response.read(1_000_001).decode("utf-8", errors="replace")


def site_visible(path: Path, title: str, thumbnail: str = "", fetcher=fetch_public) -> bool:
    nonce = str(int(time.time()))
    try:
        article = fetcher(f"{BASE_URL}/column-{path.stem}.html?check={nonce}")
        listing = fetcher(f"{BASE_URL}/articles-data.js?check={nonce}")
        knowledge = fetcher(f"{BASE_URL}/knowledge.html?check={nonce}")
        if f"<h1>{escape(title)}</h1>" not in article:
            return False
        if f"column-{path.stem}.html" not in listing or title not in listing:
            return False
        listing_version = hashlib.sha256(listing.encode("utf-8")).hexdigest()[:12]
        if f"articles-data.js?v={listing_version}" not in knowledge:
            return False
        if thumbnail:
            fetcher(f"{BASE_URL}/{thumbnail}?check={nonce}")
        return True
    except (OSError, RuntimeError, ValueError):
        return False


def queue_priority(item: dict) -> int:
    return 0 if item.get("status") in {"failed", "deploying"} else 1


def stage(day: date, slot: str, *, visibility=site_visible, source_check=source_is_current) -> dict:
    if slot not in SLOTS:
        raise ValueError("Unrecognized publication slot")
    key = day.isoformat()
    state = load_state()
    record = state.setdefault("days", {}).setdefault(key, {"status": "waiting", "attempt_slots": []})
    if record.get("status") == "published":
        print("Today's publication is already verified")
        return record
    if slot in record.get("attempt_slots", []):
        print("This slot was already attempted")
        return record
    if len(record.get("attempt_slots", [])) >= 5:
        print("Five publication attempts have already been used")
        return record

    # A manually added or previously committed page counts as today's one article.
    today_files = article_for_day(key)
    if today_files:
        path = today_files[0]
        metadata, lines = read_article(path)
        if visibility(path, lines[0][2:].strip(), metadata.get("thumbnail", "")):
            record.update(status="published", article_path=str(path.relative_to(DIST)).replace("\\", "/"), verified_at=now_kst().isoformat(), last_error="")
            write_json(STATE_PATH, state)
            print("Today's article is already visible on the site")
            return record
        if len(today_files) > 1:
            raise RuntimeError("More than one article is assigned to today")

    choices = sorted(((path, item) for path, item in queue_items() if item.get("status") in {"ready", "deploying", "failed"}), key=lambda pair: (queue_priority(pair[1]), pair[1]["created_at"]))
    active = next(((path, item) for path, item in choices if str(path.relative_to(AUTOMATION)).replace("\\", "/") == record.get("queue_path")), None)
    if today_files:
        active = next(((path, item) for path, item in choices if item.get("article_path") == str(today_files[0].relative_to(DIST)).replace("\\", "/")), None)
    if active is None:
        active = choices[0] if choices and not today_files else None
    if active is None and not today_files:
        record.update(status="validation_failed", last_error="No verified draft is available")
        write_json(STATE_PATH, state)
        return record

    if active:
        queue_path, item = active
        if item.get("status") in {"ready", "failed", "deploying"}:
            while active and not source_check(item["source"]):
                item.update(status="stale", last_error="Official source changed before publication")
                write_json(queue_path, item)
                if today_files:
                    record.update(status="validation_failed", last_error="The staged article's official source changed")
                    write_json(STATE_PATH, state)
                    return record
                choices = [(p, x) for p, x in choices if p != queue_path]
                active = choices[0] if choices else None
                if active:
                    queue_path, item = active
            if active is None and not today_files:
                record.update(status="validation_failed", last_error="Every queued source changed before publication")
                write_json(STATE_PATH, state)
                return record
    if active:
        queue_path, item = active
        existing = item.get("article_path", "")
        path = DIST / existing if existing else slug_path(key, item["article"]["slug"])
        if not str(path.resolve()).startswith(str((DIST / "articles").resolve())):
            raise ValueError("Queued article path is unsafe")
        if not path.exists() or item.get("target_date") != key:
            basename = path.stem
            thumbnail = create_thumbnail(basename, item["article"]["title"], item["article"]["category"], item["article"]["summary"])
            path.write_text(serialize(key, item, thumbnail), encoding="utf-8")
            read_article(path)
            build_columns()
            build_sitemap()
        item.update(status="deploying", article_path=str(path.relative_to(DIST)).replace("\\", "/"), target_date=key, last_error="")
        item.setdefault("attempt_slots", []).append(slot)
        write_json(queue_path, item)
        record["queue_path"] = str(queue_path.relative_to(AUTOMATION)).replace("\\", "/")
        record["article_path"] = item["article_path"]
    else:
        record["article_path"] = str(today_files[0].relative_to(DIST)).replace("\\", "/")
    record.setdefault("attempt_slots", []).append(slot)
    record.update(status="deploying", last_error="", last_attempt_at=now_kst().isoformat())
    write_json(STATE_PATH, state)
    print(f"Staged publication attempt {len(record['attempt_slots'])}/5 for {key}")
    return record


def verify(day: date, *, max_wait_seconds: int = 540, interval_seconds: int = 20,
           visibility=site_visible, sleeper=time.sleep) -> dict:
    key = day.isoformat()
    state = load_state()
    record = state.setdefault("days", {}).setdefault(key, {"status": "waiting", "attempt_slots": []})
    if record.get("status") == "published":
        return record
    relative = record.get("article_path", "")
    if not relative:
        return record
    path = DIST / relative
    metadata, lines = read_article(path)
    title = lines[0][2:].strip()
    rounds = max(1, max_wait_seconds // max(1, interval_seconds))
    visible = False
    for index in range(rounds):
        if visibility(path, title, metadata.get("thumbnail", "")):
            visible = True
            break
        if index < rounds - 1:
            sleeper(interval_seconds)
    if visible:
        record.update(status="published", verified_at=now_kst().isoformat(), last_error="")
        print(f"Verified on public site: {BASE_URL}/column-{path.stem}")
    else:
        exhausted = len(record.get("attempt_slots", [])) >= 5
        record.update(status="failed" if exhausted else "deploying", last_error="Article is not visible on the public site after verification window")
        print(f"Site verification failed; attempts={len(record.get('attempt_slots', []))}/5")
    queue_path = record.get("queue_path")
    if queue_path:
        path_in_queue = AUTOMATION / queue_path
        if path_in_queue.exists():
            item = json.loads(path_in_queue.read_text(encoding="utf-8"))
            item.update(status="published" if visible else "failed" if len(record.get("attempt_slots", [])) >= 5 else "deploying", last_error=record["last_error"])
            write_json(path_in_queue, item)
    write_json(STATE_PATH, state)
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("prepare", "stage", "stage-now", "verify", "assert-published", "verify-existing"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--slot", default="")
    parser.add_argument("--wait-seconds", type=int, default=540)
    args = parser.parse_args()
    day = now_kst().date()
    if args.mode == "prepare":
        prepare(day, dry_run=args.dry_run)
    elif args.mode == "stage":
        stage(day, args.slot)
    elif args.mode == "stage-now":
        used = load_state().get("days", {}).get(day.isoformat(), {}).get("attempt_slots", [])
        available = next((slot for slot in SLOTS if slot not in used), None)
        if available:
            stage(day, available)
        else:
            print("No publication attempts remain today")
    elif args.mode == "verify":
        verify(day, max_wait_seconds=args.wait_seconds)
    elif args.mode == "assert-published":
        if load_state().get("days", {}).get(day.isoformat(), {}).get("status") != "published":
            raise RuntimeError("Today's article has not been verified on the public site")
    elif args.mode == "verify-existing":
        for path in article_for_day(day.isoformat()):
            metadata, lines = read_article(path)
            print(f"{path.name}: {'visible' if site_visible(path, lines[0][2:].strip(), metadata.get('thumbnail', '')) else 'not visible'}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"Column automation failed: {exc}", file=sys.stderr)
        sys.exit(1)
