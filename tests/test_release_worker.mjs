import assert from 'node:assert/strict';
import { test } from 'node:test';
import { handle } from '../dist/_worker.js';

const href = 'column-daily-2026-10-23-test.html';
const article = { title: '내일 칼럼', href, published: '2026-10-23' };
const schedule = { version: 1, articles: [{
  publish_at: '2026-10-23T08:00:00+09:00', href,
  source: 'articles/daily-2026-10-23-test.md',
  thumbnail: 'assets/daily-2026-10-23-test-thumb.webp',
}] };
const assets = {
  '/publication-schedule.json': JSON.stringify(schedule),
  '/articles-data.js': `window.VON_ARTICLES=${JSON.stringify([article])};\n`,
  '/sitemap.xml': '<?xml version="1.0"?><urlset><url><loc>https://vonpatglobalpt.net/column-daily-2026-10-23-test</loc></url></urlset>',
  [`/${href}`]: '<h1>내일 칼럼</h1>',
  '/column-daily-2026-10-23-test': '<h1>내일 칼럼</h1>',
  '/articles/daily-2026-10-23-test.md': 'raw draft',
  '/assets/daily-2026-10-23-test-thumb.webp': 'thumbnail',
  '/column-old': '<h1>지난 칼럼</h1>',
};
const env = { ASSETS: { fetch: async request => {
  const value = assets[new URL(request.url).pathname];
  return new Response(value ?? 'missing', { status: value === undefined ? 404 : 200 });
} } };
const before = Date.parse('2026-10-22T22:59:59Z');
const release = Date.parse('2026-10-22T23:00:00Z');
async function get(path, time) {
  return handle(new Request(`https://vonpatglobalpt.net${path}`), env, time);
}

test('prepublished pages and their raw assets are hidden until exactly 08:00 KST', async () => {
  for (const path of [`/${href}`, '/column-daily-2026-10-23-test', '/articles/daily-2026-10-23-test.md', '/assets/daily-2026-10-23-test-thumb.webp']) {
    assert.equal((await get(path, before)).status, 404);
    assert.equal((await get(path, release)).status, 200);
  }
  assert.equal((await get('/publication-schedule.json', release)).status, 404);
  assert.equal((await get('/column-old', before)).status, 200);
});

test('listing and sitemap reveal the column at the same release time', async () => {
  assert.deepEqual((await (await get('/column-release-status', before)).json()).ready_dates, ['2026-10-23']);
  assert.deepEqual((await (await get('/column-release-status', release)).json()).ready_dates, []);
  assert.equal((await (await get('/articles-data.js', before)).text()).includes('내일 칼럼'), false);
  assert.equal((await (await get('/sitemap.xml', before)).text()).includes('column-daily-2026-10-23-test'), false);
  assert.equal((await (await get('/articles-data.js', release)).text()).includes('내일 칼럼'), true);
  assert.equal((await (await get('/sitemap.xml', release)).text()).includes('column-daily-2026-10-23-test'), true);
});

test('manifest failure fails closed on article routes', async () => {
  const broken = { ASSETS: { fetch: async () => new Response('missing', { status: 404 }) } };
  const response = await handle(new Request(`https://vonpatglobalpt.net/${href}`), broken, release);
  assert.equal(response.status, 503);
});
