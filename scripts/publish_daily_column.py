"""Create one source-constrained patent column per Korea calendar day.

Only GEMINI_API_KEY is read from the environment. No third-party Python packages
are needed, and neither the key nor the model's unvalidated response is logged.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib import error, request
from zoneinfo import ZoneInfo

from build_column import read_article
from make_thumbnail import create_thumbnail, render_thumbnail


ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "dist" / "articles"
MODELS = ("gemini-3.5-flash", "gemini-3.5-flash-lite")
KST = ZoneInfo("Asia/Seoul")

# The publisher supplies its own official sources. Gemini cannot create citations.
# Rotate the reader question, not a changing legal deadline or fee.
TOPICS = (
    ("국내특허", "특허출원 전에 아이디어를 공개해도 될까요?", "공개 전 점검할 항목과 선행기술 조사", "https://www.kipo.go.kr/ko/kpoContentView.do?menuCd=SCD0200111", "지식재산처, 특허의 이해", "process.html", "특허등록절차 살펴보기"),
    ("해외특허", "PCT 국제출원과 해외 등록은 어떻게 다른가요?", "국가단계 진입 전 확인할 사항", "https://www.wipo.int/en/web/pct-system/faqs/faqs", "WIPO, PCT 자주 묻는 질문", "overseas.html", "해외특허등록 살펴보기"),
    ("국내특허", "특허 명세서에서 왜 기술 설명이 중요한가요?", "발명의 핵심을 정리하는 관점", "https://www.kipo.go.kr/ko/kpoContentView.do?menuCd=SCD0200111", "지식재산처, 특허의 이해", "process.html", "특허등록절차 살펴보기"),
    ("해외특허", "해외 출원 국가는 무엇을 기준으로 고를까요?", "시장과 사업 계획을 함께 살펴보기", "https://www.wipo.int/en/web/pct-system/faqs/faqs", "WIPO, PCT 자주 묻는 질문", "overseas.html", "해외특허등록 살펴보기"),
    ("국내특허", "특허 심사에서는 무엇을 확인하나요?", "출원부터 결정까지의 흐름", "https://www.kipo.go.kr/ko/kpoContentView.do?menuCd=SCD0200111", "지식재산처, 특허의 이해", "process.html", "특허등록절차 살펴보기"),
    ("해외특허", "개별국 직접출원과 PCT 중 무엇을 검토할까요?", "진출 국가가 정해졌는지부터 판단하기", "https://www.wipo.int/en/web/pct-system/faqs/faqs", "WIPO, PCT 자주 묻는 질문", "overseas.html", "해외특허등록 살펴보기"),
    ("국내특허", "선행기술 조사는 왜 출원 전에 할까요?", "기술의 차이와 권리 범위 살피기", "https://www.wipo.int/en/web/patents/protection", "WIPO, How to Protect Inventions through Patents", "process.html", "특허등록절차 살펴보기"),
    ("해외특허", "PCT 국가단계에 들어가기 전 무엇을 준비할까요?", "번역과 현지 절차를 미리 확인하기", "https://www.wipo.int/en/web/pct-system/faqs/faqs", "WIPO, PCT 자주 묻는 질문", "overseas.html", "해외특허등록 살펴보기"),
    ("국내특허", "특허를 받을 수 있는 발명인지 어떻게 살펴볼까요?", "신규성·진보성·산업상 이용가능성의 기본", "https://www.kipo.go.kr/ko/kpoContentView.do?menuCd=SCD0200111", "지식재산처, 특허의 이해", "process.html", "특허등록절차 살펴보기"),
    ("해외특허", "국제조사보고서는 어떻게 활용할까요?", "국가단계 진입 전략의 참고 자료", "https://www.wipo.int/en/web/pct-system/faqs/faqs", "WIPO, PCT 자주 묻는 질문", "overseas.html", "해외특허등록 살펴보기"),
)

VERIFIED_FACTS = {
    "https://www.kipo.go.kr/ko/kpoContentView.do?menuCd=SCD0200111": (
        "지식재산처는 특허 심사 흐름을 방식심사, 출원공개, 실체심사, "
        "특허결정, 등록공고로 설명한다. 실체심사에서는 발명 내용과 선행기술을 살펴본다. "
        "신규성, 진보성, 산업상 이용가능성은 특허요건의 기본 개념이다. "
        "출원만으로 특허권이 생기는 것은 아니며 설정등록이 필요하다. "
        "출원 전 공개가 있었어도 공지예외 제도 적용 가능성을 사안별로 검토할 수 있다."
    ),
    "https://www.wipo.int/en/web/pct-system/faqs/faqs": (
        "특허권은 원칙적으로 지역별 권리이다. PCT 국제출원은 그 자체로 여러 나라의 "
        "등록 특허를 만들어 주지 않는다. 권리를 원하는 국가나 지역의 단계로 진입해 "
        "해당 관청의 절차를 거치며, 최종 등록 여부는 해당 관청이 결정한다. "
        "국가단계에는 관납료·번역·현지 대리인 등 추가 준비가 필요할 수 있다."
    ),
    "https://www.wipo.int/en/web/patents/protection": (
        "특허를 받으려면 국가 또는 지역 특허청에 출원한다. 일반적인 실체심사에서는 "
        "특허 대상성, 신규성, 진보성, 산업상 이용가능성과 충분한 공개를 살펴본다."
    ),
}


def existing_titles() -> list[str]:
    return [read_article(path)[1][0][2:].strip() for path in sorted(ARTICLES.glob("*.md"))]


def choose_topic(today: str) -> tuple[str, ...]:
    ordinal = datetime.fromisoformat(today).date().toordinal()
    return TOPICS[ordinal % len(TOPICS)]


def prompt_for(today: str, topic: tuple[str, ...], titles: list[str]) -> str:
    category, question, angle, source_url, source_label, _, _ = topic
    return f"""당신은 특허법인 홈페이지의 한국어 칼럼 편집자입니다. 오늘은 {today}입니다.
이번 글의 분야: {category}
독자 질문: {question}
글의 관점: {angle}
검증된 참고 자료: {source_label} — {source_url}
이 자동화에 미리 확인해 둔 자료의 핵심 사실: {VERIFIED_FACTS[source_url]}

위 핵심 사실에서 벗어나는 구체적 법률 사실을 추측하지 마세요. 확인하지 않은 내용을 출처가 뒷받침한다고 주장하지 마세요.
구체적인 법조문 번호, 법정 기한, 수수료, 통계, 심사 소요 기간, 국가별 예외를 만들거나 단정하지 마세요.
개별 사건에 따라 달라지는 조건은 확인이 필요하다고 적으세요. 성공률을 보장하거나 광고성 문구를 넣지 마세요.
실제 의뢰인, 개인 정보, 가상의 판례, 출처 없는 인용문을 쓰지 마세요.
기존 칼럼과 같은 제목이나 같은 논지의 반복을 피하세요. 기존 제목: {json.dumps(titles[-80:], ensure_ascii=False)}

읽기 쉬운 설명형 칼럼을 한국어 1600~2800자 정도로 작성하세요. 너무 짧게 요약하지 마세요.
오늘 칼럼부터 모든 글은 같은 편집 구조를 사용합니다. body의 순서를 반드시 지키세요.
1. 맨 위에 :::takeaway 블록: 첫 줄은 독자에게 도움이 되는 한 문장 제목, 다음 줄은 2~3문장의 핵심 설명, 끝은 ::: 한 줄.
2. 두 개의 짧은 도입 문단.
3. 정확히 다섯 개의 번호별 섹션. 제목 형식은 '## 1. 짧은 분류 | 독자의 질문 또는 행동형 제목'입니다. 번호는 1~5 순서입니다.
4. 첫 섹션의 설명 문단 뒤에 :::quote 블록. 짧은 핵심 문장 한 개를 넣고 :::로 닫으세요.
5. 둘째 섹션에 :::cards 블록. '- 카드 제목 | 한 문장 설명' 형식으로 세 항목을 넣고 :::로 닫으세요.
6. 셋째 섹션에 :::steps 블록. '- 단계 제목 | 한 문장 설명' 형식으로 세 항목을 넣고 :::로 닫으세요.
7. 넷째 섹션에 :::checklist 블록. '- 점검할 질문' 형식으로 네 항목을 넣고 :::로 닫으세요.
8. 다섯째 섹션에는 개별 상황에 따른 결론과 주의점을 두 문단으로 쓰세요.
각 구역의 문단은 구체적이고 서로 반복되지 않아야 합니다. 카드와 목록은 실제 독자가 점검할 수 있는 내용으로 적으세요.
JSON 객체만 반환하세요. 필드는 title, subtitle, description, body 네 개의 문자열입니다.
title은 45자 이내, subtitle은 55자 이내, description은 120자 이내입니다.
body는 위의 구조와 지정한 ::: 블록 및 Markdown 소제목으로 씁니다.
본문에는 H1 제목이나 출처 링크를 넣지 마세요. 출처는 별도 참고 자료에 자동으로 붙습니다.
"""


def generate(prompt: str, api_key: str) -> dict[str, str]:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.55,
            "maxOutputTokens": 8192,
            "responseMimeType": "application/json",
        },
    }
    data = None
    for index, model in enumerate((*MODELS[:1], *MODELS)):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        req = request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=120) as response:
                data = json.load(response)
            break
        except error.HTTPError as exc:
            # Google's response can contain details; do not print it or request headers.
            if exc.code not in {500, 502, 503, 504} or index == 2:
                raise RuntimeError(f"Gemini API returned HTTP {exc.code}") from exc
            print(f"{model} is temporarily unavailable; trying another free-tier request")
            time.sleep(5)
        except error.URLError as exc:
            raise RuntimeError("Could not reach Gemini API") from exc
    try:
        candidate = data["candidates"][0]
        if candidate.get("finishReason") != "STOP":
            raise ValueError("generation did not finish normally")
        content = "".join(part.get("text", "") for part in candidate["content"]["parts"])
        return json.loads(content)
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise RuntimeError("Gemini did not return a complete JSON article") from exc


def validate_article(article: dict[str, str], titles: list[str]) -> dict[str, str]:
    if not isinstance(article, dict):
        raise ValueError("Article must be a JSON object")
    for key, limit in (("title", 45), ("subtitle", 55), ("description", 120)):
        value = article.get(key)
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > limit or "\n" in value:
            raise ValueError(f"Invalid {key}")
        article[key] = value.strip()
    body = article.get("body")
    if not isinstance(body, str) or not 1000 <= len(body.strip()) <= 5500:
        raise ValueError(f"Body length is outside the allowed range: {len(body) if isinstance(body, str) else 0}")
    headings = re.findall(r"^## (\d+)\. [^|\n]+ \| [^\n]+$", body, flags=re.MULTILINE)
    if headings != ["1", "2", "3", "4", "5"]:
        raise ValueError("Body must contain five numbered insight sections")
    for block in ("takeaway", "quote", "cards", "steps", "checklist"):
        if body.count(f":::{block}") != 1:
            raise ValueError(f"Body must contain one {block} block")
    if re.search(r"(?m)^# (?!#)|https?://|\[[^]]+\]\([^)]+\)|<script|</", body, re.I):
        raise ValueError("Body contains unexpected heading, link or markup")
    if article["title"].casefold() in {title.casefold() for title in titles}:
        raise ValueError("A column with this title already exists")
    # The same parser creates the public page; reject malformed custom blocks now.
    from build_column import render_insight_body
    render_insight_body(["# " + article["title"], "## " + article["subtitle"], *body.splitlines()])
    article["body"] = body.strip()
    return article


def serialize(today: str, topic: tuple[str, ...], article: dict[str, str], thumbnail: str = "") -> str:
    category, _, _, source_url, source_label, related_url, related_label = topic
    thumbnail_line = f"thumbnail: {thumbnail}\n" if thumbnail else ""
    # Single-line metadata fields are checked before serialization.
    return (
        f"---\npublished: {today}\ncategory: {category}\nlayout: insight\n"
        f"tags: {category} · 특허 전략\nhero: assets/pct-column-hero.webp\n"
        f"{thumbnail_line}"
        f"description: {article['description']}\n"
        f"related_url: {related_url}\nrelated_label: {related_label}\n"
        f"source_1_label: {source_label}\nsource_1_url: {source_url}\n"
        f"---\n# {article['title']}\n## {article['subtitle']}\n\n{article['body']}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Generate and validate without writing a file")
    args = parser.parse_args()
    today = datetime.now(KST).date().isoformat()
    target = ARTICLES / f"daily-{today}.md"
    if target.exists():
        print(f"Today's column already exists: {target.name}")
        return 0
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY secret is missing")
    titles = existing_titles()
    topic = choose_topic(today)
    article = validate_article(generate(prompt_for(today, topic, titles), api_key), titles)
    render_thumbnail(article["title"], topic[0], article["description"])
    if args.dry_run:
        print(f"Dry run passed: {article['title']} ({len(article['body'])} characters)")
        return 0
    thumbnail = create_thumbnail(f"daily-{today}", article["title"], topic[0], article["description"])
    document = serialize(today, topic, article, thumbnail)
    target.write_text(document, encoding="utf-8")
    read_article(target)  # Confirm the site's real renderer accepts the new source.
    print(f"Created {target.name}: {article['title']}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, ValueError) as exc:
        print(f"Daily column failed: {exc}", file=sys.stderr)
        sys.exit(1)
