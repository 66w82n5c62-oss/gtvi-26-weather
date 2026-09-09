from pathlib import Path
s=Path('preview-v89.html').read_text(encoding='utf-8')
s=s.replace('<title>GTVI 26 Weather App · Mobile v89 Preview</title>','<title>GTVI 26 Weather App · Mobile v90 Preview</title>',1)

# Make refresh control able to show a coasting bicycle wheel.
s=s.replace('<button id="refresh" class="refresh">↻ Refresh</button>', '<button id="refresh" class="refresh"><span class="refreshLabel">↻ Refresh</span></button>', 1)

css=r'''
/* v90: bicycle feedback for refresh and day selection */
.refresh{display:inline-flex;align-items:center;justify-content:center;gap:7px;min-width:92px}
.refreshWheel{width:22px;height:22px;display:inline-block;flex:0 0 22px;transform-origin:50% 50%}
.refreshWheel svg{display:block;width:22px;height:22px}
.refreshWheel circle,.refreshWheel line{stroke:#06101b;fill:none;stroke-width:1.7;stroke-linecap:round}
'''
s=s.replace('</style>', css+'\n</style>', 1)

# Add lightweight WebAudio bicycle gear-change sound and coasting wheel animation before buildDays.
anchor='function buildDays(){\n'
insert=r'''let bikeAudioCtx=null;
function playGearShiftSound(){
 try{
   const AC=window.AudioContext||window.webkitAudioContext;
   if(!AC)return;
   const ctx=bikeAudioCtx||(bikeAudioCtx=new AC());
   if(ctx.state==='suspended')ctx.resume();
   const t=ctx.currentTime;
   const out=ctx.createGain();
   out.gain.setValueAtTime(0.0001,t);
   out.gain.exponentialRampToValueAtTime(0.12,t+0.008);
   out.gain.exponentialRampToValueAtTime(0.0001,t+0.20);
   out.connect(ctx.destination);

   // Two short metallic derailleur/cassette clicks.
   [0,0.055].forEach((d,i)=>{
     const osc=ctx.createOscillator(),g=ctx.createGain(),bp=ctx.createBiquadFilter();
     osc.type='square';
     osc.frequency.setValueAtTime(i?760:980,t+d);
     osc.frequency.exponentialRampToValueAtTime(i?520:650,t+d+0.045);
     bp.type='bandpass';bp.frequency.value=1450;bp.Q.value=1.4;
     g.gain.setValueAtTime(0.0001,t+d);
     g.gain.exponentialRampToValueAtTime(i?0.18:0.24,t+d+0.004);
     g.gain.exponentialRampToValueAtTime(0.0001,t+d+0.07);
     osc.connect(bp);bp.connect(g);g.connect(out);osc.start(t+d);osc.stop(t+d+0.08);
   });

   // Brief chain rasp to make the click read as a bicycle gear change.
   const len=Math.max(1,Math.floor(ctx.sampleRate*0.11)),buf=ctx.createBuffer(1,len,ctx.sampleRate),data=buf.getChannelData(0);
   for(let i=0;i<len;i++)data[i]=(Math.random()*2-1)*(1-i/len);
   const noise=ctx.createBufferSource(),hp=ctx.createBiquadFilter(),ng=ctx.createGain();
   noise.buffer=buf;hp.type='highpass';hp.frequency.value=1800;ng.gain.value=0.035;
   noise.connect(hp);hp.connect(ng);ng.connect(out);noise.start(t+0.018);noise.stop(t+0.13);
 }catch(e){}
}
function refreshWheelMarkup(){
 return `<span class="refreshWheel" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="1.3"/><line x1="12" y1="3" x2="12" y2="10.7"/><line x1="12" y1="13.3" x2="12" y2="21"/><line x1="3" y1="12" x2="10.7" y2="12"/><line x1="13.3" y1="12" x2="21" y2="12"/><line x1="5.6" y1="5.6" x2="10.9" y2="10.9"/><line x1="13.1" y1="13.1" x2="18.4" y2="18.4"/><line x1="18.4" y1="5.6" x2="13.1" y2="10.9"/><line x1="10.9" y1="13.1" x2="5.6" y2="18.4"/></svg></span>`;
}
function startRefreshWheel(){
 const b=document.getElementById('refresh');
 if(!b)return null;
 b.innerHTML=refreshWheelMarkup()+'<span class="refreshLabel">Refreshing…</span>';
 const wheel=b.querySelector('.refreshWheel');
 if(wheel&&wheel.animate){
   return wheel.animate([{transform:'rotate(0deg)'},{transform:'rotate(1800deg)'}],{duration:3000,easing:'cubic-bezier(.12,.72,.18,1)',fill:'forwards'});
 }
 return null;
}
function stopRefreshWheel(){
 const b=document.getElementById('refresh');
 if(b)b.innerHTML='<span class="refreshLabel">↻ Refresh</span>';
}

'''
if anchor not in s:
    raise SystemExit('buildDays anchor not found')
s=s.replace(anchor,insert+anchor,1)

old='''   b.onclick=()=>{activeKey=key;render(false)};'''
new='''   b.onclick=()=>{if(key===activeKey)return;playGearShiftSound();activeKey=key;render(false)};'''
if old not in s:
    raise SystemExit('day click anchor not found')
s=s.replace(old,new,1)

old_refresh='''document.getElementById("refresh").onclick=()=>{
 const b=document.getElementById("refresh");
 b.textContent="↻ Refreshing…";
 render(true).finally(()=>{ if(!document.getElementById("outlook").textContent.includes("Loading")) b.textContent="↻ Refresh"; });
};'''
new_refresh='''document.getElementById("refresh").onclick=()=>{
 startRefreshWheel();
 render(true).finally(()=>{stopRefreshWheel();});
};'''
if old_refresh not in s:
    raise SystemExit('refresh handler anchor not found')
s=s.replace(old_refresh,new_refresh,1)

Path('preview-v90.html').write_text(s,encoding='utf-8')
print('built preview-v90.html')
