"""Build raster fallbacks for the selected global compass favicon."""

from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "dist" / "assets"
CONCEPT = ROOT / "design" / "favicon-concepts" / "05-global-compass.svg"
SCALE = 16
SIZE = 64 * SCALE


def p(*coords):
    return tuple(round(n * SCALE) for n in coords)


image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)
draw.rounded_rectangle((0, 0, SIZE - 1, SIZE - 1), radius=15 * SCALE, fill="#102b34")
draw.ellipse(p(10, 10, 54, 54), outline="#1498d0", width=5 * SCALE)
draw.polygon([p(22, 42), p(30, 22), p(43, 15), p(36, 28)], fill="white")
draw.polygon([p(30, 22), p(36, 28), p(43, 15)], fill="#1498d0")
draw.ellipse(p(29, 29, 35, 35), fill="#102b34")

ASSETS.joinpath("favicon.svg").write_bytes(CONCEPT.read_bytes())

for size in (16, 32, 48, 180, 192):
    image.resize((size, size), Image.Resampling.LANCZOS).save(ASSETS / f"favicon-{size}.png")
image.save(ASSETS / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
