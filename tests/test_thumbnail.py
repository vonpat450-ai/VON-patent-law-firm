"""Checks for the image source fallback and deterministic Korean title overlay."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

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
                # The central text and navy panel are both distinctly darker/brighter
                # than the original solid-color photo.
                self.assertNotEqual(result.getpixel((600, 300)), photo.getpixel((600, 300)))

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
