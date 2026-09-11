const HOST = "gtvi-26-weather.pages.dev";
const COOKIE_NAME = "gtvi_usage_session";

function cookieValue(request, name) {
  const cookies = request.headers.get("Cookie") || "";
  for (const part of cookies.split(";")) {
    const i = part.indexOf("=");
    if (i < 0) continue;
    if (part.slice(0, i).trim() === name) return part.slice(i + 1).trim();
  }
  return "";
}

async function hmacKey(secret) {
  return crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["verify"]
  );
}

function unbase64url(s) {
  s = s.replace(/-/g, "+").replace(/_/g, "/");
  while (s.length % 4) s += "=";
  const raw = atob(s);
  const out = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) out[i] = raw.charCodeAt(i);
  return out;
}

async function authorised(request, env) {
  if (!env.USAGE_PASSWORD) return false;
  const token = cookieValue(request, COOKIE_NAME);
  const parts = token.split(".");
  if (parts.length !== 3 || parts[0] !== "v1") return false;
  const expires = Number(parts[1]);
  if (!Number.isFinite(expires) || expires <= Date.now()) return false;
  try {
    return await crypto.subtle.verify(
      "HMAC",
      await hmacKey(env.USAGE_PASSWORD),
      unbase64url(parts[2]),
      new TextEncoder().encode(`${parts[0]}.${parts[1]}`)
    );
  } catch {
    return false;
  }
}

function isoAgo(days) {
  return new Date(Date.now() - days * 86400000).toISOString();
}

function cleanRows(rows, dimension) {
  return (rows || []).map(row => ({
    label: row.dimensions?.[dimension] || "Unknown",
    pageViews: row.count || 0,
    visits: row.sum?.visits || 0
  }));
}

export async function onRequestGet(context) {
  const { request, env } = context;
  if (!(await authorised(request, env))) {
    return Response.json({ ok: false, message: "Session expired" }, {
      status: 401,
      headers: { "Cache-Control": "private, no-store" }
    });
  }

  if (!env.CF_ACCOUNT_ID || !env.CF_API_TOKEN) {
    return Response.json({
      ok: false,
      setupRequired: true,
      message: "Set CF_ACCOUNT_ID and encrypted CF_API_TOKEN in Cloudflare Pages Variables and Secrets."
    }, { status: 503 });
  }

  const url = new URL(request.url);
  const requested = Number(url.searchParams.get("days") || 7);
  const days = [1, 7, 30].includes(requested) ? requested : 7;
  const start = isoAgo(days);
  const end = new Date().toISOString();

  const filter = `filter:{datetime_geq:${JSON.stringify(start)},datetime_leq:${JSON.stringify(end)},requestHost:${JSON.stringify(HOST)}}`;
  const query = `query Usage {
    viewer {
      accounts(filter:{accountTag:${JSON.stringify(env.CF_ACCOUNT_ID)}}) {
        total: rumPageloadEventsAdaptiveGroups(limit:1, ${filter}) { count sum { visits } }
        daily: rumPageloadEventsAdaptiveGroups(limit:40, orderBy:[date_ASC], ${filter}) { count sum { visits } dimensions { date } }
        countries: rumPageloadEventsAdaptiveGroups(limit:8, orderBy:[count_DESC], ${filter}) { count sum { visits } dimensions { countryName } }
        devices: rumPageloadEventsAdaptiveGroups(limit:8, orderBy:[count_DESC], ${filter}) { count sum { visits } dimensions { deviceType } }
        browsers: rumPageloadEventsAdaptiveGroups(limit:8, orderBy:[count_DESC], ${filter}) { count sum { visits } dimensions { userAgentBrowser } }
        paths: rumPageloadEventsAdaptiveGroups(limit:8, orderBy:[count_DESC], ${filter}) { count sum { visits } dimensions { requestPath } }
      }
    }
  }`;

  let response;
  try {
    response = await fetch("https://api.cloudflare.com/client/v4/graphql", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${env.CF_API_TOKEN}`,
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify({ query })
    });
  } catch (error) {
    return Response.json({ ok: false, message: "Could not reach Cloudflare Analytics API.", detail: String(error) }, { status: 502 });
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.errors?.length) {
    return Response.json({
      ok: false,
      message: "Cloudflare Analytics API returned an error.",
      detail: payload.errors || payload
    }, { status: response.status || 502 });
  }

  const account = payload.data?.viewer?.accounts?.[0];
  if (!account) {
    return Response.json({ ok: false, message: "No analytics account data was returned." }, { status: 502 });
  }

  const total = account.total?.[0] || {};
  return Response.json({
    ok: true,
    host: HOST,
    days,
    generatedAt: end,
    pageViews: total.count || 0,
    visits: total.sum?.visits || 0,
    daily: (account.daily || []).map(row => ({
      date: row.dimensions?.date,
      pageViews: row.count || 0,
      visits: row.sum?.visits || 0
    })),
    countries: cleanRows(account.countries, "countryName"),
    devices: cleanRows(account.devices, "deviceType"),
    browsers: cleanRows(account.browsers, "userAgentBrowser"),
    paths: cleanRows(account.paths, "requestPath")
  }, {
    headers: {
      "Cache-Control": "private, no-store",
      "Content-Type": "application/json; charset=utf-8"
    }
  });
}
