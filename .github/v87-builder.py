from pathlib import Path

s=Path('index.html').read_text(encoding='utf-8')
s=s.replace('<title>GTVI 26 Weather App · Mobile v86</title>','<title>GTVI 26 Weather App · Mobile v87 Preview</title>',1)

# Make the actual Wheels Rolling time field materially smaller, including iOS native subfields.
old='''  font-size:14px;\n  font-weight:850;\n  font-variant-numeric:tabular-nums;'''
new='''  font-size:10px;\n  font-weight:850;\n  font-variant-numeric:tabular-nums;'''
if old not in s:
    raise SystemExit('factTimeInput font-size anchor not found')
s=s.replace(old,new,1)
s=s.replace('''.factTimeInput::-webkit-datetime-edit{\n  color:#ffffff;''','''.factTimeInput::-webkit-datetime-edit{\n  font-size:10px;\n  color:#ffffff;''',1)
s=s.replace('''.factTimeInput::-webkit-datetime-edit-fields-wrapper{\n  color:#ffffff;''','''.factTimeInput::-webkit-datetime-edit-fields-wrapper{\n  font-size:10px;\n  color:#ffffff;''',1)
s=s.replace('''.factTimeInput::-webkit-datetime-edit-hour-field,\n.factTimeInput::-webkit-datetime-edit-minute-field,\n.factTimeInput::-webkit-datetime-edit-text{\n  color:#ffffff;''','''.factTimeInput::-webkit-datetime-edit-hour-field,\n.factTimeInput::-webkit-datetime-edit-minute-field,\n.factTimeInput::-webkit-datetime-edit-text{\n  font-size:10px;\n  color:#ffffff;''',1)

# Derive light/moderate/heavy rain/showers from the same point consensus used elsewhere.
anchor='function renderTimelineFromBundles(bundles,s){'
helper='''function consensusPrecipCondition(b,cp){\n const rs=b.forecasts.filter(Boolean);\n const need=Math.max(1,Math.ceil(rs.length/2));\n const thunder=rs.filter(r=>r.code>=95).length>=need;\n if(thunder)return {code:95,text:"Thunderstorms",wet:true};\n const showerVotes=rs.filter(r=>r.code>=80&&r.code<=82).length;\n const rainVotes=rs.filter(r=>r.code>=51&&r.code<=67).length;\n const wetVotes=rs.filter(wet).length;\n if(wetVotes<need && !(Number.isFinite(cp.precip)&&cp.precip>=0.2))return {code:rs[0]?.code??3,text:WDESC[rs[0]?.code??3]||"Dry",wet:false};\n const p=Number.isFinite(cp.precip)?cp.precip:0;\n const intensity=p>=2.5?"Heavy":p>=0.5?"Moderate":"Light";\n const shower=showerVotes>=rainVotes;\n const code=shower?(intensity==="Heavy"?82:intensity==="Moderate"?81:80):(intensity==="Heavy"?65:intensity==="Moderate"?63:61);\n return {code,text:`${intensity} ${shower?"showers":"rain"}`,wet:true};\n}\n\n'''
if anchor not in s:
    raise SystemExit('timeline anchor not found')
s=s.replace(anchor,helper+anchor,1)

old_cond=''' const wetN=rs.filter(wet).length,need=Math.max(1,Math.ceil(rs.length/2)),thunderN=rs.filter(x=>x.code>=95).length,thunder=thunderN>=need,wetConsensus=wetN>=need;\n const code=thunder?95:wetConsensus?80:wetN>0?80:disp.code,cond=thunder?"Thunder":wetConsensus?"Rain/showers":wetN>0?"Possible shower":WDESC[code]||"Dry",cclass=thunder?"danger":wetConsensus?"rainWet":"";'''
new_cond=''' const precipCond=consensusPrecipCondition(b,cp),code=precipCond.code,cond=precipCond.text,cclass=code>=95?"danger":precipCond.wet?"rainWet":"";'''
if old_cond not in s:
    raise SystemExit('condition block anchor not found')
s=s.replace(old_cond,new_cond,1)

about='''      <li><b>Along-the-way headline values</b> use the consensus of ECMWF, DWD ICON and GFS at that route point; individual model values remain under show detail. Rain probability also uses ECMWF ensemble probability where available.</li>'''
if about in s:
    s=s.replace(about,about+'\n      <li><b>Rain wording and icon</b> use that same consensus precipitation signal: light, moderate or heavy rain/showers, with thunderstorms taking priority.</li>',1)

Path('preview-v87.html').write_text(s,encoding='utf-8')
print('built preview-v87.html')
