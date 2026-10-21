"""Checks for the unattended article publisher; no API key is needed."""

from pathlib import Path
import sys
import tempfile
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_column import read_article  # noqa: E402
from publish_daily_column import choose_topic, serialize, validate_article  # noqa: E402


def article(title: str = "출원 전에 무엇을 점검할까요?") -> dict[str, str]:
    section = "기술의 차이와 공개 범위를 먼저 확인하고, 사안별로 관련 자료를 정리해 상담할 필요가 있습니다. " * 10
    body = "새로운 기술을 준비할 때는 발명의 특징을 구체적으로 정리하는 것이 도움이 됩니다.\n\n"
    body += "\n\n".join(f"## {number}. 점검할 항목 {number}\n\n{section}" for number in range(1, 5))
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
        self.assertEqual(lines[0], "# " + checked["title"])
        self.assertTrue(metadata["source_1_url"].startswith("https://"))

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


if __name__ == "__main__":
    unittest.main()
