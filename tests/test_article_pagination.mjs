import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import vm from 'node:vm';

const source = readFileSync(new URL('../dist/app.js', import.meta.url), 'utf8').split('const views =')[0];
const articles = Array.from({ length: 19 }, (_, i) => ({
  title: `칼럼 ${i + 1}`, subtitle: '요약', category: '국내특허',
  href: `column-${i + 1}.html`, published: '2026-10-22',
}));

function render(search) {
  const context = {
    document: { body: { dataset: { page: 'knowledge' } } },
    window: { VON_ARTICLES: articles, location: { search } }, URLSearchParams,
  };
  return vm.runInNewContext(`${source}\nknowledgeListing(knowledge)`, context);
}

test('knowledge page shows nine newest cards and moves older cards to later pages', () => {
  const first = render('');
  const second = render('?page=2');
  const third = render('?page=3');
  assert.equal((first.match(/class="article-card"/g) || []).length, 9);
  assert.equal((second.match(/class="article-card"/g) || []).length, 9);
  assert.equal((third.match(/class="article-card"/g) || []).length, 1);
  assert.match(first, /column-1\.html/);
  assert.doesNotMatch(first, /column-10\.html/);
  assert.match(second, /column-10\.html/);
  assert.match(third, /column-19\.html/);
  assert.match(first, /knowledge\.html\?page=2/);
});
