"""Add the shared favicon links to every published HTML page."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
VERSION = 2
LINKS = (
    f'<link rel="icon" type="image/svg+xml" href="assets/favicon.svg?v={VERSION}">'
    f'<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png?v={VERSION}">'
    f'<link rel="shortcut icon" href="assets/favicon.ico?v={VERSION}">'
    f'<link rel="apple-touch-icon" sizes="180x180" href="assets/favicon-180.png?v={VERSION}">'
)

for path in (ROOT / "dist").glob("*.html"):
    html = path.read_text(encoding="utf-8")
    if 'rel="icon"' in html:
        html = re.sub(r'(href="assets/favicon[^"?]+\?v=)\d+', rf'\g<1>{VERSION}', html)
        path.write_text(html, encoding="utf-8")
        continue
    needle = '<meta name="theme-color" content="#102b34">'
    if needle not in html:
        needle = '<meta charset="utf-8">'
    html = html.replace(needle, needle + LINKS, 1)
    path.write_text(html, encoding="utf-8")
