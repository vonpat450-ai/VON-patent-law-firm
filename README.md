# 특허법인 본 홈페이지

정적 HTML/CSS/JavaScript 사이트입니다. 공개할 파일은 `dist/`에 있습니다.

## Cloudflare Pages 연결

GitHub 저장소의 `main` 브랜치를 Cloudflare Pages에 연결합니다. Framework preset은 `None`, Build command는 비워 두고, Build output directory는 `dist`로 설정합니다. 기본 공개 주소는 `https://vonpatglobalpt.net/`이며, `www.vonpatglobalpt.net`도 같은 Pages 프로젝트에 연결되어 있습니다. 이 사이트에는 npm 빌드가 필요하지 않습니다.

## 상담 이메일

상단과 본문의 상담 버튼은 `contact.html`로 이동합니다. 각 페이지 하단의 간단 입력폼은 이름, 연락처, 이메일, 진행 단계를 같은 탭의 브라우저 저장소에 잠시 보관하고 상담 페이지의 해당 칸에 채웁니다. 주소에는 개인정보를 넣지 않습니다. 상담 페이지에서는 출원 대상을 먼저 선택합니다. 국내 특허를 선택하면 상담 분야를 고른 뒤 현재 진행 단계를 선택할 수 있습니다. 해외 특허를 선택하면 국가명과 선택 사항인 국내 출원·등록 특허번호 입력란이 열리며 국내용 상담 분야와 진행 단계는 제출되지 않습니다. 연락처는 010 휴대폰 번호만 받으며 입력 중 하이픈을 붙이고, 이메일은 도메인까지 검사합니다. 문의 내용과 자료를 더한 뒤 개인정보 동의를 하고 최종 제출하면 [FormSubmit](https://formsubmit.co/documentation)을 통해 `vonpat450@gmail.com`으로 전송합니다. 첨부는 PDF/JPG/PNG/DOC/DOCX 파일 1개, 10MB 이하입니다. FormSubmit의 CAPTCHA와 숨김 입력란을 스팸 방지에 사용합니다. FormSubmit 메일 주소 활성화와 기본 폼의 메일 수신은 이미 확인했습니다.

## 검색엔진 사이트맵

`python scripts/generate_sitemap.py`가 `dist/`의 공개 HTML 페이지를 찾아 정식 주소로 `dist/sitemap.xml`을 만듭니다. 예전 검색 주소인 `search.html`은 해외특허 페이지로 이동하므로 제외합니다. 각 페이지의 `lastmod`는 Git의 실제 수정 날짜를 사용합니다. `.github/workflows/sitemap.yml`은 매일 한국 시간 새벽 3시 15분에 실행되며, 사이트맵 내용이 달라진 경우에만 `main`에 커밋해 Cloudflare Pages에 배포합니다. GitHub Actions 화면에서 수동 실행도 가능합니다. `dist/robots.txt`에서 사이트맵 주소를 검색엔진에 알립니다.

## 칼럼 추가

`dist/articles/`에 영문 소문자와 하이픈으로 된 이름의 Markdown 파일을 추가합니다. 파일 이름이 공개 주소가 됩니다. 예를 들어 `overseas-filing-guide.md`는 `column-overseas-filing-guide.html`로 생성됩니다. 파일 상단 형식은 다음과 같습니다.

```md
---
published: 2026-10-21
category: 해외특허
description: 검색 결과에 표시할 한 줄 소개
thumbnail: assets/column-thumbnail.png
hero: assets/column-hero.png
related_url: overseas.html
related_label: 해외특허등록 살펴보기
source_1_label: 참고 자료 이름
source_1_url: https://example.com/source
---
# 칼럼 제목
## 칼럼 부제

본문 첫 문단입니다.

## 1. 첫 번째 소제목

본문이 이어집니다.
```

`published`와 제목·부제는 필수입니다. `thumbnail`, `hero`, 관련 페이지, 참고 자료 항목은 선택 사항입니다. 이미지를 지정하려면 파일을 `dist/assets/`에 먼저 추가합니다. 썸네일이 없으면 기본 그래픽이, 상단 이미지가 없으면 특허지식 기본 이미지가 표시됩니다. 참고 자료는 `source_2_label` / `source_2_url`처럼 최대 10개까지 추가할 수 있습니다.

로컬에서는 `python scripts/build_column.py`와 `python scripts/generate_sitemap.py`를 순서대로 실행합니다. 생성기는 모든 원고로 개별 칼럼 페이지와 `dist/articles-data.js` 목록을 만듭니다. 특허지식에는 모든 칼럼이 최신 게시일 순으로, 메인에는 최신 3편이 표시됩니다. GitHub의 `main` 브랜치에 원고를 올리면 `.github/workflows/build-columns.yml`이 같은 작업을 자동으로 실행하고 Cloudflare 배포로 이어집니다. 같은 제목이라도 파일 이름은 서로 달라야 합니다.

## 매일 칼럼 자동 게시

GitHub 저장소의 비밀값 `GEMINI_API_KEY`를 사용합니다. `.github/workflows/daily-column.yml`이 주말과 공휴일을 포함해 한국 시간 매일 오전 8시 17분과 10시 17분에 실행됩니다. 첫 실행이 성공하면 두 번째 실행은 이미 생성된 날짜 파일을 확인하고 종료합니다. GitHub Actions의 예약 실행은 지연되거나 누락될 수 있어 두 번 기회를 둔 것이며, 하루 한 편만 만들도록 `daily-YYYY-MM-DD.md` 파일 이름으로 중복을 막습니다.

Gemini 2.5 Flash가 공개된 공식 자료를 바탕으로 일반 정보 칼럼을 작성합니다. 생성기는 글 길이, 형식, 중복 제목을 검사한 뒤 `dist/articles/`에 저장합니다. 이후 칼럼 페이지·목록·사이트맵을 만들고 `main`에 커밋하면 Cloudflare Pages가 자동 배포합니다. API 오류나 품질 검사 실패 시 커밋하지 않고 Actions 실행이 실패로 표시됩니다. 자동 작성 원고는 법률·기술 내용을 모두 보증할 수 없으므로 게시 후 사람이 사실관계를 검토해야 합니다. Gemini 무료 등급의 실제 요청 한도와 모델 제공 여부는 Google AI Studio 계정 설정에 따릅니다.

Actions의 **Publish daily patent column → Run workflow**에서 `dry_run`을 켜면 Gemini 호출과 원고 검증만 하고 공개하지 않습니다. 끄면 해당 날짜의 글 한 편을 게시합니다. 비밀값은 로그에 출력하지 않습니다. 기존 특허정보검색 화면은 해외특허등록 안내 페이지(`overseas.html`)로 대체했습니다. 기존 `search.html` 주소는 새 페이지로 이동합니다.
