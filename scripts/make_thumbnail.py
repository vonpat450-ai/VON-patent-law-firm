"""Create a topic-aware patent column illustration without paid image APIs."""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "dist" / "assets"
PALETTES = (
    ("#103640", "#1c6175", "#7fd0e4"),
    ("#102e3b", "#225c7c", "#89cee4"),
    ("#0f3440", "#23718a", "#a1dbe6"),
    ("#11323d", "#1d617a", "#80c9e2"),
)


def theme_for(title: str) -> str:
    if any(word in title for word in ("PCT", "국제", "해외", "국가")):
        return "global"
    if any(word in title for word in ("선행", "검색", "조사")):
        return "search"
    if any(word in title for word in ("명세서", "기술 설명", "기재")):
        return "draft"
    if any(word in title for word in ("심사", "거절", "의견제출")):
        return "review"
    if any(word in title for word in ("공개", "아이디어", "발표")):
        return "disclosure"
    return "filing"


MOTIFS = {
    "disclosure": '''
      <circle cx="180" cy="170" r="121" fill="none" stroke="#d7f3f9" stroke-width="3" opacity=".45" stroke-dasharray="8 13"/>
      <path d="M180 64c-62 0-104 44-104 100 0 40 20 65 47 90 13 12 21 25 22 41h70c1-16 9-29 22-41 27-25 47-50 47-90 0-56-42-100-104-100Z" fill="url(#glass)" stroke="#d7f3f9" stroke-width="5"/>
      <path d="M144 294h72m-63 18h54m-43 18h32" stroke="#d7f3f9" stroke-width="6" stroke-linecap="round"/>
      <path d="M147 171l22 23 44-51" fill="none" stroke="#d7f3f9" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M180 25v-18m-128 162H34m292 0h-18M87 72 74 59m213 13 13-13" stroke="#8ed6e6" stroke-width="6" stroke-linecap="round"/>
    ''',
    "global": '''
      <circle cx="180" cy="180" r="125" fill="url(#glass)" stroke="#d7f3f9" stroke-width="4"/>
      <ellipse cx="180" cy="180" rx="57" ry="125" fill="none" stroke="#d7f3f9" stroke-width="3" opacity=".7"/>
      <path d="M55 180h250M76 109h208M76 251h208" stroke="#d7f3f9" stroke-width="3" opacity=".6"/>
      <ellipse cx="180" cy="180" rx="166" ry="67" transform="rotate(-23 180 180)" fill="none" stroke="#9bdbe9" stroke-width="4" stroke-dasharray="12 10"/>
      <circle cx="305" cy="115" r="11" fill="#d7f3f9"/><circle cx="58" cy="222" r="8" fill="#d7f3f9"/>
    ''',
    "search": '''
      <rect x="66" y="62" width="190" height="236" rx="12" fill="url(#glass)" stroke="#d7f3f9" stroke-width="4"/>
      <path d="M92 103h137M92 128h108M92 153h128M92 238h92" stroke="#d7f3f9" stroke-width="4" opacity=".6"/>
      <circle cx="219" cy="212" r="64" fill="#164b60" stroke="#d7f3f9" stroke-width="7"/>
      <circle cx="219" cy="212" r="34" fill="none" stroke="#8ed6e6" stroke-width="4"/>
      <path d="m265 258 69 69" stroke="#d7f3f9" stroke-width="18" stroke-linecap="round"/>
    ''',
    "draft": '''
      <path d="M89 45h162l43 44v224H89Z" fill="url(#glass)" stroke="#d7f3f9" stroke-width="4" stroke-linejoin="round"/>
      <path d="M251 45v44h43M113 121h136M113 145h106M113 275h149" fill="none" stroke="#d7f3f9" stroke-width="4" opacity=".65"/>
      <circle cx="176" cy="211" r="37" fill="none" stroke="#d7f3f9" stroke-width="4"/>
      <circle cx="176" cy="211" r="16" fill="none" stroke="#8ed6e6" stroke-width="4"/>
      <path d="M176 162v98m-49-49h98" stroke="#8ed6e6" stroke-width="2" stroke-dasharray="5 6"/>
    ''',
    "review": '''
      <rect x="76" y="55" width="208" height="252" rx="13" fill="url(#glass)" stroke="#d7f3f9" stroke-width="4"/>
      <path d="M103 112h150M103 138h124M103 234h146M103 260h117" stroke="#d7f3f9" stroke-width="4" opacity=".65"/>
      <circle cx="180" cy="185" r="43" fill="#174c61" stroke="#d7f3f9" stroke-width="4"/>
      <path d="m158 184 15 16 30-34" fill="none" stroke="#d7f3f9" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
    ''',
    "filing": '''
      <path d="M50 125h98l25 24h138v151H50Z" fill="url(#glass)" stroke="#d7f3f9" stroke-width="4" stroke-linejoin="round"/>
      <path d="M90 74h174v75H90Z" fill="#1b6177" stroke="#d7f3f9" stroke-width="4"/>
      <path d="M116 99h120M116 120h88" stroke="#d7f3f9" stroke-width="4" opacity=".7"/>
      <path d="M81 192h200M81 224h200M81 256h150" stroke="#d7f3f9" stroke-width="4" opacity=".58"/>
    ''',
}


def render_thumbnail(title: str, category: str, description: str = "") -> str:
    theme = theme_for(title + " " + description)
    digest = hashlib.sha256((category + title).encode("utf-8")).digest()
    dark, middle, accent = PALETTES[digest[0] % len(PALETTES)]
    offset = 24 + digest[1] % 80
    motif = MOTIFS[theme]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600" role="img" aria-label="특허 칼럼 주제 일러스트">
<defs>
  <linearGradient id="bg" x2="1" y2="1"><stop stop-color="{dark}"/><stop offset="1" stop-color="{middle}"/></linearGradient>
  <linearGradient id="glass" x2="1" y2="1"><stop stop-color="{accent}" stop-opacity=".55"/><stop offset="1" stop-color="{accent}" stop-opacity=".08"/></linearGradient>
  <pattern id="grid" width="44" height="44" patternUnits="userSpaceOnUse"><path d="M44 0H0V44" fill="none" stroke="#d7f3f9" stroke-opacity=".12" stroke-width="1"/></pattern>
</defs>
<rect width="1200" height="600" fill="url(#bg)"/>
<rect width="1200" height="600" fill="url(#grid)"/>
<circle cx="{offset + 850}" cy="100" r="260" fill="{accent}" opacity=".08"/>
<path d="M690 0C620 175 667 405 790 600" fill="none" stroke="#d7f3f9" stroke-opacity=".14" stroke-width="2"/>
<g transform="translate(670 117)" stroke-linejoin="round">{motif}</g>
<path d="M720 510h415" stroke="#d7f3f9" stroke-opacity=".35" stroke-width="2"/>
<circle cx="719" cy="510" r="5" fill="{accent}"/>
</svg>
'''


def create_thumbnail(slug: str, title: str, category: str, description: str = "") -> str:
    if not slug.startswith("daily-") or not all(char.isascii() and (char.isalnum() or char == "-") for char in slug):
        raise ValueError("Invalid daily column slug")
    target = ASSETS / f"{slug}-thumb.svg"
    target.write_text(render_thumbnail(title, category, description), encoding="utf-8")
    return f"assets/{target.name}"


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("Usage: make_thumbnail.py <daily-slug> <title> <category>")
    print(create_thumbnail(sys.argv[1], sys.argv[2], sys.argv[3]))
