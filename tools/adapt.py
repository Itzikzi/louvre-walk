# One-off: turns the British Museum template (louvre.html, copied from bm-map.html) into the Louvre app shell.
# Data lives between /* DATA-BEGIN */ and /* DATA-END */ and is written by tools/gen.py.
import re
f = '/Users/itzhakzilbershtein/louvre-walk/louvre.html'
s = open(f, encoding='utf-8').read()

def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (a[:90], c)
    s = s.replace(a, b)

# ---- data block -> markers
L = s.split('\n')
a = next(i for i, l in enumerate(L) if l.startswith('/* ---------- data'))
b = next(i for i, l in enumerate(L) if l.startswith('/* ---------- state'))
L[a:b] = ['/* DATA-BEGIN */', '/* DATA-END */', '']
s = '\n'.join(L)

# ---- head / header
rep('<title>מסלול מקראי במוזיאון הבריטי</title>', '<title>הלובר: מקרא ואמנות</title>')
rep('<h1>המוזיאון הבריטי</h1>', '<h1>הלובר</h1>')
rep('<span>מסלול מקראי</span><span id="clock">', '<span>מקרא, אמנות ותרבות</span><span id="clock">')
rep('Palette from the Standard of Ur: lapis, shell, carnelian, gold over limestone.', 'Palette kept from the British Museum app: lapis, carnelian, gold over limestone.')
rep('יום מלא 10:00–17:00', 'יום מלא 9:00–17:30')
rep('3 שעות 11:00–14:00', '3 שעות 9:00–12:00')

# ---- map card: 4 levels, official map only, horizontal scroll
rep('''    <div class="seg" role="group" aria-label="קומה" style="margin-bottom:8px;background:var(--room-ctx)">
      <button id="fl-0" aria-pressed="true">קומת קרקע</button>
      <button id="fl-1" aria-pressed="false">קומה עליונה</button>
    </div>
    <div class="seg mini" role="group" aria-label="סוג מפה" style="margin-bottom:8px">
      <button id="mm-real" aria-pressed="true">מפת המוזיאון</button>
      <button id="mm-plan" aria-pressed="false">מפה פשוטה</button>
    </div>
    <svg class="map" id="map" role="img" aria-label="תכנית סכמטית של הקומה"></svg>''',
'''    <div class="seg" role="group" aria-label="קומה" id="floors" style="margin-bottom:8px;background:var(--room-ctx)"></div>
    <div class="mapscroll" id="mapscroll"><svg class="map" id="map" role="img" aria-label="מפת הקומה הרשמית של הלובר עם תחנות המסלול"></svg></div>''')
rep('<span>מקווקו = שעות מוגבלות</span>', '<span>הסיכה מסמנת את אזור החדר · גוללים את המפה הצידה</span>')
rep('''<a class="lk" href="https://www.britishmuseum.org/sites/default/files/2026-05/British_Museum_map.pdf" target="_blank" rel="noopener">''',
    '''<a class="lk" href="https://api-www.louvre.fr/sites/default/files/2026-05/2026-05_Plan_Louvre_FR.pdf" target="_blank" rel="noopener">''')
rep('''id="mapCredit">מפה: <span class="ltr">© The Trustees of the British Museum, 03/2026</span></span>''',
    '''id="mapCredit">מפה: <span class="ltr">musée du Louvre, mai 2026</span></span>
      <a class="lk" href="https://collections.louvre.fr/plan" target="_blank" rel="noopener">מפה אינטראקטיבית</a>''')
rep('''<p class="foot-note">שעות החדרים לפי מפת המוזיאון 03/2026. לבדוק ביום הביקור בעמוד <a href="https://www.britishmuseum.org/visit" target="_blank" rel="noopener">Visit</a>.</p>''',
    '''<p class="foot-note">החדרים והסגירות לפי אתר הלובר, 21.11.2026. לבדוק ביום הביקור ברשימת <a href="https://www.louvre.fr/en/visit/list-of-available-galleries" target="_blank" rel="noopener">האולמות הפתוחים</a>.</p>''')
rep('.mapcard svg.map{width:100%;height:auto;display:block;direction:ltr;touch-action:manipulation}',
    '.mapscroll{overflow-x:auto;overflow-y:hidden;border-radius:14px;direction:ltr;-webkit-overflow-scrolling:touch;overscroll-behavior-x:contain;background:#fff}\n.mapcard svg.map{width:960px;max-width:none;height:auto;display:block;direction:ltr;touch-action:pan-x pan-y}\n.zone{fill:var(--ov-fill);stroke:var(--ov-stroke);stroke-width:3;cursor:pointer}\n.zone.done{fill:rgba(31,160,90,.30);stroke:#2bb673}\n.zone.closed{stroke:var(--carnelian);stroke-dasharray:5 4}')

# ---- state keys
rep("LS.get('bm-seen',[])", "LS.get('lv-seen',[])")
rep("LS.get('bm-route','full')", "LS.get('lv-route','full')")
rep("LS.get('bm-prefs',{})", "LS.get('lv-prefs',{})")
rep("LS.set('bm-seen'", "LS.set('lv-seen'")
rep("LS.set('bm-route'", "LS.set('lv-route'")
s = s.replace("LS.set('bm-prefs'", "LS.set('lv-prefs'")
rep("let floor=0, openId=null, mapMode=LS.get('bm-mapmode','real');", "let floor=0, openId=null;")

# ---- Paris time & status
a = s.index('/* London time & gallery status')
b = s.index('/* ---------- render ---------- */')
s = s[:a] + r'''/* Paris time & gallery status (louvre.fr, 21.11.2026): 9:00–18:00, Wed/Fri to 21:00, closed Tuesday; level 2 opens 10:30 on Wed/Fri */
function paris(){
  const p=Object.fromEntries(new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/Paris',weekday:'short',hour:'2-digit',minute:'2-digit',hourCycle:'h23',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date()).map(x=>[x.type,x.value]));
  return {wd:p.weekday,min:(+p.hour)*60+(+p.minute),hm:p.hour+':'+p.minute,ymd:`${p.year}-${p.month}-${p.day}`};
}
const lateDay=L=>L.wd==='Wed'||L.wd==='Fri';
function museumOpen(L){if(L.wd==='Tue')return false;const close=lateDay(L)?21*60:18*60;return L.min>=540&&L.min<close}
function closedNow(s,L){return (s.closed||[]).find(([from,to])=>L.ymd>=from&&L.ymd<=to)}
const dm=d=>d.slice(8).replace(/^0/,'')+'.'+d.slice(5,7).replace(/^0/,'');
function status(id){
  const s=STOPS[id],L=paris();
  const c=closedNow(s,L); if(c) return {cls:'bad',t:`סגור עד ${dm(c[1])}`};
  if(!museumOpen(L)) return null;
  if(s.floor===2&&lateDay(L)&&L.min<630) return {cls:'bad',t:'קומה 2 נפתחת ב-10:30'};
  return null;
}
function limitChip(id){const s=STOPS[id];return (s.closed||[]).map(([f,t,why])=>`<span class="chip info">${esc(why)}: ${dm(f)}–${dm(t)}</span>`).join('')}
const LEVEL_NAME={'-1':'מפלס ‎-1','0':'קומה 0','1':'קומה 1','2':'קומה 2'};

''' + s[b:]

# ---- clock & alerts
a = s.index('function renderClock(){')
b = s.index('function renderMap(){')
s = s[:a] + r'''function renderClock(){
  const L=paris();
  $('#clock').textContent=`פריז ${L.hm}${museumOpen(L)?'':' · המוזיאון סגור'}`;
  const a=[];
  if(L.wd==='Tue') a.push('היום יום שלישי: הלובר סגור.');
  if(lateDay(L)) a.push('היום פתוח עד 21:00. חדרי קומה 2 (ריבלייה 800, סולי 900) נפתחים רק ב-10:30.');
  if(L.ymd>='2026-12-19'&&L.ymd<='2027-01-04') a.push('19.12–4.1: חובה להזמין כרטיס עם שעת כניסה מראש.');
  route().forEach(([id])=>{const c=closedNow(STOPS[id],L);if(c)a.push(`${STOPS[id].title}: ${c[2]} עד ${dm(c[1])}.`)});
  $('#alert').innerHTML=a.map(t=>`<div class="alert glass">${I.warn}<span>${esc(t)}</span></div>`).join('');
}

''' + s[b:]

# ---- map
a = s.index('function renderMap(){')
b = s.index('function renderList(){')
s = s[:a] + r'''function renderMap(){
  const P=PLAN[floor],svg=$('#map'),[vx,vy,vw,vh]=P.vb;
  svg.setAttribute('viewBox',P.vb.join(' '));
  const r=route(), nx=nextStop(), L=paris();
  let h=`<image href="${P.img}" x="0" y="0" width="${P.w}" height="${P.h}"/>`;
  const pts=[];
  r.forEach(([id],i)=>{const s=STOPS[id];if(s.floor===floor)pts.push({id,i,c:s.pos})});
  Object.entries(STOPS).forEach(([id,s])=>{if(s.floor!==floor||routeIdx(id)<0)return;
    const cl=['zone'];if(stopDone(id))cl.push('done');if(closedNow(s,L))cl.push('closed');
    h+=`<circle class="${cl.join(' ')}" data-stop="${id}" cx="${s.pos[0]}" cy="${s.pos[1]}" r="24"><title>${esc(s.title)}</title></circle>`});
  for(let k=1;k<pts.length;k++) if(pts[k].i===pts[k-1].i+1) h+=`<line class="route" x1="${pts[k-1].c[0]}" y1="${pts[k-1].c[1]}" x2="${pts[k].c[0]}" y2="${pts[k].c[1]}"/>`;
  pts.forEach(({id,i,c})=>{const cl=['pin'];if(stopDone(id))cl.push('done');else if(id===nx)cl.push('next');
    h+=`<g class="${cl.join(' ')}" data-stop="${id}"><circle cx="${c[0]}" cy="${c[1]-26}" r="14"/><text x="${c[0]}" y="${c[1]-26}">${i+1}</text></g>`});
  svg.innerHTML=h;
  const focus=(pts.find(p=>p.id===nx)||pts[0]);
  if(focus){const sc=$('#mapscroll'),k=960/vw;requestAnimationFrame(()=>{sc.scrollLeft=Math.max(0,(focus.c[0]-vx)*k-sc.clientWidth/2)})}
}

''' + s[b:]

# ---- list / sheet floor labels
rep("if(s.floor!==lastFloor){h+=`<div class=\"secttl\">${s.floor?'קומה עליונה (Level 3)':'קומת קרקע'}</div>`;lastFloor=s.floor}",
    "if(s.floor!==lastFloor){h+=`<div class=\"secttl\">${LEVEL_NAME[s.floor]} · ${esc(s.wing)}</div>`;lastFloor=s.floor}")
rep("(s.limit?`<span class=\"chip info\"><span class=\"ltr\">11:00–15:00</span></span>`:'')", "''")
rep("<span>· ${s.floor?'קומה עליונה':'קומת קרקע'}</span>", "<span>· ${esc(s.wing)}, ${LEVEL_NAME[s.floor]}</span>")

# ---- tier chip
rep("${it.star?`<span class=\"chip star\">Don't miss · ${it.star}</span>`:''}", "${it.star?'<span class=\"chip star\">★ חובה לראות</span>':''}")

# ---- floor / mode controls
rep("function setMode(m){mapMode=m;LS.set('bm-mapmode',m);$('#mm-real').setAttribute('aria-pressed',m==='real');$('#mm-plan').setAttribute('aria-pressed',m==='plan');$('#mapCredit').hidden=m!=='real';renderMap()}\n", '')
rep("function setFloor(f){floor=f;$('#fl-0').setAttribute('aria-pressed',f===0);$('#fl-1').setAttribute('aria-pressed',f===1);renderMap()}",
    "function setFloor(f){floor=f;document.querySelectorAll('#floors button').forEach(b=>b.setAttribute('aria-pressed',+b.dataset.floor===f));renderMap()}")
rep("$('#mm-real').onclick=()=>setMode('real'); $('#mm-plan').onclick=()=>setMode('plan'); setMode(mapMode);\n", '')
rep("$('#fl-0').onclick=()=>setFloor(0); $('#fl-1').onclick=()=>setFloor(1);",
    "$('#floors').innerHTML=[2,1,0,-1].map(f=>`<button data-floor=\"${f}\" aria-pressed=\"false\">${LEVEL_NAME[f]}</button>`).join('');\ndocument.querySelectorAll('#floors button').forEach(b=>b.onclick=()=>setFloor(+b.dataset.floor));")

# ---- info sheet title
rep("$('#shMeta').innerHTML='<span>לונדון, 14–22 בנובמבר 2026</span>';", "$('#shMeta').innerHTML='<span>מידע מעשי, נכון ל-21.11.2026</span>';")

# ---- info content -> generated
a = s.index('const INFO_HTML=`')
b = s.index('/* ---------- boot ---------- */')
s = s[:a] + s[b:]

open(f, 'w', encoding='utf-8').write(s)
print('ok')
