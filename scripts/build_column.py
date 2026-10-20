"""Render the supplied PCT column Markdown as a static site page."""

from html import escape
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1] / "dist"
SOURCE = ROOT / "articles" / "pct-country-strategy.md"
TARGET = ROOT / "column-pct-country-strategy.html"
lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
title = lines[0].removeprefix("# ").strip()
subtitle = lines[1].removeprefix("## ").strip()


def inline(value: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", lambda match: f"<strong>{match.group(1)}</strong>", escape(value))


blocks = []
sections = []
paragraph = []
bullets = []


def flush_paragraph() -> None:
    if paragraph:
        value = " ".join(paragraph)
        emphasis = value.startswith("**") and value.endswith("**")
        blocks.append(f'<p class="column-emphasis">{inline(value)}</p>' if emphasis else f"<p>{inline(value)}</p>")
        paragraph.clear()


def flush_bullets() -> None:
    if bullets:
        blocks.append('<ul class="column-list">' + "".join(f"<li>{inline(value)}</li>" for value in bullets) + "</ul>")
        bullets.clear()


for line in lines[2:]:
    value = line.strip()
    if not value:
        flush_paragraph()
        flush_bullets()
    elif value.startswith("## "):
        flush_paragraph()
        flush_bullets()
        heading = value[3:]
        section_id = f"section-{len(sections) + 1}"
        sections.append((section_id, heading))
        blocks.append(f'<h2 id="{section_id}">{escape(heading)}</h2>')
    elif value.startswith("- "):
        flush_paragraph()
        bullets.append(value[2:])
    else:
        flush_bullets()
        paragraph.append(value)
flush_paragraph()
flush_bullets()

toc = "".join(f'<li><a href="#{section_id}">{escape(heading)}</a></li>' for section_id, heading in sections)
body = "\n".join(blocks)
document = f'''<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#102b34">
  <meta name="description" content="PCT 출원 후 해외특허를 확보할 국가를 선택할 때 시장, 생산지, 경쟁사, 비용을 검토하는 방법을 살펴봅니다.">
  <title>{escape(title)} | 특허법인 본</title>
  <link rel="stylesheet" href="style.css?v=pct-column-20261020">
</head>
<body data-page="column">
  <div id="app"></div>
  <template id="column-content">
    <main>
      <section class="column-hero">
        <div class="container">
          <nav class="breadcrumb" aria-label="현재 위치"><a href="index.html">⌂</a><span>›</span><a href="knowledge.html">특허지식</a><span>›</span><span>칼럼</span></nav>
          <span class="column-kicker">VON PATENT INSIGHT · 해외특허</span>
          <h1>{escape(title)}</h1>
          <p>{escape(subtitle)}</p>
        </div>
      </section>
      <section class="column-section">
        <div class="container column-layout">
          <aside class="column-sidebar" aria-label="칼럼 목차">
            <details class="column-toc" open>
              <summary>이 글의 목차</summary>
              <ol>{toc}</ol>
            </details>
            <a class="column-sidebar-link" href="overseas.html">해외특허등록 살펴보기 <span aria-hidden="true">↗</span></a>
          </aside>
          <article class="column-body">{body}
            <section class="column-sources" aria-labelledby="column-sources-title">
              <h2 id="column-sources-title">참고 자료</h2>
              <ul>
                <li><a href="https://www.wipo.int/en/web/pct-system/article-9" target="_blank" rel="noopener noreferrer">WIPO PCT Newsletter, September 2026 — SME Support Series ↗</a></li>
                <li><a href="https://www.wipo.int/en/web/pct-system/texts/time_limits" target="_blank" rel="noopener noreferrer">WIPO 국가·지역단계 진입기한표 ↗</a></li>
              </ul>
            </section>
          </article>
        </div>
      </section>
      <section class="column-bottom">
        <div class="container column-bottom-inner">
          <div><span>해외출원 상담</span><h2>어느 국가에서 권리를 확보해야 할지<br>함께 검토해 보세요.</h2><p>진출 시장과 사업 일정, 현재 출원 상황을 알려주시면 상담 방향을 안내해 드립니다.</p></div>
          <a class="btn btn-primary" href="contact.html">상담 신청 <span aria-hidden="true">→</span></a>
        </div>
      </section>
      <div class="container column-back"><a href="knowledge.html">← 특허지식 목록으로</a></div>
    </main>
  </template>
  <script src="app.js?v=pct-column-20261020" defer></script>
</body>
</html>
'''
TARGET.write_text(document, encoding="utf-8")
print(f"Wrote {TARGET} with {len(sections)} sections")
