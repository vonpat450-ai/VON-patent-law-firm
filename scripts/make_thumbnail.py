"""Create photographic column thumbnails from the site's licensed image library.

The daily job is unattended and uses no image API or paid service. Each source
image was already supplied for this site. Keep the mapping here editable when
new source photographs are approved for use.
"""

from __future__ import annotations

from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "dist" / "assets"
SOURCES = {
    "global": "overseas-hero.png",
    "search": "search-hero.png",
    "draft": "process-center.png",
    "review": "priority-center.png",
    "disclosure": "home-center.png",
    "filing": "process-hero.png",
}


def theme_for(value: str) -> str:
    if any(word in value for word in ("PCT", "국제", "해외", "국가")):
        return "global"
    if any(word in value for word in ("선행", "검색", "조사")):
        return "search"
    if any(word in value for word in ("명세서", "기술 설명", "기재")):
        return "draft"
    if any(word in value for word in ("심사", "거절", "의견제출")):
        return "review"
    if any(word in value for word in ("공개", "아이디어", "발표")):
        return "disclosure"
    return "filing"


def create_thumbnail(slug: str, title: str, category: str, description: str = "") -> str:
    if not re.fullmatch(r"daily-[0-9]{4}-[0-9]{2}-[0-9]{2}(?:-[a-z0-9]+)*", slug):
        raise ValueError("Invalid daily column slug")
    theme = theme_for(title)
    if theme == "filing":
        theme = theme_for(description)
    source = ASSETS / SOURCES[theme]
    if not source.is_file():
        raise FileNotFoundError(f"Thumbnail source is missing: {source.name}")
    target = ASSETS / f"{slug}-thumb.webp"

    with Image.open(source) as original:
        photo = ImageOps.fit(original.convert("RGB"), (1200, 600), Image.Resampling.LANCZOS, centering=(0.6, 0.5))

    # Bring different site photographs into the same dark-blue editorial style.
    cool = Image.new("RGBA", photo.size, (9, 34, 53, 42))
    photo = Image.alpha_composite(photo.convert("RGBA"), cool)
    shadow = Image.new("RGBA", photo.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    for x in range(1200):
        strength = int(195 * max(0, 1 - x / 850) ** 1.45)
        draw.line((x, 0, x, 600), fill=(5, 27, 43, strength))
    photo = Image.alpha_composite(photo, shadow).convert("RGB")
    photo.save(target, "WEBP", quality=84, method=6)
    return f"assets/{target.name}"


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        raise SystemExit("Usage: make_thumbnail.py <daily-slug> <title> <category>")
    print(create_thumbnail(sys.argv[1], sys.argv[2], sys.argv[3]))
