"""Build all Markdown columns and a listing for the home and knowledge pages."""

from __future__ import annotations

from datetime import date
from html import escape
import hashlib
import json
from pathlib import Path
import re

DIST = Path(__file__).resolve().parents[1] / "dist"
ASSET_RE = re.compile(r"^assets/[a-zA-Z0-9._-]+$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def read_article(path: Path) -> tuple[dict[str, str], list[str]]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    metadata: dict[str, str] = {}
    if lines and lines[0].strip() == "---":
        try:
            end = lines.index("---", 1)
        except ValueError as error:
            raise ValueError(f"{path.name}: metadata is not closed") from error
        for line in lines[1:end]:
            if line.strip():
                if ":" not in line:
                    raise ValueError(f"{path.name}: invalid metadata line")
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()
        lines = lines[end + 1:]
    while lines and not lines[0].strip():
        lines.pop(0)
    if len(lines) < 2 or not lines[0].startswith("# ") or not lines[1].startswith("## "):
        raise ValueError(f"{path.name}: start with # title and ## subtitle")
    if not SLUG_RE.fullmatch(path.stem):
        raise ValueError(f"{path.name}: use a lowercase hyphenated filename")
    try:
        date.fromisoformat(metadata.get("published", ""))
    except ValueError as error:
        raise ValueError(f"{path.name}: published must be YYYY-MM-DD") from error
    for key in ("thumbnail", "hero"):
        value = metadata.get(key, "")
        if value and (not ASSET_RE.fullmatch(value) or not (DIST / value).is_file()):
            raise ValueError(f"{path.name}: {key} must name an existing dist/assets file")
    related_url = metadata.get("related_url", "")
    if related_url and (
        not re.fullmatch(r"[a-z-]+\.html", related_url)
        or not (DIST / related_url).is_file()
    ):
        raise ValueError(f"{path.name}: related_url must name an existing local HTML page")
    return metadata, lines


def inline(value: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", lambda match: f"<strong>{match.group(1)}</strong>", escape(value))


def render_body(lines: list[str]) -> tuple[str, str]:
    blocks: list[str] = []
    sections: list[tuple[str, str]] = []
    paragraph: list[str] = []
    bullets: list[str] = []

    def flush() -> None:
        if paragraph:
            value = " ".join(paragraph)
            css = ' class="column-emphasis"' if value.startswith("**") and value.endswith("**") else ""
            blocks.append(f"<p{css}>{inline(value)}</p>")
            paragraph.clear()
        if bullets:
            blocks.append('<ul class="column-list">' + "".join(f"<li>{inline(value)}</li>" for value in bullets) + "</ul>")
            bullets.clear()

    for line in lines[2:]:
        value = line.strip()
        if not value:
            flush()
        elif value.startswith("## "):
            flush()
            heading = value[3:]
            section_id = f"section-{len(sections) + 1}"
            sections.append((section_id, heading))
            blocks.append(f'<h2 id="{section_id}">{escape(heading)}</h2>')
        elif value.startswith("- "):
            if paragraph:
                flush()
            bullets.append(value[2:])
        else:
            if bullets:
                flush()
            paragraph.append(value)
    flush()
    toc = "".join(
        f'<li><a href="#{section_id}">{escape(re.sub(r"^\d+\.\s*", "", heading))}</a></li>'
        for section_id, heading in sections
    )
    return "\n".join(blocks), toc


def render_insight_body(lines: list[str]) -> tuple[str, str]:
    """Render the editorial column format used by current and future daily posts."""
    blocks: list[str] = []
    toc: list[str] = []
    paragraph: list[str] = []
    section_open = False
    directive: str | None = None
    directive_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append(f'<p>{inline(" ".join(paragraph))}</p>')
            paragraph.clear()

    def flush_directive() -> None:
        nonlocal directive
        if directive is None:
            return
        values = [value.strip() for value in directive_lines if value.strip()]
        if directive == "takeaway":
            if len(values) < 2:
                raise ValueError("takeaway needs a title and explanation")
            blocks.append('<div class="insight-takeaway"><span>먼저 알아둘 점</span>'
                          f'<h2>{inline(values[0])}</h2><p>{inline(" ".join(values[1:]))}</p></div>')
        elif directive == "quote":
            blocks.append(f'<blockquote class="insight-quote">{inline(" ".join(values))}</blockquote>')
        elif directive in {"cards", "steps"}:
            items = []
            for index, value in enumerate(values, 1):
                parts = [part.strip() for part in value.removeprefix("- ").split(" | ", 1)]
                if len(parts) != 2 or not all(parts):
                    raise ValueError(f"{directive} items need 'title | explanation'")
                items.append(f'<li><span>{index:02d}</span><div><h4>{inline(parts[0])}</h4><p>{inline(parts[1])}</p></div></li>')
            blocks.append(f'<ol class="insight-{directive}">' + "".join(items) + "</ol>")
        elif directive == "checklist":
            items = "".join(f'<li>{inline(value.removeprefix("- "))}</li>' for value in values)
            blocks.append('<div class="insight-checklist"><h4>진행 전 확인 항목</h4><ul>' + items + '</ul></div>')
        else:
            raise ValueError(f"Unknown insight block: {directive}")
        directive_lines.clear()
        directive = None

    for line in lines[2:]:
        value = line.strip()
        if value.startswith(":::"):
            flush_paragraph()
            if directive is None:
                directive = value[3:]
                if directive not in {"takeaway", "quote", "cards", "steps", "checklist"}:
                    raise ValueError(f"Unknown insight block: {directive}")
            elif value == ":::":
                flush_directive()
            else:
                raise ValueError("Close the insight block before opening another")
        elif directive is not None:
            directive_lines.append(value)
        elif value.startswith("## "):
            flush_paragraph()
            if section_open:
                blocks.append("</section>")
            match = re.fullmatch(r"(\d+)\. ([^|]+) \| (.+)", value[3:])
            if not match:
                raise ValueError("Insight headings need '## 1. label | title'")
            number, label, heading = match.groups()
            section_id = f"section-{len(toc) + 1}"
            toc.append(f'<li><a href="#{section_id}"><span>{int(number):02d}</span>{escape(heading.strip())}</a></li>')
            blocks.append(f'<section class="insight-part" id="{section_id}"><span class="insight-part-label">{int(number):02d} · {escape(label.strip())}</span><h2>{escape(heading.strip())}</h2>')
            section_open = True
        elif not value:
            flush_paragraph()
        else:
            paragraph.append(value)
    if directive is not None:
        raise ValueError("Insight block is not closed")
    flush_paragraph()
    if section_open:
        blocks.append("</section>")
    return "\n".join(blocks), "".join(toc)


def render_guide_body(lines: list[str]) -> tuple[str, str]:
    """Render the evidence-linked 3–4 section format for automated columns."""
    blocks: list[str] = []
    toc: list[str] = []
    paragraph: list[str] = []
    block_name: str | None = None
    block_lines: list[str] = []
    section_open = False

    def linked(value: str) -> str:
        return inline(value).replace("〔1〕", '<a class="source-ref" href="#source-1" aria-label="참고 자료 1">〔1〕</a>')

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append(f'<p>{linked(" ".join(paragraph))}</p>')
            paragraph.clear()

    def flush_block() -> None:
        nonlocal block_name
        values = [item.strip() for item in block_lines if item.strip()]
        if block_name == "takeaway":
            if len(values) < 2:
                raise ValueError("guide takeaway needs a title and answer")
            # The same answer is printed directly below the H1 in the hero.
        elif block_name == "checklist":
            if not 3 <= len(values) <= 5 or any(not value.startswith("- ") for value in values):
                raise ValueError("guide checklist needs 3–5 bullet items")
            items = "".join(f'<li>{linked(value[2:])}</li>' for value in values)
            blocks.append('<div class="insight-checklist"><h4>내 상황 확인 항목</h4><ul>' + items + '</ul></div>')
        else:
            raise ValueError("unknown guide block")
        block_lines.clear()
        block_name = None

    for line in lines[2:]:
        value = line.strip()
        if value.startswith(":::"):
            flush_paragraph()
            if block_name is None and value in {":::takeaway", ":::checklist"}:
                block_name = value[3:]
            elif block_name is not None and value == ":::":
                flush_block()
            else:
                raise ValueError("invalid guide block")
        elif block_name is not None:
            block_lines.append(value)
        elif value.startswith("## "):
            flush_paragraph()
            if section_open:
                blocks.append("</section>")
            heading = value[3:]
            match = re.fullmatch(r"([1-4])\. (.+)", heading)
            if match:
                number, title = match.groups()
                section_id = f"section-{number}"
                toc.append(f'<li><a href="#{section_id}"><span>{int(number):02d}</span>{escape(title)}</a></li>')
                blocks.append(f'<section class="insight-part" id="{section_id}"><span class="insight-part-label">{int(number):02d} · 핵심 질문</span><h2>{escape(title)}</h2>')
            elif heading in {"마무리", "FAQ"}:
                blocks.append(f'<section class="insight-part"><h2>{escape(heading)}</h2>')
            else:
                raise ValueError("invalid guide section heading")
            section_open = True
        elif value.startswith("### "):
            flush_paragraph()
            blocks.append(f'<h3>{escape(value[4:])}</h3>')
        elif not value:
            flush_paragraph()
        else:
            paragraph.append(value)
    if block_name:
        raise ValueError("unclosed guide block")
    flush_paragraph()
    if section_open:
        blocks.append("</section>")
    return "\n".join(blocks), "".join(toc)


def sources_html(metadata: dict[str, str]) -> str:
    links = []
    for number in range(1, 11):
        label = metadata.get(f"source_{number}_label", "")
        url = metadata.get(f"source_{number}_url", "")
        if label and url:
            if not url.startswith("https://"):
                raise ValueError("source URLs must use https")
            note = metadata.get(f"source_{number}_note", "")
            links.append(f'<li id="source-{number}"><a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(label)} ↗</a>{f"<p>{escape(note)}</p>" if note else ""}</li>')
    return ('<section class="column-sources" aria-labelledby="column-sources-title"><h2 id="column-sources-title">참고 자료</h2><ul>' + "".join(links) + "</ul></section>") if links else ""


def render_page(path: Path, metadata: dict[str, str], lines: list[str]) -> dict[str, str]:
    title, subtitle = lines[0][2:].strip(), lines[1][3:].strip()
    category = metadata.get("category", "특허지식")
    description = metadata.get("description", subtitle)
    hero = metadata.get("hero", "assets/knowledge-hero.png")
    layout = metadata.get("layout")
    insight = layout in {"insight", "guide"}
    body, toc = render_guide_body(lines) if layout == "guide" else render_insight_body(lines) if insight else render_body(lines)
    related_url = metadata.get("related_url", "")
    related_label = metadata.get("related_label", "더 알아보기")
    if related_url and not re.fullmatch(r"[a-z-]+\.html", related_url):
        raise ValueError(f"{path.name}: related_url must be a local HTML page")
    related = f'<a class="column-sidebar-link" href="{escape(related_url, quote=True)}">{escape(related_label)} <span aria-hidden="true">↗</span></a>' if related_url else ""
    bottom = '' if insight else '''<section class="column-bottom">
        <div class="container column-bottom-inner">
          <div><span>특허 상담</span><h2>현재 상황에 맞는 특허 전략을<br>함께 검토해 보세요.</h2><p>출원 국가와 기술의 진행 상황을 알려주시면 상담 방향을 안내해 드립니다.</p></div>
          <a class="btn btn-primary" href="contact.html">상담 신청 <span aria-hidden="true">→</span></a>
        </div>
      </section>
      <div class="container column-back"><a href="knowledge.html">← 특허지식 목록으로</a></div>'''
    document = f'''<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#102b34">
  <meta name="description" content="{escape(description, quote=True)}">
  <title>{escape(title)} | 특허법인 본</title>
  <link rel="icon" type="image/svg+xml" href="assets/favicon.svg?v=3">
  <link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png?v=3">
  <link rel="shortcut icon" href="assets/favicon.ico?v=3">
  <link rel="apple-touch-icon" sizes="180x180" href="assets/favicon-180.png?v=3">
  <link rel="stylesheet" href="style.css?v=columns-2">
</head>
<body data-page="column" class="{'column-insight' if insight else ''}">
  <div id="app"></div>
  <template id="column-content">
    <main>
      <section class="column-hero" style="--column-hero-image:url('{hero}')">
        <div class="container">
          <nav class="breadcrumb" aria-label="현재 위치"><a href="index.html">⌂</a><span>›</span><a href="knowledge.html">특허지식</a><span>›</span><span>칼럼</span></nav>
          <span class="column-kicker">VON PATENT INSIGHT · {escape(category)}</span>
          <h1>{escape(title)}</h1>
          <p>{escape(subtitle)}</p>
          {f'<div class="insight-hero-tags">{escape(metadata.get("tags", category))}</div>' if insight else ''}
        </div>
      </section>
      <section class="column-section">
        <div class="container column-layout">
          <aside class="column-sidebar" aria-label="칼럼 목차">
            <details class="column-toc" open><summary>{'이 글에서 살펴볼 내용' if insight else '이 글의 목차'}</summary><ol>{toc}</ol>{'<p class="insight-toc-note">필요한 항목부터 읽어도 좋습니다. 전체 흐름을 이해할 수 있도록 정리했습니다.</p>' if insight else ''}</details>
            {'' if insight else related}
          </aside>
          <article class="column-body">{body}{sources_html(metadata)}</article>
        </div>
      </section>
      {bottom}
    </main>
  </template>
  <script src="app.js?v=columns-2" defer></script>
</body>
</html>
'''
    document = "\n".join(line.rstrip() for line in document.splitlines()) + "\n"
    target = DIST / f"column-{path.stem}.html"
    target.write_text(document, encoding="utf-8")
    print(f"Wrote {target.name}")
    return {"title": title, "subtitle": metadata.get("list_summary", subtitle), "category": category, "published": metadata["published"], "href": target.name, "thumbnail": metadata.get("thumbnail", "")}


def main() -> None:
    listing = [render_page(path, *read_article(path)) for path in sorted((DIST / "articles").glob("*.md"))]
    listing.sort(key=lambda item: (item["published"], item["href"]), reverse=True)
    data = json.dumps(listing, ensure_ascii=False, separators=(",", ":")).replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    listing_script = f"window.VON_ARTICLES={data};\n"
    (DIST / "articles-data.js").write_text(listing_script, encoding="utf-8")
    # A new content hash prevents browsers from reusing yesterday's article list.
    version = hashlib.sha256(listing_script.encode("utf-8")).hexdigest()[:12]
    for name in ("index.html", "knowledge.html"):
        page = DIST / name
        html = page.read_text(encoding="utf-8")
        updated, count = re.subn(r'articles-data\.js(?:\?v=[a-zA-Z0-9-]+)?', f'articles-data.js?v={version}', html)
        if count != 1:
            raise ValueError(f"{name}: expected one article data script")
        page.write_text(updated, encoding="utf-8")
    print(f"Indexed {len(listing)} columns")


if __name__ == "__main__":
    main()
