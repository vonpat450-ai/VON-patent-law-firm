"""Keep search metadata and structured data consistent across generated pages."""

from __future__ import annotations

from html import escape
import json
from pathlib import Path
import re

from build_column import read_article


DIST = Path(__file__).resolve().parents[1] / "dist"
BASE = "https://vonpatglobalpt.net"
SITE_NAME = "특허법인 본"
PAGES = {
    "index": (
        "국내·해외 특허출원 상담 | 특허법인 본",
        "특허법인 본은 국내 특허출원·등록, 우선심사, 해외 특허출원과 PCT 국제출원을 상담합니다. 기술과 사업 일정에 맞는 권리 확보 방향을 살펴보세요.",
        "assets/home-hero-01.webp",
    ),
    "process": (
        "특허등록절차와 국내 특허출원 | 특허법인 본",
        "국내 특허등록절차를 발명 상담, 선행기술 검토, 명세서 작성, 출원, 심사, 등록 순서로 안내합니다. 단계별 준비 자료와 검토 사항을 확인하세요.",
        "assets/process-hero.webp",
    ),
    "priority": (
        "특허 우선심사 대상·절차 | 특허법인 본",
        "특허 우선심사의 신청 요건과 절차, 일반심사와의 차이를 살펴보세요. 출원 상태와 사업 일정에 맞춰 필요한 증빙과 대응 방향을 검토합니다.",
        "assets/priority-hero.webp",
    ),
    "overseas": (
        "해외 특허출원: 개별국·PCT 비교 | 특허법인 본",
        "해외 특허출원을 준비한다면 개별국 직접출원과 PCT 국제출원의 차이를 비교하세요. 진출 국가, 우선권 일정, 비용 결정 시점을 함께 살펴봅니다.",
        "assets/overseas-hero.webp",
    ),
    "knowledge": (
        "특허지식 칼럼: 국내·해외 특허 | 특허법인 본",
        "국내·해외 특허출원, PCT, 우선심사와 심사 대응에 관한 특허법인 본의 칼럼을 읽어보세요. 기업이 확인할 절차와 판단 기준을 쉽게 정리합니다.",
        "assets/knowledge-hero.webp",
    ),
    "contact": (
        "국내·해외 특허 상담 신청 | 특허법인 본",
        "국내·해외 특허출원과 우선심사 상담을 신청하세요. 현재 진행 단계, 진출 국가와 문의 내용을 남기면 검토할 사항과 다음 절차를 안내합니다.",
        "assets/von-standard-logo.png",
    ),
}


def schema_script(value: dict) -> str:
    data = json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/ld+json">{data}</script>'


def update_page(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    stem = path.stem
    if stem in PAGES:
        title, description, image = PAGES[stem]
        html, count = re.subn(r"<title>.*?</title>", f"<title>{escape(title)}</title>", html, count=1)
        if count != 1:
            raise ValueError(f"{path.name}: missing title")
        html, count = re.subn(
            r'<meta name="description" content="[^"]*">',
            f'<meta name="description" content="{escape(description, quote=True)}">',
            html,
            count=1,
        )
        if count != 1:
            raise ValueError(f"{path.name}: missing description")
        published = None
    elif stem.startswith("column-"):
        metadata, lines = read_article(DIST / "articles" / f"{stem.removeprefix('column-')}.md")
        title = f"{lines[0][2:].strip()} | {SITE_NAME}"
        description = metadata.get("description", lines[1][3:].strip())
        image = metadata.get("thumbnail") or metadata.get("hero") or "assets/knowledge-hero.webp"
        published = metadata["published"]
    else:
        return

    canonical = BASE + ("/" if stem == "index" else f"/{stem}")
    image_url = f"{BASE}/{image}"
    tags = [
        f'<link rel="canonical" href="{canonical}">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        '<meta property="og:locale" content="ko_KR">',
        f'<meta property="og:type" content="{"article" if published else "website"}">',
        f'<meta property="og:title" content="{escape(title, quote=True)}">',
        f'<meta property="og:description" content="{escape(description, quote=True)}">',
        f'<meta property="og:url" content="{canonical}">',
        f'<meta property="og:image" content="{image_url}">',
        '<meta name="twitter:card" content="summary_large_image">',
    ]
    if stem == "index":
        tags.append(schema_script({
            "@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME,
            "alternateName": "VON 특허법인 본", "url": f"{BASE}/",
        }))
        tags.append(schema_script({
            "@context": "https://schema.org", "@type": "LegalService", "name": SITE_NAME,
            "url": f"{BASE}/", "image": f"{BASE}/assets/von-standard-logo.png",
            "telephone": "+82-2-6494-0524", "email": "vonpat450@gmail.com",
            "address": {"@type": "PostalAddress", "streetAddress": "테헤란로70길 14-8 세왕개발빌딩 8층", "addressLocality": "강남구", "addressRegion": "서울", "addressCountry": "KR"},
        }))
    else:
        parent = "특허지식" if published else "홈"
        parent_url = f"{BASE}/knowledge" if published else f"{BASE}/"
        tags.append(schema_script({
            "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "홈", "item": f"{BASE}/"},
                *([{"@type": "ListItem", "position": 2, "name": parent, "item": parent_url}] if published else []),
                {"@type": "ListItem", "position": 3 if published else 2, "name": title.removesuffix(f" | {SITE_NAME}"), "item": canonical},
            ],
        }))
    if published:
        tags.append(schema_script({
            "@context": "https://schema.org", "@type": "Article", "headline": title.removesuffix(f" | {SITE_NAME}"),
            "description": description, "datePublished": published, "inLanguage": "ko-KR",
            "image": image_url, "mainEntityOfPage": canonical,
            "publisher": {"@type": "Organization", "name": SITE_NAME, "url": f"{BASE}/"},
        }))
    block = "<!-- SEO_METADATA_START -->\n" + "\n".join(tags) + "\n<!-- SEO_METADATA_END -->"
    html = re.sub(r"<!-- SEO_METADATA_START -->[\s\S]*?<!-- SEO_METADATA_END -->", "", html)
    if "</head>" not in html:
        raise ValueError(f"{path.name}: missing head")
    html = html.replace("</head>", f"{block}\n</head>", 1)
    path.write_text(html, encoding="utf-8")


def main() -> None:
    for path in sorted(DIST.glob("*.html")):
        update_page(path)
    print("Updated SEO metadata on service and article pages")


if __name__ == "__main__":
    main()
