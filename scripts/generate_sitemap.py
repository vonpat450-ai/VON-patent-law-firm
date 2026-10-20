"""Generate the public sitemap from deployable HTML pages."""

from __future__ import annotations

import subprocess
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
BASE_URL = "https://vonpatglobalpt.net"
EXCLUDED = {"search.html", "404.html"}
NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"


def last_modified(page: Path) -> str:
    paths = [page.relative_to(ROOT), Path("dist/app.js")]
    if page.name == "column-pct-country-strategy.html":
        paths.append(Path("dist/articles/pct-country-strategy.md"))
    result = subprocess.run(
        [
            "git", "-c", f"safe.directory={ROOT.as_posix()}", "log", "-1",
            "--format=%cs", "--", *(p.as_posix() for p in paths),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip() or date.today().isoformat()


def main() -> None:
    pages = sorted(
        (page for page in DIST.glob("*.html") if page.name not in EXCLUDED),
        key=lambda page: (page.name != "index.html", page.name),
    )
    ET.register_namespace("", NAMESPACE)
    root = ET.Element(f"{{{NAMESPACE}}}urlset")
    for page in pages:
        path = "/" if page.name == "index.html" else f"/{page.stem}"
        entry = ET.SubElement(root, f"{{{NAMESPACE}}}url")
        ET.SubElement(entry, f"{{{NAMESPACE}}}loc").text = f"{BASE_URL}{path}"
        ET.SubElement(entry, f"{{{NAMESPACE}}}lastmod").text = last_modified(page)
    ET.indent(root, space="  ")
    output = DIST / "sitemap.xml"
    output.write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n")
    print(f"Generated {output} with {len(pages)} URLs")


if __name__ == "__main__":
    main()
