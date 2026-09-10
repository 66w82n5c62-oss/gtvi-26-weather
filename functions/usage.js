function unauthorized() {
  return new Response("Authentication required", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="GTVI Usage", charset="UTF-8"' }
  });
}

function authorised(request, env) {
  const header = request.headers.get("Authorization") || "";
  if (!header.startsWith("Basic ") || !env.USAGE_PASSWORD) return false;
  try {
    const decoded = atob(header.slice(6));
    const split = decoded.indexOf(":");
    const user = split >= 0 ? decoded.slice(0, split) : "";
    const pass = split >= 0 ? decoded.slice(split + 1) : "";
    return user === "gtvi" && pass === env.USAGE_PASSWORD;
  } catch {
    return false;
  }
}

const HTML = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#081522">
<title>GTVI 26 · Usage</title>
<style>
:root{--bg:#081522;--card:#102237;--card2:#132a42;--line:#28445f;--text:#f4f8fc;--muted:#aebfcd;--blue:#58b7f4;--good:#87d7c8;--amber:#f1cc74}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.app{max-width:860px;margin:auto;padding:18px 14px 40px}.top{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:16px}.eyebrow{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:#9eb1c0;font-weight:800}.title{font-size:25px;font-weight:900;letter-spacing:-.03em;margin:3px 0}.sub{font-size:12px;color:var(--muted)}.back{color:var(--blue);text-decoration:none;font-size:12px;font-weight:800;padding:8px 0}.range{display:flex;gap:6px;margin:0 0 13px}.range button{border:1px solid var(--line);background:#0d2134;color:#c9d7e2;border-radius:999px;padding:7px 11px;font-weight:800;font-size:12px;cursor:pointer}.range button.active{background:#1b466b;border-color:var(--blue);color:white}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}.card{background:var(--card);border:1px solid #213d58;border-radius:14px;padding:12px}.metricLabel{font-size:9px;text-transform:uppercase;letter-spacing:.08em;color:#9eb1c0;font-weight:800}.metricValue{font-size:28px;font-weight:900;margin-top:4px}.metricNote{font-size:10px;color:var(--muted);margin-top:3px}.section{margin-top:12px}.sectionTitle{font-size:13px;font-weight:850;margin:0 0 7px}.chart{height:158px;display:flex;align-items:flex-end;gap:5px;padding-top:10px}.barCol{flex:1;min-width:0;height:100%;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:4px}.barWrap{height:118px;width:100%;display:flex;align-items:flex-end;justify-content:center}.bar{width:min(22px,70%);background:var(--blue);border-radius:4px 4px 2px 2px;min-height:2px}.barDate{font-size:8px;color:#879aaa;white-space:nowrap}.split{display:grid;grid-template-columns:1fr 1fr;gap:8px}.list{display:flex;flex-direction:column;gap:7px}.row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:center}.rowName{font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.rowNum{font-size:11px;font-weight:850}.track{height:4px;background:#193148;border-radius:999px;margin-top:4px;overflow:hidden}.fill{height:100%;background:#65bff1;border-radius:999px}.status{margin-top:12px;font-size:11px;color:var(--muted);line-height:1.45}.error{background:#3a2528;border:1px solid #704149;color:#ffd1c7;border-radius:12px;padding:11px;font-size:12px;line-height:1.45}.hidden{display:none}@media(max-width:620px){.grid{grid-template-columns:1fr 1fr}.grid .card:last-child{grid-column:1/-1}.split{grid-template-columns:1fr}.title{font-size:22px}.chart{gap:3px}}
</style>
</head>
<body>
<main class="app">
  <div class="top">
    <div><div class="eyebrow">Private dashboard</div><div class="title">GTVI 26 Usage</div><div class="sub">Cloudflare Web Analytics · gtvi-26-weather.pages.dev</div></div>
    <a class="back" href="/">Weather app ↗</a>
  </div>
  <div class="range" aria-label="Time range"><button data-days="1">24 h</button><button class="active" data-days="7">7 days</button><button data-days="30">30 days</button></div>
  <div id="error" class="error hidden"></div>
  <div id="content">
    <div class="grid">
      <section class="card"><div class="metricLabel">Page views</div><div class="metricValue" id="views">—</div><div class="metricNote" id="viewsNote">Selected period</div></section>
      <section class="card"><div class="metricLabel">Visits</div><div class="metricValue" id="visits">—</div><div class="metricNote">Cloudflare visit estimate</div></section>
      <section class="card"><div class="metricLabel">Views / visit</div><div class="metricValue" id="ratio">—</div><div class="metricNote">Engagement indicator</div></section>
    </div>
    <section class="card section"><div class="sectionTitle">Daily usage</div><div id="chart" class="chart" aria-label="Daily page views"></div></section>
    <div class="split section">
      <section class="card"><div class="sectionTitle">Countries</div><div id="countries" class="list"></div></section>
      <section class="card"><div class="sectionTitle">Devices</div><div id="devices" class="list"></div></section>
      <section class="card"><div class="sectionTitle">Browsers</div><div id="browsers" class="list"></div></section>
      <section class="card"><div class="sectionTitle">Top pages</div><div id="paths" class="list"></div></section>
    </div>
    <div class="status" id="status">Loading analytics…</div>
  </div>
</main>
<script>
(function(){
  var buttons=Array.from(document.querySelectorAll('[data-days]'));
  var fmt=new Intl.NumberFormat('en-GB');
  function setError(message){document.getElementById('error').textContent=message;document.getElementById('error').classList.remove('hidden');document.getElementById('content').classList.add('hidden')}
  function renderList(id,rows){var el=document.getElementById(id);if(!rows||!rows.length){el.innerHTML='<div class="sub">No data yet</div>';return}var max=Math.max.apply(null,rows.map(function(r){return r.pageViews||0}).concat([1]));el.innerHTML=rows.map(function(r){var pct=Math.max(2,Math.round((r.pageViews||0)/max*100));return '<div><div class="row"><div class="rowName">'+escapeHtml(r.label)+'</div><div class="rowNum">'+fmt.format(r.pageViews||0)+'</div></div><div class="track"><div class="fill" style="width:'+pct+'%"></div></div></div>'}).join('')}
  function escapeHtml(s){return String(s==null?'':s).replace(/[&<>\"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function renderChart(rows){var el=document.getElementById('chart');if(!rows||!rows.length){el.innerHTML='<div class="sub">No page views recorded yet</div>';return}var max=Math.max.apply(null,rows.map(function(r){return r.pageViews||0}).concat([1]));el.innerHTML=rows.map(function(r){var h=Math.max(2,Math.round((r.pageViews||0)/max*110));var d=r.date?new Date(r.date+'T12:00:00Z').toLocaleDateString('en-GB',{day:'numeric',month:'short'}):'';return '<div class="barCol" title="'+escapeHtml(d)+': '+fmt.format(r.pageViews||0)+' views"><div class="barWrap"><div class="bar" style="height:'+h+'px"></div></div><div class="barDate">'+escapeHtml(d)+'</div></div>'}).join('')}
  async function load(days){buttons.forEach(function(b){b.classList.toggle('active',Number(b.dataset.days)===days)});document.getElementById('status').textContent='Loading analytics…';document.getElementById('error').classList.add('hidden');document.getElementById('content').classList.remove('hidden');try{var r=await fetch('/api/usage?days='+days,{credentials:'same-origin',cache:'no-store'});var data=await r.json();if(!r.ok||!data.ok)throw new Error(data.message||'Analytics request failed');document.getElementById('views').textContent=fmt.format(data.pageViews||0);document.getElementById('visits').textContent=fmt.format(data.visits||0);document.getElementById('ratio').textContent=data.visits?((data.pageViews||0)/data.visits).toFixed(1):'—';document.getElementById('viewsNote').textContent=days===1?'Past 24 hours':'Past '+days+' days';renderChart(data.daily);renderList('countries',data.countries);renderList('devices',data.devices);renderList('browsers',data.browsers);renderList('paths',data.paths);var stamp=new Date(data.generatedAt).toLocaleString('en-GB',{dateStyle:'medium',timeStyle:'short'});document.getElementById('status').textContent='Updated '+stamp+' · Analytics begins from the point Web Analytics was enabled; earlier visits are not reconstructed.'}catch(e){setError(e.message+' If this is the first setup, add the three Cloudflare variables described in the setup instructions.') }}
  buttons.forEach(function(b){b.addEventListener('click',function(){load(Number(b.dataset.days))})});load(7);
})();
</script>
</body>
</html>`;

export async function onRequestGet(context) {
  if (!authorised(context.request, context.env)) return unauthorized();
  return new Response(HTML, {
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "private, no-store",
      "X-Robots-Tag": "noindex, nofollow"
    }
  });
}
