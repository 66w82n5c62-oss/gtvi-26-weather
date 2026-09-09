from pathlib import Path
import re

src = Path('index.html')
out = Path('preview-v84.html')
s = src.read_text(encoding='utf-8')

s = s.replace('<title>GTVI 26 Weather App · Mobile v80</title>', '<title>GTVI 26 Weather App · Mobile v84 Preview</title>', 1)

m = re.search(r'<input[^>]*id="startTime"[^>]*>', s)
if not m:
    raise SystemExit('startTime input not found')
tag = m.group(0)
value = re.search(r'value="([^"]+)"', tag)
default = value.group(1) if value else '08:30'
classes = re.search(r'class="([^"]+)"', tag)
klass = classes.group(1) if classes else 'mobileTimeInput'
new_tag = f'<input id="startTime" class="{klass}" type="text" inputmode="numeric" value="{default}" aria-label="Wheels rolling time">'
s = s.replace(tag, new_tag, 1)

old = 'temperature_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_gusts_10m,wind_direction_10m'
if old not in s:
    raise SystemExit('hourly field list not found')
s = s.replace(old, old + ',cloud_cover', 1)

old_row = 'gust:num(h.wind_gusts_10m?.[i])??0,wdir:num(h.wind_direction_10m?.[i])};'
new_row = 'gust:num(h.wind_gusts_10m?.[i])??0,wdir:num(h.wind_direction_10m?.[i]),cloud:num(h.cloud_cover?.[i])};'
if s.count(old_row) < 2:
    raise SystemExit('row/consensus row anchors not found')
s = s.replace(old_row, new_row, 2)

old_summary = 'const temp=temps.length?temps.reduce((a,c)=>a+c,0)/temps.length:(Number.isFinite(disp.temp)?disp.temp:null);const a=pointArrivalMinutes(b.p,s);return {km:b.p.km,time:a.time,rainProb,precip:meanPrecip,gust,temp}}'
new_summary = 'const temp=temps.length?temps.reduce((a,c)=>a+c,0)/temps.length:(Number.isFinite(disp.temp)?disp.temp:null);const clouds=rs.map(x=>x.cloud).filter(Number.isFinite);const cloud=clouds.length?clouds.reduce((a,c)=>a+c,0)/clouds.length:(Number.isFinite(disp.cloud)?disp.cloud:null);const a=pointArrivalMinutes(b.p,s);return {km:b.p.km,time:a.time,rainProb,precip:meanPrecip,gust,temp,cloud}}'
if old_summary not in s:
    raise SystemExit('bundleSummaryPoint anchor not found')
s = s.replace(old_summary, new_summary, 1)

start = s.find('function renderWorstHighlights(bundles,s){')
end = s.find('function changeText(', start)
if start < 0 or end < 0:
    raise SystemExit('renderWorstHighlights block not found')
new_fn = '''function renderWorstHighlights(bundles,s){
 const el=document.getElementById("alongHighlights");if(!el)return;
 const pts=bundles.map(b=>bundleSummaryPoint(b,s)).filter(Boolean);
 if(!pts.length){el.innerHTML="";return}
 const validTemp=pts.filter(p=>Number.isFinite(p.temp));
 const validCloud=pts.filter(p=>Number.isFinite(p.cloud));
 const coldest=validTemp.length?validTemp.reduce((a,p)=>p.temp<a.temp?p:a):null;
 const warmest=validTemp.length?validTemp.reduce((a,p)=>p.temp>a.temp?p:a):null;
 const sunniest=validCloud.length?validCloud.reduce((a,p)=>p.cloud<a.cloud?p:a):null;
 const wettest=pts.reduce((a,p)=>{const score=(Number.isFinite(p.rainProb)?p.rainProb:0)+(Number.isFinite(p.precip)?p.precip*20:0);return !a||score>a.score?{...p,score}:a},null);
 const windiest=pts.reduce((a,p)=>!a||p.gust>a.gust?p:a,null);
 const card=(label,p,detail)=>p?`<div class="alongHighlight"><b>${label}</b>${p.time} · around ${Math.round(p.km)} km · ${detail}</div>`:"";
 const wetDetail=(Number.isFinite(wettest.rainProb)&&wettest.rainProb>0)?`${Math.round(wettest.rainProb)}% rain`:(wettest.precip>=0.1?`${wettest.precip.toFixed(1)} mm/h`:"little rain signal");
 el.innerHTML=[
   card("Coldest",coldest,`${Math.round(coldest?.temp)}°C`),
   card("Warmest",warmest,`${Math.round(warmest?.temp)}°C`),
   card("Sunniest",sunniest,`${Math.round(100-sunniest?.cloud)}% clear-sky signal`),
   card("Wettest",wettest,wetDetail),
   card("Windiest",windiest,`gust ${Math.round(windiest?.gust)} km/h`)
 ].join("");
}
'''
s = s[:start] + new_fn + s[end:]

css = r'''
/* v84: iOS Wheels Rolling fit, brighter controls and scrollable ride highlights */
.mobileTimeInput{font-size:12px!important;padding:0 4px!important;letter-spacing:0!important;text-align:center!important;-webkit-appearance:none!important;appearance:none!important}

/* Forecast spread: slightly larger and whiter */
.mobileRiskDisclosure>summary{font-size:12px!important;color:#edf4fa!important}
.forecastSources{font-size:10px!important;color:#cbd7e1!important}
.forecastSources span{color:#edf4fa!important}
.riskTitle{font-size:11px!important;color:#e6eef5!important}
.riskSource{font-size:10px!important;color:#c8d5df!important}
.riskRowTitle{font-size:10.5px!important;color:#d6e0e8!important}
.riskMain{font-size:14px!important;color:#f4f8fc!important}
.riskDetail{font-size:10px!important;color:#d3dee7!important}
.riskChip{font-size:10px!important;color:#d8e3eb!important}

/* Ride Plan: slightly larger and whiter */
.mobileRidePlan>summary{font-size:12px!important;color:#edf4fa!important}
.mobileSectionHead{font-size:12px!important;color:#edf4fa!important}
.mobileLabel{font-size:10px!important;color:#d2dde6!important}
.komootNote{font-size:9.5px!important;color:#c7d3dd!important}
.mobileStat span{font-size:8.5px!important;color:#bdcad5!important}
.mobileStopFieldLabel{font-size:8.5px!important;color:#bdcad5!important}
.mobilePlanNote{font-size:9.5px!important;color:#c2ced8!important}

/* Swipeable ride highlights */
.alongHighlights{display:flex!important;gap:6px!important;overflow-x:auto!important;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch;scrollbar-width:none;margin:0 0 7px;padding-bottom:1px}
.alongHighlights::-webkit-scrollbar{display:none}
.alongHighlight{flex:0 0 72%;scroll-snap-align:start;font-size:10px!important;color:#edf5fb!important}
.alongHighlight b{font-size:10px!important;color:#9ed7fa!important}
@media(max-width:360px){.alongHighlight{flex-basis:84%}}
'''
s = s.replace('</style>', css + '\n</style>', 1)

out.write_text(s, encoding='utf-8')
print('built', out)
