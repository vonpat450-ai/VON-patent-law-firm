"""Raster fallbacks for the V + orbit SVG favicon."""

from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "dist" / "assets"
SCALE = 16
SIZE = 64 * SCALE


def p(*coords):
    return tuple(round(n * SCALE) for n in coords)


image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)
draw.rounded_rectangle((0, 0, SIZE - 1, SIZE - 1), radius=15 * SCALE, fill="#102b34")
draw.line([p(15, 18), p(31.5, 48), p(49, 18)], fill="white", width=7 * SCALE, joint="curve")
for x, y in [(15, 18), (31.5, 48), (49, 18)]:
    r = 3.5 * SCALE
    draw.ellipse((x * SCALE - r, y * SCALE - r, x * SCALE + r, y * SCALE + r), fill="white")
draw.arc(p(16, 8, 58, 56), start=277, end=360, fill="#1498d0", width=4 * SCALE)
draw.ellipse(p(36.6, 6.1, 43.4, 12.9), fill="#1498d0")

for size in (16, 32, 48, 180, 192):
    image.resize((size, size), Image.Resampling.LANCZOS).save(ASSETS / f"favicon-{size}.png")
image.save(ASSETS / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
