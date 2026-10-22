# 특허법인 본 홈페이지

정적 HTML/CSS/JavaScript 사이트입니다. 공개할 파일은 `dist/`에 있습니다.

## Cloudflare Pages 연결

GitHub 저장소의 `main` 브랜치를 Cloudflare Pages에 연결합니다. Framework preset은 `None`, Build command는 비워 두고, Build output directory는 `dist`로 설정합니다. 기본 공개 주소는 `https://vonpatglobalpt.net/`이며, `www.vonpatglobalpt.net`도 같은 Pages 프로젝트에 연결되어 있습니다. 이 사이트에는 npm 빌드가 필요하지 않습니다.

## 상담 이메일

상단과 본문의 상담 버튼은 `contact.html`로 이동합니다. 각 페이지 하단의 간단 입력폼은 이름, 연락처, 이메일, 진행 단계를 같은 탭의 브라우저 저장소에 잠시 보관하고 상담 페이지의 해당 칸에 채웁니다. 주소에는 개인정보를 넣지 않습니다. 상담 페이지에서는 출원 대상을 먼저 선택합니다. 국내 특허를 선택하면 상담 분야를 고른 뒤 현재 진행 단계를 선택할 수 있습니다. 해외 특허를 선택하면 국가명과 선택 사항인 국내 출원·등록 특허번호 입력란이 열리며 국내용 상담 분야와 진행 단계는 제출되지 않습니다. 연락처는 010 휴대폰 번호만 받으며 입력 중 하이픈을 붙이고, 이메일은 도메인까지 검사합니다. 문의 내용과 자료를 더한 뒤 개인정보 동의를 하고 최종 제출하면 [FormSubmit](https://formsubmit.co/documentation)을 통해 `vonpat450@gmail.com`으로 전송합니다. 첨부는 PDF/JPG/PNG/DOC/DOCX 파일 1개, 10MB 이하입니다. FormSubmit의 CAPTCHA와 숨김 입력란을 스팸 방지에 사용합니다. FormSubmit 메일 주소 활성화와 기본 폼의 메일 수신은 이미 확인했습니다.

## 검색엔진 사이트맵

`python scripts/generate_sitemap.py`가 `dist/`의 공개 HTML 페이지를 찾아 정식 주소로 `dist/sitemap.xml`을 만듭니다. 예전 검색 주소인 `search.html`은 해외특허 페이지로 이동하므로 제외합니다. 각 페이지의 `lastmod`는 Git의 실제 수정 날짜를 사용합니다. `.github/workflows/sitemap.yml`은 매일 한국 시간 새벽 3시 15분에 실행되며, 사이트맵 내용이 달라진 경우에만 `main`에 커밋해 Cloudflare Pages에 배포합니다. GitHub Actions 화면에서 수동 실행도 가능합니다. `dist/robots.txt`에서 사이트맵 주소를 검색엔진에 알립니다.

### 오전 8시 칼럼 공개

`.github/workflows/prepare-column.yml`은 한국시간 05:17, 07:17, 13:17, 19:17에 Gemini로 검증된 원고 대기열을 보충합니다. 미래 게시 예정 원고는 최대 7편을 유지하며, 하루 새로 작성하는 원고는 최대 3편입니다. 비어 있는 게시 날짜에 하루 1편씩 배정해 HTML·썸네일·목록·사이트맵을 미리 Cloudflare Pages에 배포합니다. `dist/_worker.js`가 요청 시각을 검사해 게시 예정일 08:00 KST 전에는 칼럼 본문, 원본 Markdown, 썸네일, 목록, 사이트맵에서 해당 글을 숨깁니다. 08:00부터 별도 GitHub 예약 작업을 기다리지 않고 공개합니다. `dist/_routes.json`은 이 검사에 필요한 경로에서만 Pages Function을 실행합니다.

원고 준비 작업은 배포 후 `/column-release-status`를 확인해 다음 날 글이 Cloudflare에 도착했는지 검사합니다. 기존 `.github/workflows/daily-column.yml`의 08:00~10:00 실행은 실제 사이트 노출 확인과 배포 실패 시 복구를 맡습니다. 하루 1편만 게시되며, Gemini 또는 GitHub 예약 실행이 잠시 늦어져도 미리 배포한 글은 예정 시각에 공개됩니다. Pages Function 호출 한도나 Cloudflare 장애는 별도 운영 제약입니다.

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

원고 지침은 `automation/column_prompt_ko.txt`, 공식자료와 후보 질문은 `automation/topics.json`에서 수정합니다. `scripts/column_automation.py`가 공식 기관의 실제 웹페이지 본문을 수집하고 최근 30일 제목·요약과 문체 참고 원고를 Gemini에 전달합니다. JSON 필드, 글의 구성과 길이, 주제 중복, 출처 URL, 원문 인용 구절을 검사합니다. 검증에 실패하면 한 번 수정 요청을 보내고, 재검증에도 실패하면 다음 후보 질문으로 넘어갑니다. 이 검사와 별도로 Gemini의 주장 검토를 한 번 더 수행하지만, 법률적 정확성을 완전히 보증하지는 못하므로 게시 후 사람이 확인해야 합니다. API 키는 GitHub 비밀값 `GEMINI_API_KEY`로만 전달합니다.

`.github/workflows/prepare-column.yml`은 주말·공휴일을 포함한 매일 **한국시간 05:17·07:17**에 실행하여 검증된 원고 2편을 `automation/queue/`에 보관합니다. 기존에 준비된 원고가 2편이면 추가로 생성하지 않습니다. 수동 실행의 `dry_run`은 실제 Gemini 호출과 검증만 하고 저장하거나 게시하지 않습니다.

`.github/workflows/daily-column.yml`은 매일 **한국시간 08:00, 08:30, 09:00, 09:30, 10:00**에 실행합니다. 가장 오래된 실패 원고를 우선하고 하루에 새 글 1편만 게시합니다. 같은 원고를 다시 시도할 때 별도 글을 추가하지 않습니다. 원고·썸네일·개별 페이지·목록·사이트맵을 GitHub `main`에 올리면 Cloudflare Pages가 배포하며, 자동화는 실제 공개 도메인의 글 제목, 목록 데이터, 목록 화면의 버전과 썸네일이 확인되어야 성공으로 기록합니다. 5회 실패한 원고는 상태와 함께 보존되어 다음 날 우선 대상이 됩니다. 출처가 변경된 원고는 게시하지 않습니다.

새 원고는 `layout: guide`로 렌더링됩니다. 제목 아래에 핵심 답, 3~4개 본문 절, 3~5개 확인 항목, 마무리와 실제 사용한 공식자료가 표시됩니다. `scripts/make_thumbnail.py`는 기존 사이트의 주제별 사진을 활용해 WebP 썸네일을 만듭니다. 기존 수동 원고와 2026-10-21 칼럼의 레이아웃은 그대로 유지됩니다.

로컬 점검은 `python -m unittest discover -s tests -v`, `python scripts/publish_daily_column.py verify-existing`으로 실행합니다. Actions에서 수동으로 **Publish verified daily patent column**을 실행할 때 `publish_now`가 꺼져 있으면 오늘 글의 공개 상태만 확인하고, 켜져 있으면 GitHub 예약 실행 누락 시 남아 있는 5회 시도 중 하나를 사용하여 즉시 게시합니다. 예약 작업은 GitHub Actions의 실제 시작 시각에 따라 지연·누락될 수 있으므로 08:00 정각 게시를 보증하지는 않습니다. GitHub 반영과 Cloudflare 배포가 정상이어도 공개 사이트 확인에 실패하면 게시 성공으로 기록하지 않습니다.
