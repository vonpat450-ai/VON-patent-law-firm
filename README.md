# 특허법인 본 홈페이지

정적 HTML/CSS/JavaScript 사이트입니다. 공개할 파일은 `dist/`에 있습니다.

## Cloudflare Pages 연결

GitHub 저장소의 `main` 브랜치를 Cloudflare Pages에 연결합니다. Framework preset은 `None`, Build command는 비워 두고, Build output directory는 `dist`로 설정합니다. 기본 공개 주소는 `https://vonpatglobalpt.net/`이며, `www.vonpatglobalpt.net`도 같은 Pages 프로젝트에 연결되어 있습니다. 이 사이트에는 npm 빌드가 필요하지 않습니다.

## 상담 이메일

상단과 본문의 상담 버튼은 `contact.html`로 이동합니다. 각 페이지 하단의 간단 입력폼은 이름, 연락처, 이메일, 진행 단계를 같은 탭의 브라우저 저장소에 잠시 보관하고 상담 페이지의 해당 칸에 채웁니다. 주소에는 개인정보를 넣지 않습니다. 상담 페이지에서는 출원 대상을 먼저 선택합니다. 국내 특허를 선택하면 상담 분야를 고른 뒤 현재 진행 단계를 선택할 수 있습니다. 해외 특허를 선택하면 국가명과 선택 사항인 국내 출원·등록 특허번호 입력란이 열리며 국내용 상담 분야와 진행 단계는 제출되지 않습니다. 연락처는 010 휴대폰 번호만 받으며 입력 중 하이픈을 붙이고, 이메일은 도메인까지 검사합니다. 문의 내용과 자료를 더한 뒤 개인정보 동의를 하고 최종 제출하면 [FormSubmit](https://formsubmit.co/documentation)을 통해 `vonpat450@gmail.com`으로 전송합니다. 첨부는 PDF/JPG/PNG/DOC/DOCX 파일 1개, 10MB 이하입니다. FormSubmit의 CAPTCHA와 숨김 입력란을 스팸 방지에 사용합니다. FormSubmit 메일 주소 활성화와 기본 폼의 메일 수신은 이미 확인했습니다.

## 보류 중인 작업

특허 칼럼의 AI 자동 작성은 회사에서 칼럼 양식을 제공한 뒤 설계합니다. 기존 특허정보검색 화면은 해외특허등록 안내 페이지(`overseas.html`)로 대체했습니다. 기존 `search.html` 주소는 새 페이지로 이동합니다.
