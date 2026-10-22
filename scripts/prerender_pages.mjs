/** Put the existing page templates in HTML before any browser JavaScript runs. */
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import vm from 'node:vm';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const dist = join(root, 'dist');
const source = readFileSync(join(dist, 'app.js'), 'utf8');
const templates = source.split('const views =')[0];
if (templates === source) throw new Error('Could not find page templates in app.js');

const articleSource = readFileSync(join(dist, 'articles-data.js'), 'utf8');
const articleMatch = articleSource.match(/^window\.VON_ARTICLES=(.*);\s*$/s);
if (!articleMatch) throw new Error('Invalid articles-data.js');
const allArticles = JSON.parse(articleMatch[1]);
const now = process.env.SEO_BUILD_NOW ? new Date(process.env.SEO_BUILD_NOW) : new Date();
if (Number.isNaN(now.getTime())) throw new Error('Invalid SEO_BUILD_NOW');
const visibleArticles = allArticles.filter(article =>
  Date.parse(`${article.published}T08:00:00+09:00`) <= now.getTime()
);

function components(page) {
  const context = { document: { body: { dataset: { page } } }, window: { VON_ARTICLES: visibleArticles } };
  return vm.runInNewContext(`${templates}\n({header,footer,home,process,priority,overseas,knowledgePage,consultationPage})`, context);
}

function renderIntoApp(html, markup) {
  const content = `<div id="app"><!--STATIC_RENDER_START-->${markup}<!--STATIC_RENDER_END--></div>`;
  if (html.includes('<!--STATIC_RENDER_START-->')) {
    return html.replace(/<div id="app"><!--STATIC_RENDER_START-->[\s\S]*?<!--STATIC_RENDER_END--><\/div>/, content);
  }
  if (!html.includes('<div id="app"></div>')) throw new Error('Missing #app placeholder');
  return html.replace('<div id="app"></div>', content);
}

const views = { home: 'home', process: 'process', priority: 'priority', overseas: 'overseas', knowledge: 'knowledgePage', consultation: 'consultationPage' };
for (const [page, view] of Object.entries(views)) {
  const filename = page === 'home' ? 'index.html' : page === 'consultation' ? 'contact.html' : `${page}.html`;
  const path = join(dist, filename);
  const parts = components(page);
  const markup = `${parts.header()}<main id="main-content">${parts[view]()}</main>${parts.footer()}`;
  writeFileSync(path, renderIntoApp(readFileSync(path, 'utf8'), markup).replace(/[ \t]+$/gm, ''));
}

for (const filename of readdirSync(dist).filter(name => /^column-.+\.html$/.test(name))) {
  const path = join(dist, filename);
  let html = readFileSync(path, 'utf8');
  const template = html.match(/<template id="column-content">([\s\S]*?)<\/template>/);
  if (!template) continue;
  const parts = components('column');
  const body = template[1].replace('<main>', '<main id="main-content">');
  html = renderIntoApp(html, `${parts.header()}${body}${parts.footer()}`);
  html = html.replace(template[0], '');
  writeFileSync(path, html.replace(/[ \t]+$/gm, ''));
}

console.log(`Prerendered service pages and ${visibleArticles.length} currently released article links`);
