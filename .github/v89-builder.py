from pathlib import Path
s=Path('preview-v88.html').read_text(encoding='utf-8')
s=s.replace('<title>GTVI 26 Weather App · Mobile v88 Preview</title>','<title>GTVI 26 Weather App · Mobile v89 Preview</title>',1)
old='return `<svg viewBox="0 0 48 48" aria-hidden="true" style="width:1em;height:1em;vertical-align:-.14em">${wheel}'
new='return `<svg class="rainIntensityWxIcon" viewBox="0 0 48 48" aria-hidden="true">${wheel}'
if old not in s:
    raise SystemExit('rain icon svg anchor not found')
s=s.replace(old,new,1)
css='''\n/* v89: keep custom rain/shower icons at the same visual scale as the other weather icons on every stage. */\n.wxIcon .rainIntensityWxIcon{\n  width:40px;\n  height:40px;\n  display:block;\n  flex:0 0 40px;\n}\n@media(max-width:370px){\n  .wxIcon .rainIntensityWxIcon{width:37px;height:37px;flex-basis:37px}\n}\n'''
anchor='</style>'
if anchor not in s:
    raise SystemExit('style end anchor not found')
s=s.replace(anchor,css+anchor,1)
old_today='''function setToday(){\n const n=new Date();\n if(n.getFullYear()===2026&&n.getMonth()===8){\n   const map={12:"D1",13:"D2",14:"D3",15:"D4",16:"D5A",17:"D6",18:"D7"};\n   if(map[n.getDate()])activeKey=map[n.getDate()];\n }\n}\nsetToday();'''
new_today='''function setToday(){\n try{\n   const parts=new Intl.DateTimeFormat("en-CA",{timeZone:"Europe/Vienna",year:"numeric",month:"2-digit",day:"2-digit"}).formatToParts(new Date());\n   const o={};parts.forEach(p=>{if(p.type!=="literal")o[p.type]=p.value});\n   const iso=`${o.year}-${o.month}-${o.day}`;\n   const map={\n     "2026-09-12":"D1",\n     "2026-09-13":"D2",\n     "2026-09-14":"D3",\n     "2026-09-15":"D4",\n     "2026-09-16":"D5A",\n     "2026-09-17":"D6",\n     "2026-09-18":"D7"\n   };\n   if(map[iso])activeKey=map[iso];\n }catch(e){}\n}\nsetToday();'''
if old_today not in s:
    raise SystemExit('setToday anchor not found')
s=s.replace(old_today,new_today,1)
Path('preview-v89.html').write_text(s,encoding='utf-8')
print('built preview-v89.html')
