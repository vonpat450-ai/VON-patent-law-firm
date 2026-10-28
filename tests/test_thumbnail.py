"""Checks for the image source fallback and deterministic Korean title overlay."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import make_thumbnail  # noqa: E402


class ThumbnailTests(unittest.TestCase):
    def test_generated_image_gets_centered_pretendard_label(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as folder:
            assets = Path(folder)
            photo = Image.new("RGB", (1200, 600), "#6c8291")
            with patch.object(make_thumbnail, "ASSETS", assets), \
                 patch.dict("os.environ", {"MAGNIFIC_API_KEY": "test-key"}), \
                 patch.object(make_thumbnail, "magnific_photo", return_value=photo) as generate:
                path = make_thumbnail.create_thumbnail(
                    "daily-2026-10-23-pct-country-guide", "PCT 이후 국가단계는 어떻게 준비하나요?",
                    "해외특허", "국가별 절차 안내", label="PCT 국가단계", visual="A globe and mechanical drawings")
            self.assertEqual(generate.call_count, 1)
            with Image.open(assets / Path(path).name) as result:
                self.assertEqual(result.size, (1200, 600))
                # The centered title, translucent black panel and white border
                # must all differ from the untouched background.
                self.assertNotEqual(result.getpixel((600, 300)), photo.getpixel((600, 300)))

    def test_fixed_semibold_size_and_two_line_limit(self) -> None:
        font = ImageFont.truetype(str(make_thumbnail.FONT), make_thumbnail.TITLE_FONT_SIZE)
        self.assertEqual(len(make_thumbnail.title_lines("특허 등록", font)), 1)
        self.assertEqual(len(make_thumbnail.title_lines("해외특허 국가단계 준비와 현지 심사", font)), 2)
        with self.assertRaisesRegex(ValueError, "more than two lines"):
            make_thumbnail.title_lines("해외특허 국가단계 준비와 현지 심사 " * 4, font)

    def test_october_29_switches_to_seventy_five_percent(self) -> None:
        self.assertEqual(make_thumbnail.panel_opacity_for_slug("daily-2026-10-28-example"), 50)
        self.assertEqual(make_thumbnail.panel_opacity_for_slug("daily-2026-10-29-example"), 75)
        self.assertEqual(make_thumbnail.panel_opacity_for_slug("daily-2026-11-04-example"), 75)

    def test_future_panel_is_seventy_five_percent_black_with_opaque_white_border(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as folder:
            target = Path(folder) / "example.webp"
            make_thumbnail.render_thumbnail(Image.new("RGB", (1200, 600), "#808080"), "특허 등록", target)
            with Image.open(target) as result:
                # A point within the panel but above the glyphs: 128 * 0.25 ≈ 32.
                interior = result.getpixel((600, 245))[0]
                self.assertGreaterEqual(interior, 27)
                self.assertLessEqual(interior, 38)
                # Away from the panel the photograph is not darkened.
                self.assertGreaterEqual(result.getpixel((40, 40))[0], 123)
                font = ImageFont.truetype(str(make_thumbnail.FONT), make_thumbnail.TITLE_FONT_SIZE)
                bounds = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), "특허 등록", font=font)
                border_y = (600 - (bounds[3] - bounds[1] + 116)) // 2
                self.assertGreaterEqual(min(result.getpixel((600, border_y))), 240)

    def test_failed_service_keeps_licensed_photo_fallback(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as folder:
            assets = Path(folder)
            Image.new("RGB", (1200, 600), "#6c8291").save(assets / "overseas-hero.png")
            with patch.object(make_thumbnail, "ASSETS", assets), \
                 patch.dict("os.environ", {"MAGNIFIC_API_KEY": "test-key"}), \
                 patch.object(make_thumbnail, "magnific_photo", side_effect=OSError("down")):
                path = make_thumbnail.create_thumbnail(
                    "daily-2026-10-23-pct-country-guide", "PCT 국가단계", "해외특허")
                self.assertTrue((assets / Path(path).name).is_file())
                with self.assertRaisesRegex(RuntimeError, "Magnific image unavailable"):
                    make_thumbnail.create_thumbnail(
                        "daily-2026-10-23-pct-country-guide", "PCT 국가단계", "해외특허",
                        require_ai=True)


if __name__ == "__main__":
    unittest.main()
