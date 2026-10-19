const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../dist/app.js'), 'utf8');
const quickStart = source.indexOf('const quickForm =');
const fullStart = source.indexOf('const consultationForm =');
assert.ok(quickStart > 0 && fullStart > quickStart);

const render = {document: {body: {dataset: {page: 'consultation'}}}};
vm.createContext(render);
vm.runInContext(source.slice(0, source.indexOf('const views =')), render);
const fullPage = render.header() + render.consultationPage() + render.footer();
assert.match(fullPage, /href="contact\.html"/);
assert.match(fullPage, /id="consult-form"[^>]*action="https:\/\/formsubmit\.co\/vonpat450@gmail\.com"[^>]*method="POST"[^>]*enctype="multipart\/form-data"/);
for (const field of ['name', 'phone', 'email', 'category', 'stage', 'message', 'attachment', 'privacy_consent']) {
  assert.ok(fullPage.includes(`name="${field}"`), `${field} is missing`);
}
for (const view of [render.home, render.process, render.priority, render.search, render.knowledgePage]) {
  const page = view();
  assert.match(page, /id="contact-quick-form"/);
  assert.ok(!page.includes('href="#contact"'));
}

const listeners = {};
const quickForm = {
  addEventListener: (event, callback) => { listeners[event] = callback; },
  reportValidity: () => true
};
const saved = new Map();
const window = {name: '', location: {assign: value => { window.destination = value; }}};
const quick = {
  document: {getElementById: id => id === 'contact-quick-form' ? quickForm : null},
  sessionStorage: {setItem: (key, value) => saved.set(key, value)},
  FormData: class { get(key) { return {name: '테스트 이름', phone: '010-1234-5678', email: 'test@example.com', stage: '출원 준비'}[key]; } },
  window
};
vm.createContext(quick);
vm.runInContext(source.slice(quickStart, fullStart), quick);
listeners.submit({preventDefault() {}});
assert.equal(window.destination, 'contact.html');
assert.equal(JSON.parse(saved.get('von-consultation-lead')).stage, '출원 준비');

const stageInputs = ['아이디어 단계', '출원 준비', '심사 대응', '기타'].map(value => ({value, checked: false}));
const elements = {name: {value: ''}, phone: {value: ''}, email: {value: ''}};
const form = {elements, querySelectorAll: () => stageInputs, addEventListener() {}};
const attachment = {files: [], value: '', addEventListener(event, callback) { this.onChange = callback; }};
const status = {textContent: ''};
const error = {hidden: true, textContent: ''};
const controls = {'consult-form': form, 'consult-attachment': attachment, 'attachment-status': status, 'attachment-error': error};
const full = {
  document: {getElementById: id => controls[id]},
  sessionStorage: {getItem: key => saved.get(key), removeItem: key => saved.delete(key)},
  window
};
vm.createContext(full);
vm.runInContext(source.slice(fullStart), full);
assert.equal(elements.name.value, '테스트 이름');
assert.equal(elements.phone.value, '010-1234-5678');
assert.equal(elements.email.value, 'test@example.com');
assert.equal(stageInputs.find(input => input.checked).value, '출원 준비');
assert.equal(window.name, '');
assert.equal(saved.has('von-consultation-lead'), false);

attachment.files = [{name: 'too-large.pdf', size: 11 * 1024 * 1024}];
attachment.onChange();
assert.equal(error.hidden, false);
attachment.files = [{name: 'drawing.pdf', size: 1024}];
attachment.onChange();
assert.equal(error.hidden, true);
assert.equal(status.textContent, 'drawing.pdf');

console.log('Consultation navigation, prefill, form fields, and attachment checks passed.');
