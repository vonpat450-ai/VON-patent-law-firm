const page = document.body.dataset.page || 'home';
const nav = [
  ['process','특허등록절차','process.html'],
  ['priority','특허우선심사','priority.html'],
  ['overseas','해외특허등록','overseas.html'],
  ['knowledge','특허지식','knowledge.html']
];
const image = {process:'process-hero.png',priority:'priority-hero.png',overseas:'overseas-globe.svg',knowledge:'knowledge-hero.png'};
const processSteps = [
  ['발명 상담','아이디어 이해'],['선행기술 검토','선행기술 조사'],['명세서 작성 및 출원','권리범위 설계'],
  ['심사청구','서류 제출'],['의견서·보정서 대응','심사 대응'],['등록','권리 확보']
];
const knowledge = [
  ['제품을 공개하기 전, 특허출원을 살펴보세요.','출시 일정과 준비 상황을 함께 살펴보는 이야기입니다.','제품 공개 전에 출원 시점과 공개 범위를 함께 검토해 보세요. 이미 공개한 내용이 있다면 공개 날짜와 자료를 정리해 전문가에게 알려주는 것이 좋습니다.'],
  ['비슷한 특허가 있다면 무엇을 비교할까요?','기술 구조와 작동 방식을 읽는 관점을 살펴봅니다.','비슷한 명칭보다 청구항에 적힌 구성과 작동 관계를 살펴보는 것이 중요합니다. 내 기술의 차이를 도면과 설명으로 정리해 보세요.'],
  ['심사 의견을 받았다면 무엇부터 볼까요?','통지 내용과 대응 순서를 차근차근 살펴봅니다.','통지서의 거절이유, 인용된 문헌, 제출 기한을 먼저 확인하세요. 차이점과 보정 가능한 범위를 정리한 뒤 대응 방향을 결정합니다.'],
  ['특허출원 전 확인할 것들','아이디어 정리부터 선행기술 검토까지 살펴봅니다.','핵심 기술, 구현 방법, 예상 변형, 공개 이력을 정리하면 출원 상담이 구체적이 됩니다. 관련 자료를 한곳에 모아 두세요.'],
  ['특허가 거절되면 끝나는 걸까요?','의견제출 통지와 이후 절차를 살펴봅니다.','심사 과정에서 거절이유가 통지되면 의견서나 보정서로 대응할 수 있습니다. 통지 내용과 기간에 따라 가능한 선택이 달라집니다.'],
  ['하나의 제품, 여러 특허가 필요할까요?','제품 안의 기술 요소를 나누어 살펴봅니다.','하나의 제품에도 구조, 제어 방법, 제조 공정 등 여러 발명이 들어갈 수 있습니다. 각 기술의 독립성과 사업상 중요도를 함께 살펴보세요.'],
  ['AI 기술은 어떻게 보호할까요?','기술 내용과 발명 방식의 쟁점을 정리합니다.','AI 자체라는 표현보다 해결하려는 기술 문제와 구체적인 구현 흐름을 설명하는 것이 중요합니다. 데이터 처리와 모델 적용 방식도 함께 검토합니다.'],
  ['제품을 공개한 뒤 출원할 수 있을까요?','공개 시점과 출원 계획을 함께 살펴봅니다.','공개 이후의 출원 가능성은 공개 형태와 시점, 적용 제도에 따라 달라질 수 있습니다. 공개 자료와 날짜를 보관하고 빠르게 상담해 보세요.'],
  ['좋은 특허와 강한 특허의 차이','등록 이후의 활용까지 생각해 봅니다.','등록 여부뿐 아니라 경쟁 제품에 적용 가능한 권리 범위, 회피 가능성, 사업 계획과의 연결을 함께 살펴보는 것이 좋습니다.']
];
const extraKnowledge = [
  ['특허 명세서에는 무엇을 담을까요?','발명의 구조와 효과를 설명하는 방법.','발명이 해결하는 문제, 구성, 작동 방식, 실시 예를 명확히 정리해 두면 상담에 도움이 됩니다.'],
  ['특허권은 언제부터 효력이 생길까요?','출원과 등록의 차이를 살펴봅니다.','출원과 등록은 다른 단계입니다. 권리의 효력과 범위는 등록 여부 및 청구항에 따라 살펴야 합니다.'],
  ['공동 발명자는 어떻게 정할까요?','발명 과정에 참여한 사람을 살펴봅니다.','아이디어의 기술적 완성에 실제로 기여한 내용을 기준으로 사실관계를 정리해 보세요.'],
  ['해외 출원은 언제 준비할까요?','시장 계획과 출원 일정을 함께 봅니다.','진출 국가, 비용, 일정, 우선권 관련 기한을 종합적으로 검토해야 합니다.'],
  ['특허 도면은 왜 중요할까요?','구조와 작동 관계를 보여주는 자료.','도면은 발명의 각 구성과 상호 작용을 설명하는 데 도움이 됩니다.'],
  ['특허 검색어는 어떻게 고를까요?','다른 표현과 분류를 함께 봅니다.','기술을 설명하는 여러 명칭, 유사어, 구성요소, 분류 기호를 조합해 검색해 보세요.'],
  ['심사청구는 무엇인가요?','출원 후 심사 절차의 한 단계.','출원과 심사청구는 별도 절차일 수 있습니다. 기한과 전략을 확인하세요.'],
  ['의견서와 보정서는 어떻게 다를까요?','심사 대응 문서의 역할.','의견서는 논리를 설명하고 보정서는 출원 서류의 내용을 정해진 범위에서 고치는 데 쓰입니다.'],
  ['특허 포트폴리오는 어떻게 관리할까요?','기술과 사업을 함께 정리합니다.','중요 기술, 제품 일정, 경쟁 상황에 맞춰 출원·유지 방향을 점검해 보세요.']
];
function header(){return `<header class="site-header"><div class="container header-inner"><a href="index.html" class="logo" aria-label="특허법인 본 홈"><img class="brand-logo" src="assets/von-standard-logo.png" alt="특허법인 본"></a><nav class="primary-nav" aria-label="주 메뉴">${nav.map(([id,label,href])=>`<a href="${href}" ${page===id?'aria-current="page"':''}>${label}</a>`).join('')}</nav><div class="header-actions"><a class="btn btn-primary btn-small" href="contact.html">상담 신청 <span aria-hidden="true">→</span></a><button class="menu-toggle" type="button" aria-label="메뉴 열기" aria-expanded="false" aria-controls="mobile-nav"><span></span><span></span><span></span></button></div></div><nav class="mobile-nav" id="mobile-nav" aria-label="모바일 메뉴"><a href="index.html">메인페이지</a>${nav.map(([id,label,href])=>`<a href="${href}">${label}</a>`).join('')}<a href="contact.html">상담 신청</a></nav></header>`}
function heroVisual(kind){
  if(kind==='home') return `<div class="hero-visual home-composition" aria-hidden="true"><img class="home-visual-blur" src="assets/home-hero-03.png" alt=""><img class="home-visual-wire" src="assets/home-hero-02.png" alt=""><img class="home-visual-final" src="assets/home-hero-01.png" alt=""></div>`;
  return `<div class="hero-visual" style="background-image:url('assets/${image[kind]}')" aria-hidden="true"></div>`;
}
function hero(title,description,kind='home',eyebrow='',secondary=''){return `<section class="hero hero-${kind} ${kind==='home'?'hero-home':''}" style="--hero-size:${kind==='home'?'1500px auto':'1380px auto'};--hero-position:right ${kind==='home'?'-42px':'-38px'}">${heroVisual(kind)}<div class="container hero-inner"><div class="hero-copy">${kind==='home'?`<div class="hero-eyebrow">${eyebrow}</div>`:`<div class="breadcrumb"><a href="index.html">⌂</a><span>›</span><span>${nav.find(x=>x[0]===kind)?.[1]}</span></div>`}<h1 class="hero-title"><span class="hero-title-echo" aria-hidden="true">${title}</span><span class="hero-title-foreground">${title}</span></h1><p class="hero-description"><span class="hero-description-echo" aria-hidden="true">${description}</span><span class="hero-description-foreground">${description}</span></p><div class="hero-buttons"><a class="btn btn-primary" href="contact.html">상담 신청 <span aria-hidden="true">→</span></a>${secondary?`<a class="btn btn-outline" href="${secondary}">내 아이디어, 특허가 될까? <span aria-hidden="true">→</span></a>`:''}</div>${kind==='home'?`<div class="hero-stats"><div><strong>5,500+</strong><small>누적 출원 건수</small></div><div><strong>92%</strong><small>등록 성공률</small></div><div><strong>12년+</strong><small>평균 경력의 변리사</small></div></div>`:''}</div></div></section>`}
function contact(title='지금, 아이디어를 이야기해 주세요.',description='간단한 정보만으로도, 변리사가 직접 검토해 드립니다.',pale=false){return `<section class="contact-section ${pale?'pale':''}" id="contact"><div class="container contact-grid"><div><h2 class="section-title">${title}</h2><p class="section-description">${description}</p></div><form class="contact-card" id="contact-quick-form"><div class="contact-fields"><label><span class="sr-only">이름</span><input name="name" type="text" placeholder="이름 (필수)" autocomplete="name" required></label><label><span class="sr-only">연락처</span><input name="phone" type="tel" placeholder="연락처 (필수)" autocomplete="tel" required></label><label><span class="sr-only">이메일</span><input name="email" type="email" placeholder="이메일 (필수)" autocomplete="email" required></label></div><div class="contact-radio"><strong>현재 진행 단계</strong><label><input type="radio" name="stage" value="아이디어 단계" checked> 아이디어 단계</label><label><input type="radio" name="stage" value="출원 준비"> 출원 준비</label><label><input type="radio" name="stage" value="심사 대응"> 심사 대응</label><label><input type="radio" name="stage" value="기타"> 기타</label></div><button class="btn btn-primary form-submit" type="submit">상담 신청하기 <span aria-hidden="true">→</span></button><p class="form-note">다음 페이지에서 국내·해외와 문의 내용, 자료를 확인한 뒤 최종 신청합니다.</p></form></div></section>`}
function footer(){return `<footer class="site-footer"><div class="container footer-grid"><div><a href="index.html" class="logo" aria-label="특허법인 본 홈"><img class="brand-logo" src="assets/von-standard-logo.png" alt="특허법인 본"></a><div class="footer-info"><div>개인정보처리방침&nbsp;&nbsp; | &nbsp;&nbsp;이용약관</div><div>서울 강남구 테헤란로70길 14-8 세왕개발빌딩 8층&nbsp; | &nbsp;02-6494-0524&nbsp; | &nbsp;<a href="mailto:vonpat450@gmail.com">vonpat450@gmail.com</a></div><div>© 2024 VON PATENT. All rights reserved.</div></div></div><a class="btn" href="contact.html">상담 신청하기 <span aria-hidden="true">→</span></a><div class="footer-side">더 선명한 세상이<br>당신의 기술로부터.</div></div></footer>`}
function articleCards(items,offset=0){return `<div class="article-grid">${items.map((a,i)=>`<article class="article-card"><button type="button" class="article-open" data-index="${offset+i}" aria-label="${a[0]} 읽기"><div class="article-art ${(i+offset)%3===1?'circle':''}" aria-hidden="true"></div><div class="article-copy"><strong>${a[0]}</strong><p>${a[1]}</p></div></button></article>`).join('')}</div>`}
function home(){return `${hero('기술을 더 선명하게,<br>특허를 더 강력하게','아이디어의 가능성을 정확히 분석하고,<br>권리의 범위를 설계합니다.<br>당신의 기술이 더 멀리, 더 안전하게 나아갈 수 있도록<br>특허의 해상도를 높입니다.','home','호칭뿐인 아이디어가,<br>선명한 권리가 되는 순간','process.html')}<section class="section"><div class="container split"><div><h2 class="section-title">복잡한 특허,<br>이제 선명해집니다.</h2><p class="section-description">막연한 아이디어도, 구체적인 기술도<br>체계적인 분석을 통해 명확한 권리로 만들어드립니다.</p></div><div class="process-strip">${[['발명 상담','아이디어 이해'],['기술 분석','선행기술 조사'],['명세서 작성','권리범위 설계'],['특허출원','서류 제출'],['심사 및 등록','권리 확보']].map((x,i)=>`<div class="process-item"><span class="process-num">0${i+1}</span><strong>${x[0]}</strong><small>${x[1]}</small></div>`).join('')}</div></div></section><section class="section dark-feature dark-home"><div class="container"><div style="max-width:580px"><span style="font-size:11px;letter-spacing:.15em;color:#91b1bb;font-weight:700">WHY VON PATENT</span><h2 class="section-title" style="margin-top:14px">보이는 기술을 넘어,<br>지켜지는 권리로.</h2><p class="section-description">단순한 서류 작성이 아닌,<br>기술의 본질을 이해하고 권리의 해상도를 높입니다.<br>시작부터 다른, 특허의 결과를 경험하세요.</p><div class="hero-stats"><div><strong>5,500+</strong><small>누적 출원 건수</small></div><div><strong>92%</strong><small>등록 성공률</small></div><div><strong>12년+</strong><small>평균 경력의 변리사</small></div></div></div></div></section>${contact()}<section class="section section-soft"><div class="container"><div class="section-topline"><div><h2 class="section-title">지식이 자산이 되는 이야기</h2><p class="section-description">특허, 더 깊이 이해할 수 있는 콘텐츠를 만나보세요.</p></div><a class="text-link" href="knowledge.html">전체 보기 →</a></div>${articleCards([knowledge[3],knowledge[1],knowledge[2]],[3,1,2][0])}</div></section><section class="section"><div class="container"><div class="section-topline"><h2 class="section-title">자주 묻는 질문</h2><a class="text-link" href="knowledge.html">전체 보기 →</a></div><div class="faq"><details><summary>Q. 아이디어만 있어도 상담이 가능한가요?</summary><p>네. 아이디어의 핵심 기능과 해결하려는 문제를 알려주시면 다음에 준비할 자료와 검토 방향을 함께 살펴볼 수 있습니다.</p></details><details><summary>Q. 특허출원 비용은 얼마나 드나요?</summary><p>기술 분야, 출원 범위, 도면 및 자료 준비 상태에 따라 달라집니다. 내용을 확인한 뒤 필요한 절차와 비용을 안내해 드립니다.</p></details><details><summary>Q. 출원부터 등록까지 얼마나 걸리나요?</summary><p>심사청구 시점과 심사 상황, 의견제출 여부에 따라 달라집니다. 일정이 중요한 경우 우선심사 가능성도 함께 검토할 수 있습니다.</p></details></div></div></section>`}
function process(){const rows=[['발명 상담','아이디어를 구체화하고 특허 가능성을 검토합니다.','발명 아이디어 개요 · 관련 자료','1:1 발명 상담 · 특허 가능성 검토'],['선행기술 검토','국내외 선행기술을 조사하여 신규성과 진보성을 검토합니다.','핵심 기술 내용 · 관련 자료','선행기술 조사 · 특허 가능성 분석'],['명세서 작성 및 출원','보호 범위를 정하는 명세서를 작성하고 출원합니다.','기술 설명 자료 · 도면 또는 사진','명세서 작성 및 검토 · 특허 출원'],['심사청구','출원 후 일정 기간 내에 심사청구를 진행합니다.','심사청구 시점 결정','심사청구서 제출 · 심사 진행 관리'],['의견서·보정서 대응','거절이유가 통지된 경우 의견서와 보정서를 제출하며 대응합니다.','거절이유서 확인 · 보완 아이디어 검토','의견서·보정서 작성 · 심사관 의견 대응'],['등록','심사를 통과하면 특허권이 설정되어 공식적으로 등록됩니다.','등록 결정 내용 확인','등록 절차 안내 · 등록 후 권리 관리 지원']];return `${hero('특허, 시작부터 등록까지<br>한눈에 정리했습니다','아이디어 상담부터 출원, 심사, 등록까지의 실제 진행 순서를 확인하세요.<br>VON이 체계적으로 도와드립니다.','process')}<section class="section section-soft"><div class="container"><h2 class="section-title">특허등록절차 한눈에 보기</h2><p class="section-description">아이디어 상담부터 등록까지, 6단계로 진행됩니다.</p><div class="steps-six">${processSteps.map((x,i)=>`<div><span class="step-symbol" aria-hidden="true"><img src="assets/process-step-0${i+1}.png" alt=""></span><small>0${i+1}</small><strong>${x[0]}</strong></div>`).join('')}</div></div></section><section class="section"><div class="container"><h2 class="section-title">단계별 상세 안내</h2><p class="section-description">각 단계별 주요 내용과 고객 준비사항, VON의 지원을 간단히 확인하세요.</p><table class="data-table"><thead><tr><th>단계</th><th>절차</th><th>주요 내용</th><th>고객 준비</th><th>VON 진행</th></tr></thead><tbody>${rows.map((r,i)=>`<tr><td><span class="number-badge">0${i+1}</span></td><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td></tr>`).join('')}</tbody></table></div></section><section class="section section-soft"><div class="container"><h2 class="section-title">다양한 분야의 변리사와 전문팀이 함께합니다</h2><p class="section-description">기술을 넘어 비즈니스까지, 특허등록과 관련된 모든 과정을 전문가와 함께합니다.</p><div class="expert-grid">${[['⌘','전자·ICT','AI, SW, 반도체'],['⚙','기계·메카트로닉스','기계, 기구, 소자'],['♧','화학·소재','화학, 소재, 제약'],['✚','바이오·의료','생명공학, 의료'],['▱','기술사업화','기술 라이선싱'],['▥','조사·분석','선행기술, FTO'],['⬡','기업인증','이노비즈 인증']].map((x,i)=>`<div class="expert-card"><b aria-hidden="true"><img src="assets/expertise-0${i+1}.png" alt=""></b><strong>${x[1]}</strong><small>${x[2]}</small></div>`).join('')}</div></div></section><section class="section dark-feature dark-process"><div class="container split"><div><h2 class="section-title">상담 전 준비하면 빨라지는 자료</h2><p class="section-description">자료가 있으면 보다 정확하고 빠른 상담이 가능합니다.</p></div><div class="checklist-panel">${['발명의 개요 및 목적','관련 시장 정보 (선택)','제품 또는 기술 관련 자료','선행기술 자료 (선택)','구체적 특징 및 차별 기술 정보','추가로 검토하고 싶은 내용'].map(x=>`<div>${x}</div>`).join('')}</div></div></section>${contact('지금, 전문가와 상담하세요','아이디어 단계부터 등록 이후까지, 전문 변리사가 친절히 안내해 드립니다.')}`}
function priority(){return `${hero('권리 확보가 시급할 때,<br>우선심사를 검토하세요','일정한 요건을 충족하는 특허출원은 우선심사 신청을 통해 일반적인 심사보다<br>빠르게 심사를 받을 수 있습니다.','priority')}<section class="section"><div class="container split"><div><h2 class="section-title">심사 순서를 앞당기는<br>우선심사</h2><p class="section-description">일반심사는 출원 순서에 따라 진행됩니다.<br>우선심사는 신청 요건에 해당하면 심사를 먼저 받을 수 있습니다.</p></div><table class="compact-table"><thead><tr><th>구분</th><th>심사 흐름</th><th>확인할 점</th></tr></thead><tbody><tr><td>일반심사</td><td>출원 순서에 따라 심사</td><td>심사 시점은 진행 상황에 따라 달라집니다.</td></tr><tr><td>우선심사</td><td>신청 요건 확인 후 우선 심사</td><td>요건과 증빙 서류를 먼저 확인합니다.</td></tr></tbody></table></div></section><section class="section section-pale"><div class="container"><h2 class="section-title">이런 상황에서 우선심사를 검토할 수 있습니다.</h2><p class="section-description">사업 계획과 기술의 활용 시점을 함께 고려합니다.</p><div class="feature-cards">${[['01','사업 일정이 빠를 때','제품 출시나 사업 일정에 맞춰 권리 확보 시점을 검토합니다.'],['02','투자 또는 계약을 앞두고 있을 때','투자유치, 라이선스 또는 사업계약 전에 심사 일정을 확인합니다.'],['03','출원 기술을 실제 사용 중일 때','사업에 적용 중인 기술의 보호 필요성을 살펴봅니다.'],['04','빠른 권리 확보가 시급할 때','시장 진입 계획에 맞춰 심사 시점을 판단합니다.']].map(x=>`<div class="feature-card"><small>${x[0]}</small><strong>${x[1]}</strong><p>${x[2]}</p></div>`).join('')}</div><p class="info-note">실제 우선심사 대상 여부는 출원 내용과 신청 사유를 구체적으로 검토해야 합니다.</p></div></section><section class="section"><div class="container"><h2 class="section-title">우선심사, 신청부터 대응까지</h2><p class="section-description">신청 요건을 확인하고 심사 결과에 맞춰 대응합니다.</p><div class="timeline">${[['특허출원','기술 내용을 정리해 출원합니다.'],['요건 검토','우선심사 대상인지 확인합니다.'],['자료 준비','신청 사유와 자료를 준비합니다.'],['우선심사 신청','특허청에 신청서를 제출합니다.'],['특허청 심사','신청 결과와 심사 진행을 확인합니다.'],['심사 대응','의견서를 통지에 맞춰 대응합니다.']].map((x,i)=>`<div><span>0${i+1}</span><strong>${x[0]}</strong><small>${x[1]}</small></div>`).join('')}</div></div></section><section class="section dark-feature dark-priority"><div class="container split"><div><h2 class="section-title">빠른 심사가<br>항상 유리한 것은 아닙니다.</h2><p class="section-description">발명의 완성도와 사업 일정을 함께 살펴 우선심사를 신청할 시점을 결정합니다.</p></div><div class="checklist-panel">${['발명의 완성도','명세서 준비','사업 일정','해외출원 계획'].map(x=>`<div>${x}</div>`).join('')}</div></div></section>${contact('지금, 우선심사 가능성을<br>확인하세요','출원 상황과 사업 계획을 알려주시면 검토할 사항을 정리해 드립니다.')}`}
function overseas(){
  const comparison = [
    ['좋은 점','목표 국가에 빠르게 출원 절차를 시작할 수 있습니다.','국제조사 결과를 참고하고 진입 국가를 검토할 시간을 확보할 수 있습니다.'],
    ['부담되는 점','국가별 번역·대리인·비용을 초기에 준비해야 합니다.','국제단계 비용이 들며, 이후 각국 단계의 비용도 별도로 발생합니다.'],
    ['국가 결정','출원할 국가를 비교적 일찍 정해야 합니다.','국내단계 진입 전까지 보호받을 국가를 검토할 수 있습니다.'],
    ['판단 자료','국가별 조사·심사 과정에서 결과를 확인합니다.','국제조사보고서와 견해서를 진입 결정에 참고합니다.'],
    ['현지 절차','선택한 국가의 요건에 따라 출원·심사를 진행합니다.','보호받을 국가에 진입한 뒤 각국 심사를 받습니다.']
  ];
  const situations = [
    ['목표 국가 확정 · 현지 절차 필요','진출할 나라가<br>이미 정해졌다면','개별국 직접출원','필요한 국가에 집중해 해당 국가의 절차를 시작합니다.'],
    ['후보 국가 다수 · 시장 검증 중','진출할 나라를<br>더 검토해야 한다면','PCT 국제출원','국제조사 결과와 사업 계획을 보며 진입국을 정할 시간을 확보합니다.'],
    ['국가 확정 · 비용과 일정 고민','어느 쪽이 효율적인지<br>판단이 어렵다면','출원일 · 현지 일정','국가별 진입 시점과 예상 비용, 필요한 심사 시간을 함께 비교합니다.']
  ];
  return `${hero('해외출원,<br>어떤 경로가 맞을까요?','개별국과 PCT의 장점과 부담을 같은 기준에서 비교하고,<br>사업 일정에 맞는 출원 경로를 살펴보세요.','overseas')}
    <section class="section overseas-comparison"><div class="container">
      <h2 class="section-title">개별국과 PCT, 무엇이 다를까요?</h2>
      <p class="section-description">개별국은 정해진 목표에 집중하고, PCT는 국가를 결정할 시간을 확보합니다.</p>
      <div class="overseas-table-wrap"><table class="overseas-table"><caption class="sr-only">개별국 직접출원과 PCT 국제출원 비교</caption>
        <thead><tr><th scope="col">판단 기준</th><th scope="col"><small>DIRECT FILING</small><strong>개별국 직접출원</strong><span>정해진 국가에 절차로 진입</span></th><th scope="col"><small>PCT ROUTE</small><strong>PCT 국제출원</strong><span>국제출원 후 필요한 국가에 진입</span></th></tr></thead>
        <tbody>${comparison.map(row=>`<tr><th scope="row">${row[0]}</th><td>${row[1]}</td><td>${row[2]}</td></tr>`).join('')}</tbody>
      </table></div>
      <p class="overseas-note">국제조사 결과는 등록 여부를 보증하지 않습니다. 각국 심사와 진입 기한은 국가별로 확인해야 합니다.</p>
    </div></section>
    <section class="section section-pale overseas-situations"><div class="container">
      <h2 class="section-title">내 상황이라면, 어떤 경로부터 볼까요?</h2>
      <p class="section-description">국가의 수와 사업 일정, 사업 계획과 결정해야 하는 시점을 함께 봅니다.</p>
      <div class="overseas-cards">${situations.map((item,index)=>`<article class="overseas-card"><small>${item[0]}</small><h3>${item[1]}</h3><div class="overseas-card-route"><span>${index===2?'함께 비교':'우선 검토'}</span><strong>${item[2]}</strong></div><p>${item[3]}</p></article>`).join('')}</div>
      <p class="overseas-note">빠른 현지 심사가 필요하다면 직접출원과 PCT 조기 국내단계 진입 가능성을 함께 확인합니다.</p>
    </div></section>
    <section class="section overseas-timing"><div class="container split">
      <div class="overseas-timing-copy"><h2 class="section-title">같은 12개월,<br>다른 결정 시점.</h2><p class="section-description">국내 선출원의 우선권을 주장한다면 일반적으로 12개월 안에 다음 출원을 준비합니다. 두 경로의 차이는 그 이후에 결정하고 지출하는 방식에서 커집니다.</p></div>
      <div class="overseas-timeline" aria-label="해외 출원 경로별 일정 비교"><div class="overseas-timeline-head"><strong>해외출원 경로별 비용·일정 흐름</strong><span>최초 출원일(우선일) 기준</span></div>
        <div class="overseas-timeline-row"><strong>개별국<br>직접출원</strong><div class="overseas-milestones"><div><b>0개월</b><small>최초 출원</small></div><div><b>12개월 이내</b><small>목표국 출원<br>국가별 비용 준비</small></div><div><b>이후</b><small>국가별 심사</small></div></div></div>
        <div class="overseas-timeline-row"><strong>PCT<br>국제출원</strong><div class="overseas-milestones"><div><b>0개월</b><small>최초 출원</small></div><div><b>12개월 이내</b><small>PCT 출원<br>국제단계 비용</small></div><div><b>통상 30·31개월</b><small>국가별 진입<br>국가별 비용 준비</small></div></div></div>
        <p class="overseas-timeline-callout">PCT는 비용이 없어지는 경로가 아니라, 주요 국가별 비용을 언제 결정할지 검토할 시간을 주는 경로입니다.</p>
        <p class="overseas-timeline-caveat">국내단계 기한은 국가별로 달라 예외가 있습니다. 구체적인 일정은 국가별로 확인해야 합니다. <a href="https://www.wipo.int/en/web/pct-system/faqs/faqs" target="_blank" rel="noopener noreferrer">WIPO 안내 ↗</a></p>
      </div>
    </div></section>
    ${contact('현재 상황에 맞는<br>해외출원 경로를 살펴보세요.','진출 국가가 아직 정해지지 않아도 괜찮습니다.<br>지금까지의 출원 상황을 알려주시면 함께 정리하겠습니다.',true)}`;
}
function knowledgePage(){return `${hero('특허를 알면,<br>다음 선택이 선명해집니다.','출원 시작부터 심사 대응까지,<br>기술을 지키는 데 필요한 이야기를 전합니다.','knowledge')}<section class="section"><div class="container"><h2 class="section-title">지금 읽어볼 특허 이야기</h2><p class="section-description">출원 준비부터 심사와 권리 활용까지, 필요한 이야기를 살펴보세요.</p><p class="result-label" id="article-count">전체 9개 칼럼</p><div id="knowledge-list">${articleCards(knowledge)}</div><div class="pagination" aria-label="칼럼 페이지"><button type="button" class="active" data-article-page="1" aria-current="page">1</button><button type="button" data-article-page="2">2</button></div></div></section>${contact('지금, 궁금한 기술을<br>이야기해 주세요.','어떤 단계에 있는지 알려주시면 함께 검토할 내용을 정리해 드립니다.',true)}<dialog class="modal" id="article-modal" aria-labelledby="modal-title"><button class="modal-close" type="button" aria-label="닫기">×</button><small class="modal-kicker">VON PATENT · 특허지식</small><h2 id="modal-title"></h2><p id="modal-body"></p><a class="btn btn-primary" href="contact.html">상담 신청 →</a></dialog>`}
function consultationPage(){return `<section class="consult-hero"><div class="container consult-hero-inner"><div class="breadcrumb"><a href="index.html">⌂</a><span>›</span><span>상담 신청</span></div><h1 class="consult-hero-title">기술의 현재 상황을<br>들려주세요.</h1><p>아이디어 단계부터 심사 대응까지, 지금 필요한 내용을 함께 살펴보겠습니다.<br>기본 정보만 남겨도 신청할 수 있습니다.</p></div></section><section class="consult-section"><div class="container"><div class="consult-intro"><h2 class="section-title">상담 신청</h2><p class="section-description">필수 정보만 입력해도 신청할 수 있습니다. 문의 내용과 자료는 필요하다면 추가해 주세요.</p></div><div class="consult-layout"><form class="consult-form" id="consult-form" action="https://formsubmit.co/vonpat450@gmail.com" method="POST" enctype="multipart/form-data"><input type="hidden" name="_subject" value="[특허법인 본] 홈페이지 상담 신청"><input type="hidden" name="_template" value="table"><input type="hidden" name="_url" value="https://von-patent-law-firm.pages.dev/contact.html"><div class="form-honey" aria-hidden="true"><label>비워 두세요 <input type="text" name="_honey" tabindex="-1" autocomplete="off"></label></div><div class="consult-block"><div class="consult-block-heading"><h3><span>01</span> 신청자 정보</h3><small>* 필수 입력</small></div><div class="consult-fields"><label class="consult-field"><span>이름 <b>*</b></span><input name="name" type="text" placeholder="이름을 입력해 주세요" autocomplete="name" required></label><label class="consult-field"><span>연락처 <b>*</b></span><input name="phone" type="tel" placeholder="연락 가능한 번호를 입력해 주세요" autocomplete="tel" required></label><label class="consult-field"><span>이메일 <b>*</b></span><input name="email" type="email" placeholder="이메일 주소를 입력해 주세요" autocomplete="email" required></label></div></div><div class="consult-block consult-details"><div class="consult-block-heading"><h3><span>02</span> 상담 내용</h3></div><fieldset class="consult-fieldset"><legend>출원 대상 <b>*</b></legend><div class="consult-options consult-region"><label class="consult-option"><input type="radio" name="jurisdiction" value="국내" required><span>국내 특허</span></label><label class="consult-option"><input type="radio" name="jurisdiction" value="해외"><span>해외 특허</span></label></div><label class="consult-field consult-country" id="consult-country-wrap" for="consult-country" hidden><span>해외 국가명 <b>*</b></span><input id="consult-country" name="country" type="text" placeholder="예: 미국, 일본" autocomplete="off" disabled></label><p class="consult-region-help">해외 여러 국가를 검토 중이라면 쉼표로 구분해 적어 주세요.</p></fieldset><fieldset class="consult-fieldset"><legend>상담 분야 <b>*</b></legend><div class="consult-options consult-category">${['특허출원·등록','우선심사','특허검색·선행기술','심사 대응','기타'].map((label,i)=>`<label class="consult-option"><input type="radio" name="category" value="${label}" ${i===0?'checked':''}><span>${label}</span></label>`).join('')}</div></fieldset><fieldset class="consult-fieldset"><legend>현재 진행 단계 <b>*</b></legend><div class="consult-options consult-stage">${['아이디어 단계','출원 준비','심사 대응','기타'].map((label,i)=>`<label class="consult-option"><input type="radio" name="stage" value="${label}" ${i===0?'checked':''}><span>${label}</span></label>`).join('')}</div></fieldset><label class="consult-field consult-message"><span>문의 내용 <em>선택</em></span><textarea name="message" rows="6" placeholder="현재 단계나 궁금한 점을 간단히 적어 주세요.&#10;예) 발명 아이디어가 있는데 특허출원을 어디서부터 시작해야 할지 궁금합니다."></textarea></label><p class="consult-help">공개 전 기술의 핵심 내용은 상담 중에 전달하셔도 됩니다.</p><div class="consult-field consult-upload-field"><span>자료 첨부 <em>선택</em></span><label class="consult-upload" for="consult-attachment"><span class="consult-upload-plus" aria-hidden="true">＋</span><span class="consult-upload-copy"><strong>상담에 도움이 되는 자료가 있다면 첨부해 주세요.</strong><small id="attachment-status" aria-live="polite">PDF, JPG, PNG, DOC, DOCX · 파일 1개, 10MB 이하</small></span><span class="consult-file-button">파일 선택</span></label><input class="sr-only" type="file" id="consult-attachment" name="attachment" accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"><p id="attachment-error" class="consult-error" role="alert" hidden></p></div></div><div class="consult-final"><div class="consult-privacy"><strong>개인정보 수집·이용 안내</strong><p>상담 접수와 회신을 위해 이름, 연락처, 이메일, 출원 대상, 해외 국가명(해외 선택 시), 상담 분야, 진행 단계와 입력하신 문의 내용 및 첨부 자료를 이용합니다. 정보는 FormSubmit을 통해 이메일로 전달됩니다.</p></div><label class="consult-consent"><input type="checkbox" name="privacy_consent" value="동의" required><span>개인정보 수집·이용에 동의합니다. <b>(필수)</b></span></label><div class="consult-submit-row"><p>입력하신 내용은 상담 접수를 위해 전달됩니다.</p><button class="btn btn-primary" type="submit">상담 신청하기 <span aria-hidden="true">→</span></button></div></div></form><aside class="consult-aside"><span class="consult-aside-kicker">BEFORE YOU SEND</span><h3>어떻게 진행되나요?</h3><p>작성하신 상황을 확인한 뒤, 필요한 상담 방향을 안내해 드립니다.</p><div class="consult-aside-divider"></div><strong>상담 진행 순서</strong><ol><li><span>01</span><div><b>신청 접수</b><small>기본 정보와 상담 분야를 전해 주세요.</small></div></li><li><span>02</span><div><b>내용 확인</b><small>문의에 맞는 담당자가 내용을 살펴봅니다.</small></div></li><li><span>03</span><div><b>연락 및 안내</b><small>입력하신 연락처로 다음 단계를 안내합니다.</small></div></li></ol><div class="consult-aside-note"><strong>자료가 아직 없어도 괜찮습니다.</strong><small>아이디어를 정리해 메모나 현재 진행 상황만으로도 상담을 신청할 수 있습니다.</small></div></aside></div></div></section>`}
const views = {home,process,priority,overseas,knowledge:knowledgePage,consultation:consultationPage};
document.getElementById('app').innerHTML = header() + views[page]() + footer();
const toggle = document.querySelector('.menu-toggle');
toggle.addEventListener('click',()=>{const n=document.getElementById('mobile-nav');const open=n.classList.toggle('open');toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',open?'메뉴 닫기':'메뉴 열기')});
document.querySelectorAll('.mobile-nav a').forEach(a=>a.addEventListener('click',()=>{document.getElementById('mobile-nav').classList.remove('open');toggle.setAttribute('aria-expanded','false')}));
let articleSet=knowledge;
document.querySelectorAll('[data-article-page]').forEach(b=>b.addEventListener('click',()=>{const n=Number(b.dataset.articlePage);articleSet=n===1?knowledge:extraKnowledge;document.getElementById('knowledge-list').innerHTML=articleCards(articleSet);document.querySelectorAll('[data-article-page]').forEach(x=>{x.classList.toggle('active',x===b);x.toggleAttribute('aria-current',x===b)});document.getElementById('article-count').textContent=`전체 ${articleSet.length}개 칼럼`;document.getElementById('knowledge-list').scrollIntoView({behavior:'smooth',block:'start'})}));
document.addEventListener('click',e=>{const article=e.target.closest('.article-open');if(article&&page==='knowledge'){const a=articleSet[Number(article.dataset.index)];const d=document.getElementById('article-modal');document.getElementById('modal-title').textContent=a[0];document.getElementById('modal-body').textContent=a[2];d.showModal()}if(e.target.matches('.modal-close'))document.getElementById('article-modal').close()});
document.getElementById('article-modal')?.addEventListener('click',e=>{if(e.target===e.currentTarget)e.currentTarget.close()});
if(page==='home')document.querySelectorAll('.article-open').forEach(button=>button.addEventListener('click',()=>window.location.href='knowledge.html'));



const quickForm = document.getElementById('contact-quick-form');
quickForm?.addEventListener('submit', event => {
  event.preventDefault();
  if (!quickForm.reportValidity()) return;
  const values = new FormData(quickForm);
  const lead = {name:String(values.get('name')||''),phone:String(values.get('phone')||''),email:String(values.get('email')||''),stage:String(values.get('stage')||'아이디어 단계')};
  const serialized = JSON.stringify(lead);
  try { sessionStorage.setItem('von-consultation-lead',serialized); } catch (_) {}
  window.name = 'von-consultation-lead:' + serialized;
  window.location.assign('contact.html');
});

const consultationForm = document.getElementById('consult-form');
if (consultationForm) {
  const regionInputs = consultationForm.querySelectorAll('input[name="jurisdiction"]');
  const countryWrap = document.getElementById('consult-country-wrap');
  const countryInput = document.getElementById('consult-country');
  function updateRegion() {
    const overseas = consultationForm.querySelector('input[name="jurisdiction"]:checked')?.value === '해외';
    countryWrap.hidden = !overseas;
    countryInput.disabled = !overseas;
    countryInput.required = overseas;
    if (!overseas) countryInput.value = '';
  }
  regionInputs.forEach(input => input.addEventListener('change', updateRegion));
  updateRegion();
  let serialized = '';
  try { serialized = sessionStorage.getItem('von-consultation-lead') || ''; sessionStorage.removeItem('von-consultation-lead'); } catch (_) {}
  if (!serialized && window.name.startsWith('von-consultation-lead:')) serialized = window.name.slice('von-consultation-lead:'.length);
  if (window.name.startsWith('von-consultation-lead:')) window.name = '';
  if (serialized) {
    try {
      const lead = JSON.parse(serialized);
      for (const key of ['name','phone','email']) if (typeof lead[key] === 'string') consultationForm.elements[key].value = lead[key];
      const stage = Array.from(consultationForm.querySelectorAll('input[name="stage"]')).find(input => input.value === lead.stage);
      if (stage) stage.checked = true;
    } catch (_) {}
  }
  const attachment = document.getElementById('consult-attachment');
  const status = document.getElementById('attachment-status');
  const error = document.getElementById('attachment-error');
  function validateAttachment() {
    const file = attachment.files[0];
    error.hidden = true;
    status.textContent = file ? file.name : 'PDF, JPG, PNG, DOC, DOCX · 파일 1개, 10MB 이하';
    if (!file) return true;
    if (!/\.(pdf|jpe?g|png|docx?)$/i.test(file.name) || file.size > 10 * 1024 * 1024) {
      error.textContent = 'PDF, JPG, PNG, DOC, DOCX 파일 1개를 10MB 이하로 선택해 주세요.';
      error.hidden = false;
      attachment.value = '';
      status.textContent = 'PDF, JPG, PNG, DOC, DOCX · 파일 1개, 10MB 이하';
      return false;
    }
    return true;
  }
  attachment.addEventListener('change',validateAttachment);
  consultationForm.addEventListener('submit',event => {
    if (!validateAttachment()) { event.preventDefault(); attachment.focus(); }
  });
}
