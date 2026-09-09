from pathlib import Path
s=Path('index.html').read_text(encoding='utf-8')
s=s.replace('<title>GTVI 26 Weather App · Mobile v86</title>','<title>GTVI 26 Weather App · Mobile v87 Preview</title>',1)
old='''  font-size:14px;\n  font-weight:850;\n  font-variant-numeric:tabular-nums;'''
new='''  font-size:11px;\n  font-weight:850;\n  font-variant-numeric:tabular-nums;'''
if old not in s:
    raise SystemExit('factTimeInput font-size anchor not found')
s=s.replace(old,new,1)
# iOS/Safari can size the native datetime edit fields independently; force the smaller size there too.
s=s.replace('''.factTimeInput::-webkit-datetime-edit{\n  color:#ffffff;''','''.factTimeInput::-webkit-datetime-edit{\n  font-size:11px;\n  color:#ffffff;''',1)
s=s.replace('''.factTimeInput::-webkit-datetime-edit-fields-wrapper{\n  color:#ffffff;''','''.factTimeInput::-webkit-datetime-edit-fields-wrapper{\n  font-size:11px;\n  color:#ffffff;''',1)
Path('preview-v87.html').write_text(s,encoding='utf-8')
print('built preview-v87.html')
