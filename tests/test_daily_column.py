"""Simulation of the five publication and failure paths without API charges."""

from datetime import date, timedelta
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_column  # noqa: E402
import column_automation as evidence  # noqa: E402
import publish_daily_column as publisher  # noqa: E402


SOURCE = {
    "organization": "WIPO", "title": "Example official guide", "published": "2026-08",
    "url": "https://www.wipo.int/en/web/pct-system/faqs/faqs",
    "text": ("The granting of patents remains under the control of national or regional patent Offices in the national phase. " * 40).strip(),
    "body_sha256": "stable", "checked_at": "2026-10-21T06:00:00",
}
QUOTE = "The granting of patents remains under the control of national or regional patent Offices"
TOPIC = {"key": "pct-national-phase", "category": "해외특허", "question": "PCT 뒤에 무엇을 해야 하나요?", "related_url": "overseas.html", "related_label": "해외특허등록 살펴보기", "source": SOURCE}


def valid_article() -> dict:
    paragraph = "PCT 국제출원만으로 각국의 등록 특허가 생기지 않습니다. 권리를 원하는 국가의 절차와 현재 사업 목표를 나누어 살펴봐야 합니다. " * 6
    body = ":::takeaway\nPCT 다음에는 권리를 원하는 국가의 절차가 필요합니다.\n국가별 절차의 적용 여부는 실제 출원 상황에 따라 달라집니다. 먼저 목표 국가와 사업 계획을 정리하세요.\n:::\n\n"
    body += "해외 판매 계획을 세우는 기업이라면 여러 국가에서 보호를 원하는 이유를 먼저 정리할 수 있습니다.\n\n"
    for number in range(1, 4):
        body += f"## {number}. 국가단계에서 무엇을 확인할까요?\n\n{paragraph}〔1〕\n\n"
    body += ":::checklist\n- 권리가 필요한 국가가 정해졌나요?\n- 현지 사업 계획을 정리했나요?\n- 국가별 절차를 확인했나요?\n:::"
    body += "\n\n## 마무리\n\n사업 목적과 현지 절차를 함께 확인한 뒤 다음 행동을 정합니다. 〔1〕\n"
    return {
        "title": "PCT 다음 해외 권리 절차를 어떻게 준비할까요?", "category": "해외특허", "slug": "pct-next-step-guide",
        "summary": "PCT 이후 목표 국가와 절차를 정리할 때 확인할 사항입니다.",
        "meta_description": "PCT 국제출원 이후 국가별 특허 절차를 준비할 때 필요한 판단 기준을 살펴봅니다.",
        "body": body,
        "sources": [{"title": SOURCE["title"], "organization": SOURCE["organization"], "published": SOURCE["published"], "url": SOURCE["url"], "verified_excerpt": QUOTE}],
        "claims": [{"claim": f"각국의 심사가 필요합니다 {number}", "source_url": SOURCE["url"], "evidence_quote": QUOTE} for number in range(3)],
    }


class DraftTests(unittest.TestCase):
    def test_recent_window_covers_ninety_days(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as folder:
            dist = Path(folder)
            (dist / "articles").mkdir()
            with patch.object(evidence, "DIST", dist), patch.object(evidence, "QUEUE", dist / "queue"):
                for age in (89, 91):
                    day = date(2026, 10, 22) - timedelta(days=age)
                    (dist / "articles" / f"test-{age}.md").write_text(
                        f"---\npublished: {day.isoformat()}\n---\n# {age}일 전 글\n## 요약\n", encoding="utf-8")
                titles = [item["title"] for item in evidence.recent_articles(date(2026, 10, 22))]
        self.assertIn("89일 전 글", titles)
        self.assertNotIn("91일 전 글", titles)

    def test_fictional_example_is_rejected(self) -> None:
        article = valid_article()
        article["body"] += "\n가상 사례: A기업이 출원했다고 가정합니다."
        with self.assertRaisesRegex(ValueError, "Fictional examples"):
            evidence.validate_article(article, TOPIC, SOURCE, [])

    def test_source_linked_comparison_table_renders(self) -> None:
        article = valid_article()
        article["body"] = article["body"].replace(
            "## 2. 국가단계", "| 항목 | 확인할 내용 |\n| --- | --- |\n| 권리 | 현지 심사가 필요합니다〔1〕 |\n\n## 2. 국가단계", 1)
        checked = evidence.validate_article(article, TOPIC, SOURCE, [])
        body, _ = build_column.render_guide_body(["# 제목", "## 요약", *checked["body"].splitlines()])
        self.assertIn('<table class="insight-table">', body)
        self.assertIn('href="#source-1"', body)

    def test_unsupported_presentation_is_normalized_before_queueing(self) -> None:
        article = valid_article()
        article["body"] = article["body"].replace("## 1.", "## 도입 설명\n\n도입입니다.\n\n## 1.", 1)
        article["body"] = article["body"].replace("## 2.", ":::quote\n검증된 자료의 설명입니다.\n:::\n\n## 2.", 1)
        cleaned = evidence.clean_article(article, TOPIC)
        evidence.validate_article(cleaned, TOPIC, SOURCE, [])
        self.assertNotIn(":::quote", cleaned["body"])
        self.assertNotIn("## 도입 설명", cleaned["body"])

    def test_presentational_variants_are_normalized(self) -> None:
        article = valid_article()
        article["body"] = article["body"].replace(":::takeaway", "## 핵심 답", 1).replace("\n:::\n\n해외", "\n\n해외", 1)
        article["body"] = article["body"].replace("## 마무리", "## 결론")
        article["body"] = article["body"].replace("## 1.", "### 01)")
        cleaned = evidence.clean_article(article, TOPIC)
        self.assertTrue(cleaned["body"].startswith(":::takeaway\n"))
        self.assertIn("## 1.", cleaned["body"])
        self.assertIn("## 마무리", cleaned["body"])

    def test_editorial_format_and_direct_evidence(self) -> None:
        article = evidence.validate_article(valid_article(), TOPIC, SOURCE, [])
        lines = ["# " + article["title"], "## 핵심 답", *article["body"].splitlines()]
        body, toc = build_column.render_guide_body(lines)
        self.assertIn('href="#source-1"', body)
        self.assertEqual(toc.count('href="#section-'), 3)

    def test_invalid_draft_is_repaired_and_audited(self) -> None:
        broken = valid_article()
        broken["body"] = "근거 없는 짧은 글"
        answers = iter([broken, valid_article(), {"supported": True, "unsupported_claims": []}])
        generated = []

        def fake_generate(prompt: str, key: str) -> dict:
            generated.append(prompt)
            return next(answers)

        result = evidence.draft_one(date(2026, 10, 22), TOPIC, SOURCE, [], "fake-key", fake_generate)
        self.assertEqual(result["slug"], "pct-next-step-guide")
        self.assertEqual(len(generated), 3)
        self.assertIn("문제로 보류", generated[1])

    def test_unsupported_number_is_rejected(self) -> None:
        item = valid_article()
        item["body"] = item["body"].replace("사업 목적과", "999개월 뒤 사업 목적과")
        with self.assertRaisesRegex(ValueError, "Unverified number"):
            evidence.validate_article(item, TOPIC, SOURCE, [])


class PublicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        dist = root / "dist"
        (dist / "articles").mkdir(parents=True)
        (dist / "assets").mkdir()
        (dist / "assets" / "pct-column-hero.webp").write_bytes(b"test")
        (dist / "overseas.html").write_text("ok", encoding="utf-8")
        automation = root / "automation"
        queue = automation / "queue"
        queue.mkdir(parents=True)
        self.dist, self.automation, self.queue = dist, automation, queue
        self.patches = [
            patch.object(publisher, "DIST", dist), patch.object(publisher, "AUTOMATION", automation),
            patch.object(publisher, "QUEUE", queue), patch.object(publisher, "STATE_PATH", automation / "state.json"),
            patch.object(build_column, "DIST", dist), patch.object(evidence, "DIST", dist),
            patch.object(evidence, "QUEUE", queue), patch.object(publisher, "build_columns", lambda: None),
            patch.object(publisher, "build_sitemap", lambda: None),
            patch.object(publisher, "create_thumbnail", self.fake_thumbnail),
        ]
        for active in self.patches:
            active.start()
            self.addCleanup(active.stop)
        self.item_path = queue / "prepared.json"
        self.item = {
            "status": "ready", "created_at": "2026-10-21T06:00:00+09:00",
            "topic_key": "pct-national-phase", "article": valid_article(), "source": SOURCE,
            "article_path": "", "target_date": "", "attempt_slots": [], "last_error": "",
        }
        publisher.write_json(self.item_path, self.item)

    def fake_thumbnail(self, slug: str, title: str, category: str, summary: str) -> str:
        name = f"assets/{slug}-thumb.webp"
        (self.dist / name).write_bytes(b"RIFFtestWEBP")
        return name

    def test_normal_publication_requires_live_site(self) -> None:
        day = date(2026, 10, 22)
        record = publisher.stage(day, publisher.SLOTS[0], visibility=lambda *a: False, source_check=lambda *a: True)
        self.assertEqual(record["status"], "deploying")
        self.assertEqual(len(list((self.dist / "articles").glob("*.md"))), 1)
        result = publisher.verify(day, max_wait_seconds=1, visibility=lambda *a: True)
        self.assertEqual(result["status"], "published")

    def test_transient_upload_or_deploy_failure_retries_same_page(self) -> None:
        day = date(2026, 10, 22)
        publisher.stage(day, publisher.SLOTS[0], visibility=lambda *a: False, source_check=lambda *a: True)
        publisher.verify(day, max_wait_seconds=1, visibility=lambda *a: False)
        publisher.stage(day, publisher.SLOTS[1], visibility=lambda *a: False, source_check=lambda *a: True)
        self.assertEqual(len(list((self.dist / "articles").glob("*.md"))), 1)
        self.assertEqual(len(publisher.load_state()["days"][day.isoformat()]["attempt_slots"]), 2)

    def test_five_failures_keep_draft_for_next_day(self) -> None:
        first = date(2026, 10, 22)
        for slot in publisher.SLOTS:
            publisher.stage(first, slot, visibility=lambda *a: False, source_check=lambda *a: True)
            publisher.verify(first, max_wait_seconds=1, visibility=lambda *a: False)
        self.assertEqual(publisher.load_state()["days"][first.isoformat()]["status"], "failed")
        next_day = date(2026, 10, 23)
        publisher.stage(next_day, publisher.SLOTS[0], visibility=lambda *a: False, source_check=lambda *a: True)
        self.assertEqual(len(list((self.dist / "articles").glob("*.md"))), 1)
        path = next((self.dist / "articles").glob("*.md"))
        self.assertEqual(build_column.read_article(path)[0]["published"], "2026-10-23")

    def test_duplicate_attempt_does_not_create_second_article(self) -> None:
        day = date(2026, 10, 22)
        publisher.stage(day, publisher.SLOTS[0], visibility=lambda *a: False, source_check=lambda *a: True)
        publisher.verify(day, max_wait_seconds=1, visibility=lambda *a: True)
        publisher.stage(day, publisher.SLOTS[1], visibility=lambda *a: True, source_check=lambda *a: True)
        self.assertEqual(len(list((self.dist / "articles").glob("*.md"))), 1)
        self.assertEqual(len(publisher.load_state()["days"][day.isoformat()]["attempt_slots"]), 1)

    def test_failed_topic_is_replaced_before_queueing(self) -> None:
        self.item_path.unlink()
        attempts = []

        def fake_drafter(day, topic, source, recent, key):
            attempts.append(topic["key"])
            if len(attempts) == 1:
                raise ValueError("evidence too weak")
            article = valid_article()
            article["category"] = topic["category"]
            return article

        publisher.prepare(date(2026, 10, 22), dry_run=True, api_key="fake", fetcher=lambda _: SOURCE, drafter=fake_drafter)
        self.assertEqual(len(attempts), 2)
        self.assertEqual(len(list(self.queue.glob("*.json"))), 0)

    def test_prepublication_assigns_one_future_date_per_draft(self) -> None:
        day = date(2026, 10, 22)
        second = json.loads(self.item_path.read_text(encoding="utf-8"))
        second["article"]["slug"] = "another-pct-guide"
        publisher.write_json(self.queue / "second.json", second)
        paths = publisher.schedule_upcoming(day, source_check=lambda _: True)
        self.assertEqual(len(paths), 2)
        self.assertEqual([build_column.read_article(path)[0]["published"] for path in paths],
                         [(day + timedelta(days=offset)).isoformat() for offset in (1, 2)])
        manifest = json.loads((self.dist / "publication-schedule.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["articles"]), 2)
        self.assertEqual(manifest["articles"][0]["publish_at"], "2026-10-23T08:00:00+09:00")
        self.assertEqual(publisher.schedule_upcoming(day, source_check=lambda _: True), [])

    def test_queue_is_refilled_only_up_to_seven_and_three_per_day(self) -> None:
        day = date(2026, 10, 22)
        self.item["created_at"] = "2026-10-21T06:00:00+09:00"
        publisher.write_json(self.item_path, self.item)
        for index in range(5):
            extra = json.loads(self.item_path.read_text(encoding="utf-8"))
            extra["article"]["slug"] = f"extra-guide-{index}"
            publisher.write_json(self.queue / f"extra-{index}.json", extra)
        calls = []

        def draft(day, topic, source, recent, api_key):
            calls.append(topic["key"])
            article = valid_article()
            article["slug"] = "newly-prepared-guide"
            return article

        publisher.prepare(day, api_key="fake", fetcher=lambda _: SOURCE, drafter=draft)
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(list(self.queue.glob("*.json"))), 7)
        publisher.prepare(day, api_key="fake", fetcher=lambda _: SOURCE, drafter=draft)
        self.assertEqual(len(calls), 1)

    def test_live_verifier_accepts_time_filtered_listing(self) -> None:
        path = self.dist / "articles" / "daily-2026-10-23-test.md"
        thumbnail = self.fake_thumbnail(path.stem, "title", "해외특허", "summary")
        path.write_text(publisher.serialize("2026-10-23", self.item, thumbnail), encoding="utf-8")
        title = self.item["article"]["title"]

        def fetch(url):
            if "articles-data.js" in url:
                return f'window.VON_ARTICLES=[{{"href":"column-{path.stem}.html","title":"{title}"}}];'
            if "knowledge.html" in url:
                return '<script src="articles-data.js?v=123456789abc"></script>'
            return f'<h1>{title}</h1>'

        self.assertTrue(publisher.site_visible(path, title, thumbnail, fetcher=fetch))

    def test_prepublication_requires_cloudflare_confirmation(self) -> None:
        day = date(2026, 10, 22)
        publisher.schedule_upcoming(day, source_check=lambda _: True)
        calls = []

        def fetch(url):
            calls.append(url)
            return json.dumps({"ready_dates": ["2026-10-23"]})

        self.assertTrue(publisher.verify_prepublication(day, max_wait_seconds=20, fetcher=fetch))
        self.assertEqual(len(calls), 1)
        with self.assertRaisesRegex(RuntimeError, "did not confirm"):
            publisher.verify_prepublication(day, max_wait_seconds=20,
                                            fetcher=lambda _: json.dumps({"ready_dates": []}))


if __name__ == "__main__":
    unittest.main()
