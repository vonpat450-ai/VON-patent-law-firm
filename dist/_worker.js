// Cloudflare Pages: render future columns ahead of time, release them at 08:00 KST.
const MANIFEST_PATH = "/publication-schedule.json";

function cleanPath(pathname) {
  try {
    return decodeURIComponent(pathname).replace(/\/$/, "") || "/";
  } catch {
    return "";
  }
}

function pathsFor(entry) {
  const html = `/${entry.href}`;
  return [html, html.replace(/\.html$/, ""), `/${entry.source}`, entry.thumbnail ? `/${entry.thumbnail}` : ""];
}

function noStore(response) {
  const headers = new Headers(response.headers);
  headers.set("Cache-Control", "no-store, max-age=0");
  return new Response(response.body, { status: response.status, statusText: response.statusText, headers });
}

async function manifestFor(request, env) {
  const url = new URL(MANIFEST_PATH, request.url);
  const result = await env.ASSETS.fetch(new Request(url));
  if (!result.ok) throw new Error("Publication schedule is unavailable");
  const manifest = await result.json();
  if (manifest.version !== 1 || !Array.isArray(manifest.articles)) throw new Error("Invalid publication schedule");
  return manifest.articles;
}

export async function handle(request, env, nowMs = Date.now()) {
  const path = cleanPath(new URL(request.url).pathname);
  if (!path) return new Response("Not found", { status: 404 });
  if (path === MANIFEST_PATH) return new Response("Not found", { status: 404, headers: { "Cache-Control": "no-store" } });

  let entries;
  try {
    entries = await manifestFor(request, env);
  } catch {
    return new Response("Publication schedule unavailable", { status: 503, headers: { "Cache-Control": "no-store" } });
  }
  const hidden = entries.filter(entry => nowMs < Date.parse(entry.publish_at));
  if (path === "/column-release-status") {
    return new Response(JSON.stringify({ ready_dates: hidden.map(entry => entry.publish_at.slice(0, 10)) }), {
      headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store, max-age=0" },
    });
  }
  const scheduled = entries.find(entry => pathsFor(entry).includes(path));
  if (scheduled) {
    if (hidden.includes(scheduled)) {
      return new Response("Not found", { status: 404, headers: { "Cache-Control": "no-store", "X-Robots-Tag": "noindex" } });
    }
    return noStore(await env.ASSETS.fetch(request));
  }

  if (path === "/articles-data.js") {
    const response = await env.ASSETS.fetch(request);
    const text = await response.text();
    const prefix = "window.VON_ARTICLES=";
    if (!response.ok || !text.startsWith(prefix)) return new Response("Article listing unavailable", { status: 503 });
    try {
      const data = JSON.parse(text.slice(prefix.length).trim().replace(/;$/, ""));
      const hiddenHrefs = new Set(hidden.map(entry => entry.href));
      const visible = data.filter(article => !hiddenHrefs.has(article.href));
      return new Response(`${prefix}${JSON.stringify(visible)};\n`, {
        headers: { "Content-Type": "application/javascript; charset=utf-8", "Cache-Control": "no-store, max-age=0" },
      });
    } catch {
      return new Response("Article listing unavailable", { status: 503 });
    }
  }

  if (path === "/sitemap.xml") {
    const response = await env.ASSETS.fetch(request);
    if (!response.ok) return new Response("Sitemap unavailable", { status: 503 });
    let xml = await response.text();
    const hiddenPaths = new Set(hidden.map(entry => `/${entry.href.replace(/\.html$/, "")}`));
    xml = xml.replace(/<url>[\s\S]*?<\/url>/g, block => {
      const loc = block.match(/<loc>([^<]+)<\/loc>/)?.[1];
      return loc && hiddenPaths.has(new URL(loc).pathname) ? "" : block;
    });
    return new Response(xml, { headers: { "Content-Type": "application/xml; charset=utf-8", "Cache-Control": "no-store, max-age=0" } });
  }

  return env.ASSETS.fetch(request);
}

export default {
  fetch(request, env) {
    return handle(request, env);
  },
};
