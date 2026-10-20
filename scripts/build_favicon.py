"""Build browser icon fallbacks from the selected SVG concept."""

from pathlib import Path
from PIL import Image
import fitz

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "dist" / "assets"
CONCEPT = ROOT / "design" / "favicon-concepts" / "02-world-shield.svg"


svg = CONCEPT.read_bytes()
ASSETS.joinpath("favicon.svg").write_bytes(svg)
document = fitz.open(stream=svg, filetype="svg")
pixmap = document[0].get_pixmap(matrix=fitz.Matrix(16, 16), alpha=True)
image = Image.frombytes("RGBA", (pixmap.width, pixmap.height), pixmap.samples)

for size in (16, 32, 48, 180, 192):
    image.resize((size, size), Image.Resampling.LANCZOS).save(ASSETS / f"favicon-{size}.png")
image.save(ASSETS / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
