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
Path('preview-v89.html').write_text(s,encoding='utf-8')
print('built preview-v89.html')
