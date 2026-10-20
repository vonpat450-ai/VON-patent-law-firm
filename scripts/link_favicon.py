"""Add the shared favicon links to every published HTML page."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINKS = (
    '<link rel="icon" type="image/svg+xml" href="assets/favicon.svg?v=1">'
    '<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png?v=1">'
    '<link rel="shortcut icon" href="assets/favicon.ico?v=1">'
    '<link rel="apple-touch-icon" sizes="180x180" href="assets/favicon-180.png?v=1">'
)

for path in (ROOT / "dist").glob("*.html"):
    html = path.read_text(encoding="utf-8")
    if 'rel="icon"' in html:
        continue
    needle = '<meta name="theme-color" content="#102b34">'
    if needle not in html:
        needle = '<meta charset="utf-8">'
    html = html.replace(needle, needle + LINKS, 1)
    path.write_text(html, encoding="utf-8")
