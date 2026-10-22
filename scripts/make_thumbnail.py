"""Make one photographic, centrally titled thumbnail for each column.

Use one Magnific task when configured, with licensed site photos as a fallback.
Text is rendered locally so generated images cannot misspell Korean.
"""

from __future__ import annotations

from io import BytesIO
import json
import os
from pathlib import Path
import re
import time
from urllib import parse, request

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "dist" / "assets"
FONT = ROOT / "scripts" / "fonts" / "Pretendard-SemiBold.otf"
MAGNIFIC_URL = "https://api.magnific.com/v1/ai/mystic"
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


def short_label(title: str, category: str, suggested: str = "") -> str:
    label = re.sub(r"\s+", " ", suggested).strip(" .?!,·")
    if 2 <= len(label) <= 18 and "\n" not in label:
        return label
    for word, fallback in (
        ("PCT", "PCT 국제출원"), ("국가단계", "PCT 국가단계"),
        ("공개", "출원 전 아이디어 공개"), ("명세서", "특허 명세서"),
        ("우선심사", "특허 우선심사"), ("선행기술", "선행기술 조사"),
        ("심사", "특허 심사"), ("해외", "해외특허 출원"),
    ):
        if word in title:
            return fallback
    return "해외특허 전략" if category == "해외특허" else "국내특허 실무"


def visual_prompt(title: str, category: str, summary: str, visual: str = "") -> str:
    subject = visual.strip() if visual.strip() else f"A visual metaphor for {title}. {summary}"
    return (
        "Premium photorealistic editorial photograph for a Korean patent law firm's article. "
        f"Subject: {subject[:500]}. Category: {category}. "
        "Realistic physical materials, precision engineering or carefully composed documents; "
        "deep navy, steel blue and restrained silver palette; refined natural light, clear focal point, "
        "full-frame composition with interesting details across the entire image. "
        "No people, letters, words, numbers, logos, seals, watermarks, or fake patent certificates. "
        "Do not imply a specific legal outcome."
    )


def _api_json(url: str, api_key: str, payload: dict | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = request.Request(url, data=body, headers={
        "x-magnific-api-key": api_key, "Content-Type": "application/json",
    }, method="POST" if body is not None else "GET")
    with request.urlopen(req, timeout=30) as response:
        return json.load(response)


def magnific_photo(prompt: str, api_key: str) -> Image.Image:
    """Submit at most one billable task, then poll that same task."""
    result = _api_json(MAGNIFIC_URL, api_key, {
        "prompt": prompt, "resolution": "2k", "aspect_ratio": "horizontal_2_1",
        "model": "realism", "creative_detailing": 20,
    })
    task_id = str(result.get("data", {}).get("task_id", ""))
    if not re.fullmatch(r"[0-9a-fA-F-]{36}", task_id):
        raise RuntimeError("Magnific returned no valid task ID")
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        result = _api_json(f"{MAGNIFIC_URL}/{task_id}", api_key).get("data", {})
        status = result.get("status")
        if status == "COMPLETED":
            urls = result.get("generated", [])
            if not urls or any(result.get("has_nsfw") or []):
                raise RuntimeError("Magnific did not provide a usable image")
            image_url = str(urls[0])
            parsed = parse.urlsplit(image_url)
            host = (parsed.hostname or "").lower()
            if parsed.scheme != "https" or not any(
                host == suffix or host.endswith("." + suffix)
                for suffix in ("freepik.com", "magnific.com", "freepikcdn.com")
            ):
                raise RuntimeError("Magnific returned an unexpected image host")
            with request.urlopen(image_url, timeout=45) as response:
                data = response.read(15_000_001)
            if len(data) > 15_000_000:
                raise RuntimeError("Magnific image is too large")
            image = Image.open(BytesIO(data))
            image.load()
            return image.convert("RGB")
        if status in {"FAILED", "ERROR", "CANCELED", "CANCELLED"}:
            raise RuntimeError("Magnific image task failed")
        time.sleep(8)
    raise TimeoutError("Magnific image task did not complete in time")


def render_thumbnail(photo: Image.Image, label: str, target: Path) -> None:
    frame = ImageOps.fit(photo.convert("RGB"), (1200, 600), Image.Resampling.LANCZOS)
    frame = Image.alpha_composite(frame.convert("RGBA"), Image.new("RGBA", frame.size, (9, 34, 53, 34)))
    draw = ImageDraw.Draw(frame)
    font_size = 66
    while True:
        font = ImageFont.truetype(str(FONT), font_size)
        bounds = draw.textbbox((0, 0), label, font=font)
        text_width = bounds[2] - bounds[0]
        if text_width <= 980 or font_size <= 38:
            break
        font_size -= 2
    panel_width = min(1080, text_width + 100)
    left = (1200 - panel_width) // 2
    draw.rounded_rectangle((left, 238, left + panel_width, 362), radius=14, fill=(7, 32, 47, 222))
    text_height = bounds[3] - bounds[1]
    draw.text((600 - text_width / 2, 300 - text_height / 2 - bounds[1]), label,
              font=font, fill=(255, 255, 255, 255))
    target.parent.mkdir(parents=True, exist_ok=True)
    frame.convert("RGB").save(target, "WEBP", quality=86, method=6)


def create_thumbnail(slug: str, title: str, category: str, description: str = "",
                     *, label: str = "", visual: str = "", require_ai: bool = False) -> str:
    if not re.fullmatch(r"daily-[0-9]{4}-[0-9]{2}-[0-9]{2}(?:-[a-z0-9]+)*", slug):
        raise ValueError("Invalid daily column slug")
    target = ASSETS / f"{slug}-thumb.webp"
    api_key = os.environ.get("MAGNIFIC_API_KEY", "")
    photo = None
    if api_key:
        try:
            photo = magnific_photo(visual_prompt(title, category, description, visual), api_key)
            print(f"Magnific image generated for {slug}")
        except (OSError, ValueError, RuntimeError, TimeoutError) as exc:
            if require_ai:
                raise RuntimeError("Magnific image unavailable") from exc
            print(f"Magnific image unavailable ({type(exc).__name__}); using licensed photo")
    elif require_ai:
        raise RuntimeError("MAGNIFIC_API_KEY is missing")
    if photo is None:
        theme = theme_for(title)
        if theme == "filing":
            theme = theme_for(description)
        source = ASSETS / SOURCES[theme]
        with Image.open(source) as original:
            photo = original.convert("RGB")
    render_thumbnail(photo, short_label(title, category, label), target)
    return f"assets/{target.name}"


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        raise SystemExit("Usage: make_thumbnail.py <daily-slug> <title> <category>")
    print(create_thumbnail(sys.argv[1], sys.argv[2], sys.argv[3]))
