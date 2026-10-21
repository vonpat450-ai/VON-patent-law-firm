"""Checks for the unattended article publisher; no API key is needed."""

from pathlib import Path
import sys
import tempfile
import unittest
from PIL import Image


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_column import read_article, render_insight_body  # noqa: E402
from make_thumbnail import create_thumbnail, theme_for  # noqa: E402
from publish_daily_column import choose_topic, serialize, validate_article  # noqa: E402


def article(title: str = "출원 전에 무엇을 점검할까요?") -> dict[str, str]:
    section = "기술의 차이와 공개 범위를 먼저 확인하고, 사안별로 관련 자료를 정리해 상담할 필요가 있습니다. " * 5
    body = ":::takeaway\n출원 전 공개 여부를 확인하세요.\n기술의 핵심을 정리하고 공개 일정을 점검합니다.\n:::\n\n"
    body += "새로운 기술을 준비할 때는 발명의 특징을 구체적으로 정리하는 것이 도움이 됩니다.\n\n"
    extras = {
        1: ":::quote\n먼저 공개 일정을 살펴보세요.\n:::",
        2: ":::cards\n- 신규성 | 새로운지 확인합니다.\n- 진보성 | 차이를 확인합니다.\n- 이용가능성 | 활용할 수 있는지 확인합니다.\n:::",
        3: ":::steps\n- 조사 | 비슷한 기술을 찾습니다.\n- 비교 | 차이점을 적습니다.\n- 검토 | 방향을 정합니다.\n:::",
        4: ":::checklist\n- 공개 날짜가 있나요?\n- 기술을 설명할 수 있나요?\n- 기존 기술과 다른가요?\n- 자료를 정리했나요?\n:::",
    }
    body += "\n\n".join(f"## {number}. 분류 {number} | 점검할 항목 {number}\n\n{section}\n\n{extras.get(number, '')}" for number in range(1, 6))
    return {"title": title, "subtitle": "준비 단계의 확인 사항", "description": "특허 준비 시 확인할 항목을 알아봅니다.", "body": body}


class DailyColumnTests(unittest.TestCase):
    def test_valid_article_matches_site_builder(self) -> None:
        checked = validate_article(article(), ["다른 기존 제목"])
        document = serialize("2026-10-21", choose_topic("2026-10-21"), checked)
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            path = Path(directory) / "daily-2026-10-21.md"
            path.write_text(document, encoding="utf-8")
            metadata, lines = read_article(path)
        self.assertEqual(metadata["published"], "2026-10-21")
        self.assertEqual(metadata["layout"], "insight")
        self.assertEqual(lines[0], "# " + checked["title"])
        self.assertTrue(metadata["source_1_url"].startswith("https://"))
        html, toc = render_insight_body(lines)
        self.assertIn('class="insight-cards"', html)
        self.assertIn('href="#section-5"', toc)

    def test_duplicate_title_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "already exists"):
            validate_article(article(), ["출원 전에 무엇을 점검할까요?"])

    def test_short_body_is_rejected(self) -> None:
        candidate = article()
        candidate["body"] = "짧은 원고"
        with self.assertRaisesRegex(ValueError, "Body length"):
            validate_article(candidate, [])

    def test_broken_related_page_is_rejected(self) -> None:
        checked = validate_article(article(), [])
        document = serialize("2026-10-21", choose_topic("2026-10-21"), checked)
        document = document.replace("related_url: process.html", "related_url: missing.html")
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            path = Path(directory) / "daily-2026-10-21.md"
            path.write_text(document, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "related_url"):
                read_article(path)

    def test_missing_insight_block_is_rejected(self) -> None:
        candidate = article()
        candidate["body"] = candidate["body"].replace(":::takeaway", ":::other")
        with self.assertRaisesRegex(ValueError, "takeaway"):
            validate_article(candidate, [])

    def test_topic_thumbnail_is_photographic_webp(self) -> None:
        self.assertEqual(theme_for("특허출원 전 아이디어 공개, 안전할까요?"), "disclosure")
        self.assertEqual(theme_for("PCT 국제출원 준비"), "global")
        path = create_thumbnail("daily-2026-10-21", "특허출원 전 아이디어 공개, 안전할까요?", "국내특허")
        self.assertEqual(path, "assets/daily-2026-10-21-thumb.webp")
        with Image.open(Path(__file__).resolve().parents[1] / "dist" / path) as photo:
            self.assertEqual(photo.size, (1200, 600))


if __name__ == "__main__":
    unittest.main()
