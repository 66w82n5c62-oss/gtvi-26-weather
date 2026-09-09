from pathlib import Path
s=Path('preview-v87.html').read_text(encoding='utf-8')
s=s.replace('<title>GTVI 26 Weather App · Mobile v87 Preview</title>','<title>GTVI 26 Weather App · Mobile v88 Preview</title>',1)
old='const WICON=c=>c>=95?"⛈️":c>=80?cycleSunRainIcon():c>=61?"🌧️":c>=51?cycleSunRainIcon():c>=45?"🌫️":c===0?cycleSunIcon(false):c<=2?cycleSunIcon(true):"☁️";'
new=r'''function rainIntensityIcon(showery,intensity){
  const n=Math.max(1,Math.min(3,intensity||1));
  const drops=[
    '<path d="M24 31 C22.8 33 22.9 35 24 36.1 C25.1 35 25.2 33 24 31 Z"/>',
    '<path d="M17 31 C15.8 33 15.9 35 17 36.1 C18.1 35 18.2 33 17 31 Z"/><path d="M31 31 C29.8 33 29.9 35 31 36.1 C32.1 35 32.2 33 31 31 Z"/>',
    '<path d="M14 30 C12.6 32.4 12.7 35 14 36.4 C15.3 35 15.4 32.4 14 30 Z"/><path d="M24 31 C22.6 33.4 22.7 36 24 37.4 C25.3 36 25.4 33.4 24 31 Z"/><path d="M34 30 C32.6 32.4 32.7 35 34 36.4 C35.3 35 35.4 32.4 34 30 Z"/>'
  ][n-1];
  const wheel=showery?`<g fill="none" stroke="#f2c75c" stroke-width="1.7" stroke-linecap="round" opacity=".95"><circle cx="14" cy="14" r="7"/><circle cx="14" cy="14" r="2.2"/><path d="M14 4V8M14 20V24M4 14H8M20 14H24M7 7L10 10M18 18L21 21M21 7L18 10M10 18L7 21"/></g>`:'';
  const cloudFill=n===3?'#8193a3':n===2?'#9aaaba':'#b7c5d1';
  return `<svg viewBox="0 0 48 48" aria-hidden="true" style="width:1em;height:1em;vertical-align:-.14em">${wheel}<g><path d="M14 27c0-4.7 3.8-8.5 8.5-8.5 3.2 0 6 1.8 7.5 4.4.8-.4 1.8-.6 2.8-.6 3.7 0 6.7 2.9 6.7 6.5S36.5 35 32.8 35H15.7C11.4 35 8 31.8 8 27.9c0-3.3 2.4-6 5.7-6.8.1 0 .2 0 .3-.1" fill="${cloudFill}" stroke="#dce7ef" stroke-width="1.2"/></g><g fill="#65bff1">${drops}</g></svg>`;
}
const WICON=c=>c>=95?"⛈️":c===82?rainIntensityIcon(true,3):c===81?rainIntensityIcon(true,2):c>=80?rainIntensityIcon(true,1):c>=65?rainIntensityIcon(false,3):c>=63?rainIntensityIcon(false,2):c>=61?rainIntensityIcon(false,1):c>=51?rainIntensityIcon(false,1):c>=45?"🌫️":c===0?cycleSunIcon(false):c<=2?cycleSunIcon(true):"☁️";'''
if old not in s:
    raise SystemExit('WICON anchor not found')
s=s.replace(old,new,1)
Path('preview-v88.html').write_text(s,encoding='utf-8')
print('built preview-v88.html')
