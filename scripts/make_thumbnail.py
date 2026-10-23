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


THUMB_SIZE = (1200, 600)
TITLE_FONT_SIZE = 78  # About 105 pt at the example's 1600-pixel width.
TITLE_MAX_WIDTH = 920


def title_lines(label: str, font: ImageFont.FreeTypeFont) -> list[str]:
    """Keep one fixed font size and a maximum of two balanced lines."""
    label = re.sub(r"\s+", " ", label).strip()
    if not label:
        raise ValueError("Thumbnail label is empty")
    measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    width = lambda value: measure.textbbox((0, 0), value, font=font)[2]
    if width(label) <= TITLE_MAX_WIDTH:
        return [label]
    candidates = []
    for index in range(1, len(label)):
        first, second = label[:index].strip(), label[index:].strip()
        if first and second and max(width(first), width(second)) <= TITLE_MAX_WIDTH:
            gap = abs(width(first) - width(second))
            split_penalty = 0 if label[index - 1:index] == " " or label[index:index + 1] == " " else 100
            candidates.append((gap + split_penalty, first, second))
    if not candidates:
        raise ValueError("Thumbnail label needs more than two lines; choose a shorter phrase")
    _, first, second = min(candidates)
    return [first, second]


def render_thumbnail(photo: Image.Image, label: str, target: Path) -> None:
    background = ImageOps.fit(photo.convert("RGB"), THUMB_SIZE, Image.Resampling.LANCZOS)
    font = ImageFont.truetype(str(FONT), TITLE_FONT_SIZE)
    lines = title_lines(label, font)
    measure = ImageDraw.Draw(background)
    line_boxes = [measure.textbbox((0, 0), line, font=font) for line in lines]
    text_width = max(box[2] - box[0] for box in line_boxes)
    line_height = max(box[3] - box[1] for box in line_boxes)
    line_gap = 18 if len(lines) == 2 else 0
    text_height = len(lines) * line_height + line_gap
    panel_width = max(400, min(1080, text_width + 176))
    panel_height = text_height + 116
    left = (THUMB_SIZE[0] - panel_width) // 2
    top = (THUMB_SIZE[1] - panel_height) // 2
    rect = (left, top, left + panel_width, top + panel_height)

    # 30% pure black, followed by an opaque white border. Keep the photo visible.
    panel = Image.new("RGBA", THUMB_SIZE, (0, 0, 0, 0))
    ImageDraw.Draw(panel).rounded_rectangle(rect, radius=20, fill=(0, 0, 0, 77))
    frame = Image.alpha_composite(background.convert("RGBA"), panel)
    draw = ImageDraw.Draw(frame)
    draw.rounded_rectangle(rect, radius=20, outline=(255, 255, 255, 255), width=4)
    cursor = THUMB_SIZE[1] / 2 - text_height / 2
    for line, bounds in zip(lines, line_boxes):
        actual_width = bounds[2] - bounds[0]
        draw.text((THUMB_SIZE[0] / 2 - actual_width / 2 - bounds[0], cursor - bounds[1]),
                  line, font=font, fill=(255, 255, 255, 255))
        cursor += line_height + line_gap
    target.parent.mkdir(parents=True, exist_ok=True)
    frame.convert("RGB").save(target, "WEBP", quality=86, method=6)


def create_thumbnail(slug: str, title: str, category: str, description: str = "",
                     *, label: str = "", visual: str = "", require_ai: bool = False,
                     reuse_photo: bool = False) -> str:
    if slug != "pct-country-strategy" and not re.fullmatch(
        r"daily-[0-9]{4}-[0-9]{2}-[0-9]{2}(?:-[a-z0-9]+)*", slug
    ):
        raise ValueError("Invalid daily column slug")
    target = ASSETS / f"{slug}-thumb.webp"
    raw_target = ASSETS / f"{slug}-photo.webp"
    api_key = os.environ.get("MAGNIFIC_API_KEY", "")
    photo = None
    if reuse_photo and raw_target.is_file():
        with Image.open(raw_target) as original:
            photo = original.convert("RGB")
    if photo is None and api_key:
        try:
            photo = magnific_photo(visual_prompt(title, category, description, visual), api_key)
            print(f"Magnific image generated for {slug}")
        except (OSError, ValueError, RuntimeError, TimeoutError) as exc:
            if require_ai:
                raise RuntimeError("Magnific image unavailable") from exc
            print(f"Magnific image unavailable ({type(exc).__name__}); using licensed photo")
    elif photo is None and require_ai:
        raise RuntimeError("MAGNIFIC_API_KEY is missing")
    if photo is None:
        theme = theme_for(title)
        if theme == "filing":
            theme = theme_for(description)
        source = ASSETS / SOURCES[theme]
        with Image.open(source) as original:
            photo = original.convert("RGB")
    # Save the clean source photo so a later layout revision needs no new AI call.
    ImageOps.fit(photo.convert("RGB"), THUMB_SIZE, Image.Resampling.LANCZOS).save(
        raw_target, "WEBP", quality=88, method=6)
    render_thumbnail(photo, short_label(title, category, label), target)
    return f"assets/{target.name}"


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        raise SystemExit("Usage: make_thumbnail.py <daily-slug> <title> <category>")
    print(create_thumbnail(sys.argv[1], sys.argv[2], sys.argv[3]))
