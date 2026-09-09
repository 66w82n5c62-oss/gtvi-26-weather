from pathlib import Path

s=Path('preview-v84.html').read_text(encoding='utf-8')
s=s.replace('<title>GTVI 26 Weather App · Mobile v84 Preview</title>','<title>GTVI 26 Weather App · Mobile v85 Preview</title>',1)

js='''
<script>
(function(){
  const reduced=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(reduced)return;
  const el=document.getElementById('alongHighlights');
  if(!el)return;
  let timer=null, resumeTimer=null, interacting=false;
  function cards(){return Array.from(el.querySelectorAll('.alongHighlight'));}
  function nearestIndex(items){
    if(!items.length)return 0;
    let best=0,dist=Infinity;
    for(let i=0;i<items.length;i++){
      const d=Math.abs(items[i].offsetLeft-el.scrollLeft);
      if(d<dist){dist=d;best=i;}
    }
    return best;
  }
  function advance(){
    if(interacting)return;
    const items=cards();
    if(items.length<2)return;
    const i=nearestIndex(items);
    const n=(i+1)%items.length;
    el.scrollTo({left:items[n].offsetLeft,behavior:'smooth'});
  }
  function start(){
    if(interacting)return;
    clearInterval(timer);
    timer=setInterval(advance,3600);
  }
  function hold(){
    interacting=true;
    clearInterval(timer);
    clearTimeout(resumeTimer);
  }
  function release(){
    interacting=false;
    clearTimeout(resumeTimer);
    resumeTimer=setTimeout(start,5000);
  }
  el.addEventListener('touchstart',hold,{passive:true});
  el.addEventListener('touchend',release,{passive:true});
  el.addEventListener('touchcancel',release,{passive:true});
  el.addEventListener('pointerdown',hold,{passive:true});
  window.addEventListener('pointerup',release,{passive:true});
  el.addEventListener('wheel',()=>{hold();release();},{passive:true});
  const mo=new MutationObserver(()=>{
    el.scrollTo({left:0,behavior:'auto'});
    start();
  });
  mo.observe(el,{childList:true});
  start();
})();
</script>
'''
if '</body>' not in s:
    raise SystemExit('body close not found')
s=s.replace('</body>',js+'\n</body>',1)
Path('preview-v85.html').write_text(s,encoding='utf-8')
print('built preview-v85.html')
