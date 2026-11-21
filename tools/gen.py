# Builds the data block of louvre.html from data/*.json (objects, media) and the route below.
# Run: python3 tools/gen.py && ./build.sh
import json, os, re, sys
from urllib.parse import unquote
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda f: os.path.join(ROOT, 'data', f)
load = lambda f: json.load(open(D(f), encoding='utf-8')) if os.path.exists(D(f)) else None

objs = {o['key']: o for o in load('antiquities.json')['objects'] + load('paintings.json')['works']}

# ---------- items ----------
def item(o):
    sub = [o['name_orig']]
    sub.append(', '.join(x for x in [o.get('artist'), o.get('date')] if x))
    if o.get('room'): sub.append(f"חדר {o['room']}")
    if o.get('inv'): sub.append(o['inv'])
    w = o.get('wikipedia_url') or {}
    if isinstance(w, str): w = {'en': w}
    l = [['Louvre', o['collection_url']]] if o.get('collection_url') else []
    if w.get('he'): l.append(['ויקיפדיה', w['he']])
    if w.get('en'): l.append(['Wikipedia', w['en']])
    srcs = []
    for u in o.get('sources') or []:
        h = re.sub(r'^https?://(www\.)?', '', u).split('/')[0]
        h = {'collections.louvre.fr': 'אתר הלובר', 'collection.louvre.fr': 'אתר הלובר', 'en.wikipedia.org': 'Wikipedia', 'he.wikipedia.org': 'ויקיפדיה'}.get(h, h)
        if h not in srcs: srcs.append(h)
    it = {'t': o['name_he'], 'sub': [x for x in sub if x], 'p': o['desc_he'], 'l': l}
    if o.get('tier') == 1: it['star'] = 1
    if o.get('on_display') is False: it['off'] = 1
    note = o.get('status_note_he') or o.get('note')
    if note: it['note'] = note
    if o.get('bible'): it['b'] = o['bible']
    if o.get('more_he'): it['more'] = o['more_he']; it['msrc'] = ', '.join(srcs) or 'אתר הלובר'
    return it

# ---------- route ----------
# stop id: (level, wing, title, name, [items], (x,y) on maps/level{L}.png, walking directions, closed ranges)
S = {
 'd703': (1, 'Denon', 'חדר 703', 'ניקה מסמותרקה', ['winged_victory'], (950, 398),
          'נכנסים בפירמידה, יורדים לאולם נפוליאון ועולים לאגף דנון. מטפסים במדרגות דארו: הניקה עומדת בראשן.'),
 'd708': (1, 'Denon', 'חדר 708', 'ציור איטלקי מוקדם', ['cimabue_maesta', 'giotto_francis', 'fra_angelico_coronation'], (975, 462),
          'מראש מדרגות דארו פונים ימינה לגלריה האיטלקית. צ\'ימבואה וג\'וטו בתחילתה.'),
 'd711': (1, 'Denon', 'חדר 711', 'אולם המדינות: המונה ליזה', ['mona_lisa', 'wedding_cana', 'titian_entombment'], (815, 442),
          'ממשיכים בגלריה הגדולה ופונים ימינה לאולם המדינות. מוקדם בבוקר התור למונה ליזה הכי קצר. החתונה בקנה על הקיר שמולה.'),
 'd710': (1, 'Denon', 'חדר 710', 'הגלריה הגדולה: לאונרדו ורפאל', ['virgin_of_the_rocks', 'st_anne', 'st_john_baptist', 'belle_jardiniere', 'raphael_st_michael', 'mantegna_crucifixion', 'mantegna_sebastian'], (898, 470),
          'חוזרים לגלריה הגדולה. ציורי לאונרדו ורפאל תלויים לאורך הקירות בקטע הזה.'),
 'd712': (1, 'Denon', 'חדר 712', 'קאראווג\'ו', ['caravaggio_death_virgin', 'caravaggio_fortune_teller', 'castiglione'], (725, 483),
          'ממשיכים מערבה לאורך הגלריה הגדולה.'),
 'd700': (1, 'Denon', 'חדר 700', 'ציור צרפתי רומנטי', ['raft_medusa', 'liberty', 'sardanapalus', 'gros_jaffa'], (730, 415),
          'מהגלריה הגדולה פונים צפונה לאולם מוליאן (700). רפסודת המדוזה והחירות מובילה את העם זו מול זו.',
          [['2026-12-01', '2026-12-15', 'חדר 700 סגור']]),
 'd702': (1, 'Denon', 'חדר 702', 'אולם דארו: דויד ואנגר', ['coronation_napoleon', 'oath_horatii', 'grande_odalisque'], (865, 408),
          'ממשיכים מזרחה דרך 701 לאולם דארו (702).'),
 'd403': (0, 'Denon', 'חדר 403', 'מיכלאנג\'לו וקנובה', ['michelangelo_slaves', 'canova_psyche'], (742, 410),
          'יורדים במדרגות מוליאן לקומה 0, לגלריית הפיסול האיטלקי (403).'),
 's345': (0, 'Sully', 'חדרים 345–348', 'ונוס ממילו', ['venus_de_milo', 'borghese_gladiator', 'sleeping_hermaphroditus'], (1040, 385),
          'ממשיכים מזרחה לאגף סולי. ונוס ממילו בסוף האולם, בחדר 345.'),
 's_moat': (-1, 'Sully', 'חדרים 133–137', 'הלובר של ימי הביניים', ['charles6_helmet'], (1100, 328),
          'יורדים למפלס ‎-1 ‏(שלטים: Louvre médiéval). הולכים לאורך החפיר ויסודות המבצר.'),
 's_sphinx': (-1, 'Sully', 'חדר 338', 'הספינקס של טניס', ['sphinx_tanis', 'ramses3_sarcophagus'], (1150, 385),
          'בהמשך המסלול במפלס ‎-1, בקריפטה של הספינקס. ארון רעמסס השלישי סמוך.'),
 's_eg0': (0, 'Sully', 'חדרים 324–333', 'מצרים: מקדשים וקברים', ['ramses2_abydos', 'dendera_zodiac', 'akhethetep_mastaba'], (1218, 330),
          'עולים מהספינקס לקומה 0, לחדרי מצרים באגף המזרחי של סולי.'),
 's_lev': (0, 'Sully', 'חדרים 301–303', 'הלבנט: אוגרית ומואב', ['baal_stele', 'ugarit_abecedary', 'mesha_stele', 'shihan_stele', 'amarna_megiddo'], (1000, 262),
          'אחרי ההפסקה הולכים לאגף הצפוני של סולי, לחדרי המזרח הקדום. מצבת מישע בחדר 303.'),
 's_per': (0, 'Sully', 'חדרים 307–309', 'פרס: ארמון דריווש בשושן', ['apadana_capital', 'archers_frieze', 'lions_frieze', 'darius_charter'], (1038, 252),
          'ממשיכים מזרחה. הכותרת הענקית ופריז הקשתים מחכים בחדר 307.'),
 's_phoen': (0, 'Sully', 'חדרים 311–315', 'פיניקיה ותדמור', ['eshmunazar_sarcophagus', 'palmyra_triad'], (1098, 250),
          'ממשיכים מזרחה לחדרים 311 ו-315.'),
 'r_meso': (0, 'Richelieu', 'חדרים 227–228', 'חמורבי ונרם-סין', ['hammurabi_code', 'naram_sin_stele', 'gudea_architect'], (815, 222),
          'חוזרים מערבה לאגף ריבלייה, לחדרי מסופוטמיה. חוקי חמורבי בחדר 227.'),
 'r_khors': (0, 'Richelieu', 'חדר 229', 'חצר חורסבאד: סרגון השני', ['lamassu_khorsabad', 'sargon_dignitary', 'cedar_transport'], (868, 240),
          'ממשיכים לחצר חורסבאד: השוורים המכונפים בשערים.'),
 'r_assy': (0, 'Richelieu', 'חדר 230', 'אשור ובבל', ['tiglath_pileser3', 'hazael_ivory', 'babylon_lion'], (906, 212),
          'מחורסבאד לחדר 230 הסמוך.'),
 'r_mari': (0, 'Richelieu', 'חדרים 234–236', 'מארי ושומר', ['ebih_il', 'stele_vultures'], (848, 262),
          'חוזרים דרומה לחדרים 234 ו-236.'),
 'r_marly': (-1, 'Richelieu', 'חדר 102', 'חצר מארלי', ['marly_horses'], (702, 247),
          'יורדים לחצרות הפיסול המקורות של ריבלייה (חצר מארלי).'),
 'r544': (1, 'Richelieu', 'חדר 544', 'דירות נפוליאון השלישי', ['napoleon3_apartments'], (650, 272),
          'עולים לקומה 1 לדירות נפוליאון השלישי. בקומה הזו גם קפה ריבלייה-אנג\'לינה.'),
 'r_dutch': (2, 'Richelieu', 'חדרים 837–844', 'ורמיר ורמברנדט', ['vermeer_lacemaker', 'vermeer_astronomer', 'rembrandt_bathsheba', 'rembrandt_emmaus', 'rembrandt_self_easel'], (690, 240),
          'עולים לקומה 2. הציור ההולנדי באגף המערבי: ורמיר ב-837, רמברנדט ב-844.'),
 'r_flem': (2, 'Richelieu', 'חדרים 809–818', 'הולבין, בוש, ואן אייק', ['holbein_erasmus', 'bosch_ship_of_fools', 'van_eyck_rolin'], (815, 212),
          'ממשיכים מזרחה דרך חדרי הציור הצפוני.'),
 'r_poussin': (2, 'Richelieu', 'חדרים 825–833', 'פוסן והציור הצרפתי המוקדם', ['poussin_four_seasons', 'poussin_manna', 'poussin_solomon', 'poussin_eliezer', 'pieta_villeneuve'], (872, 230),
          'בפינה המזרחית של ריבלייה מתחיל הציור הצרפתי. ארבע העונות של פוסן בחדר 825.'),
 's912': (2, 'Sully', 'חדר 912', 'ז\'ורז\' דה לה טור', ['la_tour_cheat', 'la_tour_magdalen'], (1018, 247),
          'ממשיכים מזרחה לאגף סולי, קומה 2.'),
 's917': (2, 'Sully', 'חדרים 917–919', 'ואטו ושרדן', ['watteau_cythera', 'chardin_ray'], (1180, 255),
          'ממשיכים לאורך האגף הצפוני של סולי עד הפינה.'),
 's_eg1': (1, 'Sully', 'חדרים 635–643', 'מצרים: הסופר היושב ואחנתון', ['seated_scribe', 'akhenaten_colossus', 'nefertiti_torso', 'merneptah_statuette', 'taharqa_hemen'], (1205, 305),
          'יורדים לקומה 1 באגף המזרחי של סולי. הסופר היושב בחדר 635.'),
 's663': (1, 'Sully', 'חדר 663', 'ארון הקבורה של בני הזוג', ['sarcophagus_spouses'], (1032, 357),
          'ממשיכים דרומה ומערבה לחדר 663 (האטרוסקים). גלריית קמפאנה הסמוכה סגורה. משם יוצאים דרך מדרגות דארו לפירמידה.'),
}
FULL = [('d703', 10), ('d708', 10), ('d711', 25), ('d710', 30), ('d712', 15), ('d700', 25), ('d702', 20), ('d403', 15), ('s345', 15),
        ('s_moat', 15), ('s_sphinx', 10), ('s_eg0', 20),
        ('LUNCH', 45, 'ארוחת צהריים. הכי קרוב: בתי הקפה באולם נפוליאון מתחת לפירמידה (Café Pyramide, Les Comptoirs du Louvre). אחר כך חוזרים לאגף סולי, קומה 0.'),
        ('s_lev', 25), ('s_per', 20), ('s_phoen', 10), ('r_meso', 20), ('r_khors', 15), ('r_assy', 15), ('r_mari', 10), ('r_marly', 10),
        ('r544', 15), ('r_dutch', 20), ('r_flem', 15), ('r_poussin', 20), ('s912', 15), ('s917', 10), ('s_eg1', 20), ('s663', 10)]
SHORT = [('d703', 10), ('d711', 25), ('d710', 20), ('d712', 10), ('d700', 20), ('d702', 15), ('d403', 10), ('s345', 10),
         ('s_lev', 15), ('s_per', 15), ('r_meso', 15), ('r_khors', 10), ('r_assy', 10)]

def timed(rt, start=9 * 60):
    out, t = [], start
    for e in rt:
        hm = f'{t // 60}:{t % 60:02d}'
        out.append({'lunch': hm, 'txt': e[2]} if e[0] == 'LUNCH' else [e[0], hm, e[1]])
        t += e[1]
    return out

used = set()
STOPS = {}
for sid, v in S.items():
    lv, wing, title, name, items, pos, way = v[:7]
    for i in items:
        assert i in objs, ('missing object', i)
        assert objs[i].get('on_display') is not False, ('not on display', i)
        used.add(i)
    st = {'floor': lv, 'wing': wing, 'title': title, 'name': name, 'items': items, 'pos': list(pos), 'way': way}
    if len(v) > 7: st['closed'] = v[7]
    STOPS[sid] = st
unused = [k for k, o in objs.items() if k not in used and o.get('on_display') is True]
if unused: print('WARNING on-display objects not in any stop:', unused, file=sys.stderr)

PLAN = {lv: {'img': f'maps/level{lv}.png', 'w': 1500, 'h': h, 'vb': vb} for lv, h, vb in
        [(-1, 740, [170, 170, 1130, 340]), (0, 726, [170, 180, 1130, 330]), (1, 735, [170, 180, 1130, 360]), (2, 726, [170, 160, 1130, 270])]}

# ---------- media (videos / podcasts with timestamps) ----------
def fmt(t): return f'{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}' if t >= 3600 else f'{t // 60}:{t % 60:02d}'
def tosec(tm):
    if not tm: return None
    n = 0
    for x in str(tm).split(':'): n = n * 60 + int(float(x))
    return n
PODS = {}
for f in ['media_antiquities.json', 'media_paintings.json']:
    m = load(f)
    if not m: continue
    rows = m if isinstance(m, list) else next(v for v in m.values() if isinstance(v, list)) if any(isinstance(v, list) for v in m.values()) else [e for v in m.values() for e in (v if isinstance(v, list) else [v])]
    for e in rows:
        k = e['key']
        if k not in objs or k not in used: continue
        if e.get('verified') is False and not e.get('keep'): continue
        st = int(e.get('start_sec') or 0)
        if e.get('length_sec') and st >= int(e['length_sec']): print('BAD start beyond length', k, e['url'], file=sys.stderr); continue
        listen = []
        if e.get('vid'): listen.append(['YouTube', f"https://www.youtube.com/watch?v={e['vid']}", st])
        elif e.get('url'): listen.append([e.get('show') or 'האזנה', e['url']])
        if e.get('spotify_url'): listen.append(['Spotify', e['spotify_url']])
        if e.get('apple_url'): listen.append(['Apple Podcasts', e['apple_url']])
        p = {'l': e.get('lang', 'EN'), 'show': e.get('show', ''), 'ep': e.get('ep', ''), 'len': e.get('len', ''), 'listen': listen,
             'tr': [e.get('transcript_label') or 'Transcript', e['transcript_url']] if e.get('transcript_url') else None,
             'at': e.get('at_he', ''), 'sum': e.get('sum_he', '')}
        pts = []
        for x in e.get('points') or []:
            sec = tosec(x.get('tm'))
            pts.append({'tm': x.get('tm') or '', 'txt': x.get('txt_he') or x.get('txt', ''), 'vid': e.get('vid'), 'sec': sec} if e.get('vid') and sec is not None else {'tm': x.get('tm') or '', 'txt': x.get('txt_he') or x.get('txt', '')})
        if pts: p['elab'] = pts; p['esrc'] = (e.get('show') or '') + (' · כתוביות הסרטון' if e.get('vid') else '')
        PODS.setdefault(k, []).append(p)

# ---------- info ----------
off = [o for o in objs.values() if o.get('on_display') is not True]
def a(u, t): return f'<a href="{u}" target="_blank" rel="noopener">{t}</a>'
INFO = f'''<div class="info" style="display:flex;flex-direction:column;gap:12px">
<h3>שעות וכניסה</h3>
<dl class="kv">
<dt>שעות</dt><dd>9:00–18:00. ברביעי ובשישי עד 21:00. כניסה אחרונה שעה לפני הסגירה; פינוי האולמות מתחיל חצי שעה לפני.</dd>
<dt>סגור</dt><dd>כל יום שלישי, וב-1.1, 1.5 ו-25.12.</dd>
<dt>קומה 2</dt><dd>ברביעי ובשישי חדרי קומה 2 (ריבלייה 800, סולי 900) נפתחים רק ב-10:30.</dd>
<dt>כרטיס</dt><dd>‏32 € למי שאינו אזרח האיחוד (כולל ישראלים). מומלץ להזמין שעת כניסה ב-{a('https://ticket.louvre.fr/en','ticket.louvre.fr')}; בין 19.12 ל-4.1 זו חובה. להיזהר מאתרי מכירה חוזרת.</dd>
<dt>חינם</dt><dd>מתחת לגיל 18. ביום שישי הראשון בחודש אחרי 18:00 (למשל 4.12) הכניסה חינם לכולם.</dd>
<dt>כניסות</dt><dd>הפירמידה (הראשית). <span class="ltr">Porte des Lions</span>: לבעלי כרטיס בלבד, בדרך כלל התור הקצר ביותר, נסגרת ב-18:00. מעבר ריבלייה: לקבוצות בלבד.</dd>
<dt>תחבורה</dt><dd>מטרו <span class="ltr">Palais-Royal / Musée du Louvre</span> (קווים 1, 7), עם גישה תת-קרקעית דרך הקרוסל.</dd>
<dt>תיקים</dt><dd>לוקרים חינם מתחת לפירמידה (עד ‎55×35×20 ס"מ). מזוודות אסורות.</dd>
<dt>צילום</dt><dd>מותר לשימוש אישי, בלי פלאש ובלי מקל סלפי.</dd>
<dt>אוכל</dt><dd>Café Mollien (דנון 1, ליד חדר 700), Café Richelieu-Angelina (ריבלייה 1), בתי הקפה באולם נפוליאון.</dd>
<dt>אודיוגייד</dt><dd>‏6 € ובלי עברית. אין אפליקציית ביקור רשמית; יש {a('https://collections.louvre.fr/plan','מפה אינטראקטיבית')}.</dd>
</dl>
<h3>סגור עכשיו (לפי אתר הלובר, 21.11.2026)</h3>
<ul>
<li>אמנות האסלאם (דנון ‎-1/‎-2), עתיקות רומיות (דנון 0), גלריית קמפאנה (סולי 1), גלריית מדיצ'י של רובנס (ריבלייה 2), הציור הספרדי 720–734, חדרים 400–402.</li>
<li>חדר 709 סגור עד סוף נובמבר. <b>חדר 700</b> (רפסודת המדוזה, החירות) סגור 1–15 בדצמבר.</li>
<li>גלריית אפולו (705) נפתחה מחדש ביולי 2026, אבל תכשיטי הכתר לא מוצגים מאז השוד באוקטובר 2025. אפשר להציץ בה בדרך מהניקה (703).</li>
<li>המונה ליזה עדיין בחדר 711. ההעברה לאולם חדש מתוכננת רק לסביבות 2031.</li>
<li>אין עדיין לוח סגירות לדצמבר. לבדוק שבוע לפני ב{a('https://www.louvre.fr/en/visit/list-of-available-galleries','רשימת האולמות הפתוחים')}.</li>
</ul>
<h3>לא מוצגים כרגע</h3>
<ul>{''.join(f"<li>{o['name_he']} – {a(o['collection_url'],'Louvre') if o.get('collection_url') else ''}{(': ' + (o.get('status_note_he') or o.get('note') or '')) if (o.get('status_note_he') or o.get('note')) else ''}</li>" for o in off)}</ul>
<h3>רקע: המקרא בלובר</h3>
<p><b>המזרח הקדום (ריבלייה וסולי 0):</b> חמורבי (המאה ה-18 לפנה"ס) ומשפט "עין תחת עין"; סרגון השני, שכבש את שומרון (ישעיהו כ); תגלת-פלאסר השלישי, שהגלה את צפון ישראל (מלכים ב טו); מישע מלך מואב (מלכים ב ג) – המצבה עם השם יהוה ואולי "בית דוד".</p>
<p><b>פרס:</b> ארמון דריווש בשושן – הרקע לסיפורי אסתר, נחמיה ("ואני הייתי בשושן הבירה") ודניאל.</p>
<p><b>מצרים:</b> שישק (הספינקס של טניס), רעמסס השני ופיתום ורעמסס, תהרקה מלך כוש שיצא נגד סנחריב (מלכים ב יט:9).</p>
<p><b>הברית החדשה בציור:</b> החתונה בקנה (יוחנן ב), יוחנן המטביל, הצליבה וההובלה לקבר, הסעודה באמאוס (לוקס כד), מות הבתולה.</p>
<p><b>התנ"ך בציור:</b> בת שבע של רמברנדט (שמואל ב יא), ארבע העונות של פוסן (גן עדן, רות ובועז, אשכול המרגלים, המבול), משפט שלמה, המן במדבר, אליעזר ורבקה.</p>
<p><b>נפוליאון וארץ ישראל:</b> "בונפרטה מבקר את חולי המגפה ביפו" (חדר 700) – תעמולה על המצור על יפו ב-1799.</p>
<h3>הסתייגויות</h3>
<ul><li>מספרי החדרים והסטטוס לקוחים מרשומת כל פריט באתר האוסף של הלובר. הסיכות על המפה מסמנות את אזור החדר בקירוב.</li><li>המפה: תוכנית המוזיאון הרשמית, מאי 2026 (Dream On / Service de la médiation graphique et numérique, musée du Louvre), לשימוש אישי.</li><li>הקשרים המקראיים לפי הדעה המחקרית המקובלת. הקריאה "בית דוד" במצבת מישע שנויה במחלוקת.</li></ul>
</div>'''

def js(x): return json.dumps(x, ensure_ascii=False, separators=(',', ':'))
block = '\n'.join([
    '/* DATA-BEGIN */',
    '/* generated by tools/gen.py from data/*.json — edit there */',
    f'const ITEMS={js({k: item(objs[k]) for k in objs if k in used})};',
    f'const PODS={js(PODS)};',
    f'const STOPS={js(STOPS)};',
    f'const ROUTES={js({"full": timed(FULL), "short": timed(SHORT)})};',
    f'const PLAN={js({str(k): v for k, v in PLAN.items()})};',
    f'const INFO_HTML={js(INFO)};',
    '/* DATA-END */'])
f = os.path.join(ROOT, 'louvre.html')
s = open(f, encoding='utf-8').read()
s = re.sub(r'/\* DATA-BEGIN \*/.*?/\* DATA-END \*/', lambda _: block, s, flags=re.S)
open(f, 'w', encoding='utf-8').write(s)
print(f'items {len(used)}, stops {len(STOPS)}, episodes {sum(len(v) for v in PODS.values())} on {len(PODS)} items, not on display {len(off)}')
