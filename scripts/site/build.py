"""The reccos landing page, generated from live data.

    python3 scripts/site/build.py            writes site/index.html and site/data.json

Templates, styles and behaviour live next to this file; the live numbers come from data.py; who and what is featured
is in content.json. The GitHub Action in .github/workflows/landing-data.yml runs this every hour and commits only when
the page changed. Standard library only.
"""
import html, json, os, re, sys
from datetime import datetime
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data as live  # noqa: E402

def rd(name): return open(os.path.join(HERE, name), encoding='utf-8').read()

LET = json.loads(rd('wm.json'))['letters']
DEFS = rd('defs.svgfrag')
CSS = rd('site.css')
JS = rd('site.js')
QR = rd('qr.svg')
CONTENT = json.loads(rd('content.json'))
SUB = [p + 'Z' for p in LET.split('Z') if p.strip()]
RE, OS = ''.join(SUB[:3]), ''.join(SUB[3:])

# Where an image is served from. The site uses its own img/ folder; a design-canvas build swaps these.
OUT = {'asset': None, 'avatar': None}
def blob(k): return OUT['asset'](k)
def avatar(h):
    if OUT['avatar']:
        a = OUT['avatar'](h)
        if a: return a
    c = D['creators'].get(h) if D else None
    return (c and c['avatar']) or ''
def e(s): return html.escape(s, quote=True)

ACC = ['#FF8BA7', '#7DA2FF', '#74D394', '#F2BE6B', '#B39BFF', '#5FD0DC']
TINT = ['#4A2232', '#22305A', '#24402F', '#4A3A1F', '#352C5C', '#1F4048']
CAT = {'restaurants': ('#9CCE62', '#242C34'), 'cafes': ('#DEA678', '#2C2737'), 'bars': ('#AA8CFF', '#262447'), 'pubs': ('#54C4D6', '#1C2B42')}

# ---------- small parts ----------
_wm = [0]
def wm(cls='', label='reccos', live=True, color='currentColor'):
    _wm[0] += 1
    i = 'w%d' % _wm[0]
    eyes = ''
    masks = ''
    for k, cx in enumerate((428.6, 653.6)):
        masks += ('<mask id="%s%d" maskUnits="userSpaceOnUse" x="%.1f" y="-6" width="236" height="312">'
                  '<rect x="%.1f" y="-6" width="236" height="312" fill="#fff"/>'
                  '<rect class="open" x="%.1f" y="70" width="344" height="160" rx="60" fill="#000" transform="translate(%.1f 150) skewX(-10) translate(%.1f -150)"/>'
                  '<rect class="shut" x="%.1f" y="143" width="344" height="22" rx="11" fill="#000" transform="translate(%.1f 154) skewX(-10) translate(%.1f -154)"/>'
                  '</mask>') % (i, k, cx - 118, cx - 118, cx - 44, cx, -cx, cx - 34, cx, -cx)
        eyes += '<ellipse cx="%.1f" cy="150" rx="108" ry="150" mask="url(#%s%d)"/>' % (cx, i, k)
    a11y = ('role="img" aria-label="%s"' % e(label)) if label else 'aria-hidden="true" focusable="false"'
    return ('<svg class="wm%s%s" viewBox="0 -2 1116.65 304" %s><defs>%s</defs>'
            '<g fill="%s"><path d="%s" fill-rule="evenodd"/>%s</g></svg>') % (' live' if live else '', (' ' + cls) if cls else '', a11y, masks, color, LET, eyes)

def mk(sym, cls='', style=''):
    st = (' style="%s"' % style) if style else ''
    return '<svg class="mk %s"%s aria-hidden="true" focusable="false"><use href="#%s" width="100%%" height="100%%"/></svg>' % (cls, st, sym)

def price(t):
    out = '$' * t
    if t < 3: out += '<span class="g4">$</span>'
    if t < 2: out += '<span class="g2">$</span>'
    return out

def band(s):
    return 'lov' if s >= 8 else 'fin' if s >= 5 else 'dis'

def f1(s): return live.fixed1(s)

PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5v15a1 1 0 0 0 1.5.86l12.5-7.5a1 1 0 0 0 0-1.72L8.5 3.64A1 1 0 0 0 7 4.5Z" fill="#ECEBFF"/></svg>'
PLAYN = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 3l16 9-16 9z" fill="#0B0C1E"/></svg>'
CHEV = '<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6l6 6-6 6" fill="none" stroke="#7C7FA6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
BACK = '<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7" fill="none" stroke="#ECEBFF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
SHARE = '<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" fill="none"><path d="M12 15V4M8 8l4-4 4 4M5 13v5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-5" stroke="#ECEBFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
BOOK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3.5h10a1 1 0 0 1 1 1V21l-6-4-6 4V4.5a1 1 0 0 1 1-1z" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
SPARK = '<svg class="sp" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 0C12.9 7.4 16.6 11.1 24 12C16.6 12.9 12.9 16.6 12 24C11.1 16.6 7.4 12.9 0 12C7.4 11.1 11.1 7.4 12 0Z" fill="currentColor"/></svg>'
ASKI = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14.2 4.6A7 7 0 1 0 17.4 11.2" stroke="%s" stroke-width="2.1" stroke-linecap="round" fill="none"/>'
        '<path d="M15.4 15.9L20 20.5" stroke="%s" stroke-width="2.1" stroke-linecap="round"/><path d="M18.6 1.6c.38 2.08.92 2.62 3 3-2.08.38-2.62.92-3 3-.38-2.08-.92-2.62-3-3 2.08-.38 2.62-.92 3-3z" fill="%s"/></svg>')
CHL = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14.5 6l-6 6 6 6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CHR = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9.5 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ARROW = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="#ECEBFF" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CLOSE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="#ECEBFF" stroke-width="2.2" stroke-linecap="round"/></svg>'
SBAR = ('<div class="sbar"><span>9:41</span><span class="ic">'
        '<svg width="18" height="12" viewBox="0 0 18 12" fill="#ECEBFF"><rect x="0" y="7.5" width="3" height="4.5" rx="1"/><rect x="5" y="5" width="3" height="7" rx="1"/><rect x="10" y="2.5" width="3" height="9.5" rx="1"/><rect x="15" y="0" width="3" height="12" rx="1"/></svg>'
        '<svg width="16" height="12" viewBox="0 0 16 12" fill="#ECEBFF"><path d="M8 11.6l2.4-2.5a3.4 3.4 0 0 0-4.8 0z"/><path d="M8 5.3c1.8 0 3.4.7 4.6 1.9l1.2-1.2A8.1 8.1 0 0 0 8 3.6 8.1 8.1 0 0 0 2.2 6l1.2 1.2A6.4 6.4 0 0 1 8 5.3z"/><path d="M8 1.7c2.8 0 5.3 1.1 7.2 2.9L16.4 3.4A11.8 11.8 0 0 0 8 0 11.8 11.8 0 0 0-.4 3.4l1.2 1.2A10.1 10.1 0 0 1 8 1.7z"/></svg>'
        '<svg width="27" height="13" viewBox="0 0 27 13" fill="#ECEBFF"><rect x=".5" y=".5" width="23" height="12" rx="3.8" fill="none" stroke="#ECEBFF" stroke-opacity=".35"/><rect x="2" y="2" width="20" height="9" rx="2.4"/><path d="M25 4.4v4.2c.8-.3 1.4-1.1 1.4-2.1s-.6-1.8-1.4-2.1z" fill-opacity=".4"/></svg>'
        '</span></div>')
VER = lambda: mk('lm-verified', 'vt', 'color:#5B8CFF')
CLOCK = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5" fill="none" stroke="#C4C6E3" stroke-width="2"/><path d="M12 7.5V12l3 2" fill="none" stroke="#C4C6E3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
PLAYC = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="#C4C6E3" stroke-width="2"/><path d="M10.2 8.4v7.2l5.6-3.6z" fill="#C4C6E3"/></svg>'
NB = '\u2011'
MUTE = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="#ECEBFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5L6 9H3v6h3l5 4z" fill="#ECEBFF"/><path d="M16 9.5l5 5M21 9.5l-5 5"/></svg>'
OUT_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="#ECEBFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/></svg>'

def phone(inner, cls=''):
    return '<div class="phone %s"><div class="clip">%s</div></div>' % (cls, inner)

def qr_svg(): return QR

# ---------- data: live from Supabase (see prepare) ----------
D = None
CREW, CREATORS, TICKETS, STRIP, FACTS, ASKD = [], [], [], [], {}, {}
TOTAL_OPEN = 0
NUM = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
MEL = ZoneInfo('Australia/Melbourne')

def fl_short(label):
    """'35.9k on TikTok' as the templates want it ('35.9k'); they add 'on TikTok' themselves."""
    return re.sub(r'\s*on TikTok\s*$', '', label or '')

def prepare(data):
    """Turn the live data into the shapes the templates use."""
    global D, CREW, CREATORS, TICKETS, STRIP, FACTS, ASKD, TOTAL_OPEN
    D = data
    V = D['venues']
    cr = D['creators']
    FACTS = D['facts']

    # The hero's sort: each featured creator's top 7 in one category, with the stills of the videos behind them.
    CREW = []
    for s in CONTENT['sort']:
        c = cr.get(s['handle'])
        if not c: continue
        top = [t for t in c['top'].get(s['category'], []) if t['venue'] in V][:7]
        if not top: continue
        rows = [(V[t['venue']]['name'], V[t['venue']]['suburb'] or '', V[t['venue']]['price_tier'] or 1, t['score']) for t in top]
        at = {t['venue']: i for i, t in enumerate(top)}
        tiles = []
        for still, ids in s['tiles']:
            rws = [at[i] for i in ids if i in at]
            if rws: tiles.append((still, rws))
        n = c['counts']
        tabs = (n.get('restaurants', 0), n.get('cafes', 0), n.get('bars', 0), n.get('pubs', 0), s['category'])
        CREW.append((c['handle'], e(c['name']), fl_short(c['followers']), e(c['focus']), tabs, rows, tiles))

    # Find's cards: reviews, followers and top 3 (restaurants, or their biggest category).
    CREATORS = []
    for h in CONTENT['cards']:
        c = cr.get(h)
        if not c or not c['top']: continue
        cat = 'restaurants' if len(c['top'].get('restaurants', [])) >= 3 else max(c['counts'], key=c['counts'].get)
        top = [(V[t['venue']]['name'], t['score'], cat) for t in c['top'][cat][:3]]
        CREATORS.append((h, c['tint'] % 6, c['reviews'], fl_short(c['followers']), top))

    # Just opened: the rail Find shows today, by the app's rules.
    rail, TOTAL_OPEN = live.tickets(D)
    TICKETS = []
    for t in rail:
        v, o = t['v'], t['o']
        d, mo = t['dm'] if t['dm'] else ('', '')
        TICKETS.append((v['name'], v['category'], v['cuisine'] or '', v['suburb'] or '', v['price_tier'] or 1, d, mo, o['note'] or '', t['first'], t['soon']))

    # The creators strip: each still with that creator's own score for the place.
    STRIP = []
    for h, vid, still in CONTENT['strip']:
        c = cr.get(h)
        if not c: continue
        s = next((t['score'] for cat in c['top'].values() for t in cat if t['venue'] == vid), None)
        if s is not None: STRIP.append((h, still, s))

    # Or just ask: the pick's Locals score, the foodies who reviewed it (best first) and their videos.
    a = CONTENT['ask']
    pick = a['pick']['venue']
    revs = sorted(((t['score'], h) for h, c in cr.items() for cat in c['top'].values() for t in cat if t['venue'] == pick),
                  key=lambda x: (-x[0], x[1]))
    when = {}
    by_uid = {c['id']: h for h, c in cr.items()}
    for v in live.get('creator_videos?select=user_id,venue_id,posted_at,video_id&venue_id=eq.%d&order=posted_at.desc,video_id' % pick):
        h = by_uid.get(v['user_id'])
        if h and h not in when and v['posted_at']:
            d = datetime.fromisoformat(v['posted_at'].replace('Z', '+00:00')).astimezone(MEL)
            when[h] = '%d %s' % (d.day, live.MON[d.month - 1])
    loc = lambda vid: (D['locals'].get(vid) or {}).get('score')
    ASKD = {
        'pick': V.get(pick), 'pick_score': loc(pick), 'revs': revs,
        'player': [(h, a['videos'][h], fl_short(cr[h]['followers']), when.get(h, ''), s) for s, h in revs if h in a['videos']],
        'others': [(V[o['venue']], loc(o['venue']), o['drive']) for o in a['others'] if o['venue'] in V],
    }

TILES = [('0%', '5%', '-9deg', '1%', '3%'), ('21%', '0%', '6deg', '73%', '10%'), ('6%', '32%', '4deg', '6%', '27%'), ('27%', '27%', '-5deg', '71%', '37%'), ('1%', '61%', '-3deg', '0%', '51%'), ('22%', '64%', '8deg', '74%', '64%'), ('38%', '47%', '-6deg', '8%', '75%')]
SAM = [('Tori no Keiji', 'CBD', 1, 9.6, True), ('Ikkoryu Fukuoka Ramen', 'CBD', 1, 9.4, False), ('Sara Ramen & Yakitori', 'CBD', 2, 9.1, False),
       ('Ginza Kagari', 'CBD', 1, 8.8, False), ('Supernormal', 'CBD', 2, 8.4, False), ('Meetbowl Collins', 'CBD', 1, 7.6, False)]
FAQ = [
    ('Is reccos free?', 'Yes. reccos is free to download and free to use.'),
    ('Is it only Melbourne?', 'For now, yes. reccos is starting with Melbourne and the people who review its food.'),
    ('Is there an Android app?', 'Not yet. reccos is iPhone only for now.'),
    ('How do scores work?', 'Every recco starts as Loved it, It was fine or Didn’t like it, and a couple of quick head\u2011to\u2011heads place it among the others in your list. That gives it a score out of 10: 8 and up is loved, 5 to 7.9 is fine, and under 5 you didn’t like it. A place’s Locals score brings together everyone who’s recommended it.'),
    ('Who can see my reccos?', 'Your reccos sit on your profile, so anyone you send your link to can open your list, and people can follow you in the app. The <a href="/privacy">Privacy Policy</a> has the details.'),
    ('Where do the foodies’ reccos come from?', 'From their own TikTok reviews. reccos turns their reviews into a list, with their score, what to order and the video a tap away. New reviews land within a couple of days of posting.'),
    ('I make food videos. How do I claim my reccos?', 'Email us at [contact email]. If your list is ready, we’ll send you a link to check it in a few head\u2011to\u2011heads and get the tick.'),
    ('How do I get in touch?', 'Email [contact email]. We read everything.'),
]

def header():
    return ('<header class="hd"><div class="w">'
            '<a class="brand" href="#top" aria-label="reccos, back to the top">%s</a>'
            '<nav class="nav" aria-label="On this page"><a href="#find">Find reccos</a><a href="#mine">My reccos</a><span class="nav-sep" aria-hidden="true"></span><a href="#creators">For creators</a><a href="#faq">Q&amp;A</a></nav>'
            '<a class="gta" href="#get"><span class="chip" aria-hidden="true">%s%s</span>Get the app</a>'
            '</div></header>') % (wm(label='reccos'), mk('rx-fine-s', 'eo'), mk('rx-loved', 'eh'))

def crew_label():
    hs = ['@' + c[0] for c in CREW]
    return ', then '.join(hs)

def hero():
    groups, screens = '', ''
    pref = [0, 1, 2, 4, 5, 3, 6]  # where the first n tiles sit, so a short set still spreads out
    for g, (h, name, fl, focus, tabs, rows, tl) in enumerate(CREW):
        tiles = ''
        for k, (still, rws) in enumerate(tl):
            x, y, r, x2, y2 = TILES[sorted(pref[:len(tl)])[k]]
            tiles += ('<div class="tile%s" data-rows="%s" style="--x:%s;--y:%s;--x2:%s;--y2:%s;--r:%s;--dd:-%.1fs" aria-hidden="true"><div class="tile-in"><img src="%s" alt="" decoding="async">'
                      '<span class="tc"><img src="%s" alt="">%s</span></div></div>') % (' hid' if g else '', ','.join(map(str, rws)), x, y, x2, y2, r, k * 1.3, blob(still), avatar(h), PLAY)
        groups += '<div class="tg">%s</div>' % tiles
        rr = ''.join('<div class="prow krow"><span class="rk">%d</span><div class="tx"><div class="nm">%s</div><div class="cap">%s · %s</div></div><span class="sc %s">%s</span></div>'
                     % (i + 1, e(n), e(sub), price(t), band(s), f1(s)) for i, (n, sub, t, s) in enumerate(rows))
        on = tabs[4]
        ct = ctabs([('restaurants', 'Restaurants', tabs[0], on == 'restaurants'), ('cafes', 'Cafés', tabs[1], on == 'cafes'), ('bars', 'Bars', tabs[2], False), ('pubs', 'Pubs', tabs[3], False)])
        screens += ('<div class="scr ks%s">%s<div class="tbar">%s%s</div>'
                    '<div class="kp"><img src="%s" alt=""><div><div class="kn">%s %s</div><div class="kh">@%s · %s on TikTok</div></div></div>'
                    '<div class="kfoc">%s</div><div class="follow">Follow</div>%s'
                    '<div class="krows">%s</div><div class="home"></div></div>') % (' on' if not g else '', SBAR, BACK, SHARE, avatar(h), name, VER(), h, fl, focus, ct, rr)
    tiles, screen = groups, '<div class="kss">%s</div>' % screens
    av = '<span class="av" style="background:%s;color:%s">J</span>' % (TINT[0], ACC[0])
    return ('<section class="hero w" id="top">'
            '<div class="hcopy">'
            '<div class="chat" data-loop aria-label="A group chat: where should we eat tonight? Sixteen minutes later: anyone?">'
            '<div class="msg m0"><span class="av ghost"></span><div class="mcol"><span class="who"><b>Julie</b> · 6:42 pm</span><span class="bub t1">where should we eat tonight?</span></div></div>'
            '<div class="stamp st1">6:58 pm</div>'
            '<div class="msg m1">%s<span class="bub t2">anyone?</span></div>'
            '</div>'
            '<h1 class="h1">Stop scrolling for somewhere to eat.</h1>'
            '<p class="lede">Melbourne’s food creators have reviewed hundreds of places on TikTok. <span class="hl hl-s">reccos puts all their reviews in one place:</span> scored, on a map and searchable, with the video a tap away.</p>'
            '<div class="get" id="get">'
            '<div class="get-l"><a class="badge" href="#" aria-label="Download reccos on the App Store"><small>Download on the</small><span>App Store</span></a>'
            '<p class="ionly">reccos is iPhone only for now.</p>'
            '<button class="filmbtn" type="button" data-film><span class="pl">%s</span><b>See how it works</b><i>1 min</i></button></div>'
            '<div class="qr"><div class="qr-code">%s<span class="qr-mid">%s%s</span></div><div class="qr-t"><b>Scan to get reccos</b><span>Point your iPhone camera here.</span></div></div>'
            '</div>'
            '<ul class="facts"><li>Free on iPhone</li><li><span><b class="tab">%s</b> foodies</span></li><li><span><b class="tab">%s</b> reviews</span></li><li><span><b class="tab">%s</b> places</span></li></ul>'
            '</div>'
            '<div class="sort" data-loop role="img" aria-label="Food creators’ TikTok reviews landing in reccos as their scored lists: %s">%s%s</div>'
            '</section>') % (av, PLAY, qr_svg(), mk('rx-fine-s', 'eo'), mk('rx-loved', 'eh'), '{:,}'.format(FACTS['foodies']), '{:,}'.format(FACTS['reviews']), '{:,}'.format(FACTS['places']), crew_label(), tiles, phone(screen))

def ctabs(items):
    out = '<div class="ctabs" role="presentation">'
    for c, label, n, on in items:
        hue = CAT[c][0]
        col = hue if on else '#3B4070'
        badge = ''
        if n:
            badge = '<span class="bd" style="background:%s">%s</span>' % (hue, n if not isinstance(n, tuple) else '<span class="b0">%d</span><span class="b1">%d</span>' % n)
        out += ('<div class="ctab%s"><div class="mw">%s%s</div>%s%s</div>') % (
            ' on' if on else '', mk('lm-' + c, '', 'color:%s' % col), badge,
            ('<span class="lb" style="color:%s">%s</span>' % (hue, label)) if on else '',
            ('<span class="ul" style="background:%s"></span>' % hue) if on else '')
    return out + '</div>'

def find():
    cards = ''
    for i, (h, a, n, fl, top) in enumerate(CREATORS):
        tilt = ['-6deg', '4deg', '-3deg', '5deg', '-4deg', '3deg'][i % 6]
        rows = ''.join('<div class="cc-r">%s<span class="n">%s</span><span class="s %s">%s</span></div>' % (mk('lm-' + cat), e(p), band(s), f1(s)) for p, s, cat in top)
        cards += ('<a class="cc" href="#get" style="--ac:%s;--i:%d;--t:%s" aria-label="@%s, %d reviews, %s followers on TikTok. Open their reccos">'
                  '%s<div class="cc-in"><div class="cc-h"><img src="%s" alt=""><div class="t"><div class="hn">@%s %s</div><div class="fl">%d reviews · %s on TikTok</div></div>%s</div>'
                  '<div class="cc-l">%s</div></div></a>') % (ACC[a], i, tilt, h, n, fl, mk('lm-' + top[0][2], 'wmk'), avatar(h), h, VER(), n, fl, CHEV, rows)
    return ('<section class="act w" id="find">'
            '<div class="ahead rv"><div class="lock" role="img" aria-label="find reccos"><span class="lw" aria-hidden="true">find</span><wbr>%s</div>'
            '<h2 class="h2">Follow the foodies you trust.</h2>'
            '<p class="lede">Their reviews become one list you can filter and map, with Locals scores beside them and the video a tap away. New reviews land within a couple of days of posting.</p></div>'
            '<div class="cards" data-io>%s</div>'
            '%s%s</section>') % (wm(label=''), cards, ask(), just_opened())

def ask():
    a = CONTENT['ask']
    P = ASKD['pick']
    revs = ASKD['revs']
    if not P or not revs or not ASKD['player']:
        return ''
    lead = revs[0][1]
    player = ASKD['player']
    stack = ''.join('<img src="%s" alt="">' % avatar(h) for _, h in revs[:3])
    want = lambda col: mk('lm-want', '', 'color:%s' % col)
    cards = ''.join('<div class="vc%s"><img src="%s" alt=""><span class="pr"><i></i></span></div>' % (' live' if i == 0 else '', blob(st)) for i, (h, st, fl, d, s) in enumerate(player))
    metas = ''.join(('<div class="vm%s"><div class="r1"><img src="%s" alt=""><div class="t"><div class="hn">@%s %s</div><div class="cap">%s on TikTok%s</div></div>'
                     '<span class="gb">%s</span><span class="gb">%s</span></div>'
                     '<div class="r2">%s<span class="chipS">%s</span></div></div>') % (' on' if i == 0 else '', avatar(h), h, VER(), fl, (' · ' + d) if d else '', MUTE, OUT_ICON, mk('rx-loved'), f1(s)) for i, (h, st, fl, d, s) in enumerate(player))
    dots = ''.join('<i%s></i>' % (' class="on"' if i == 0 else '') for i in range(len(player)))
    nv = len(player)
    vp = ('<div class="vp" aria-hidden="true"><div class="vp-bg"></div>%s<div class="vp-top"><div class="t"><div class="l">%s</div><div class="cap">%d video%s on TikTok</div></div><span class="gb">%s</span></div>'
          '<div class="vr">%s</div><div class="vi"><div class="vd">%s</div><div class="vms">%s</div></div></div>') % (SBAR, e(P['name']), nv, '' if nv == 1 else 's', CLOSE, cards, dots, metas)
    n = len(revs)
    many = '%s %s' % (NUM[n] if n < len(NUM) else n, 'foodie has' if n == 1 else 'foodies have')
    ps = ASKD['pick_score'] if ASKD['pick_score'] is not None else revs[0][0]
    rows = ''
    for k, (v, s, drive) in enumerate(ASKD['others']):
        sc = ('<span class="sc %s">%s</span>' % (band(s), f1(s))) if s is not None else ''
        rows += ('<div class="arow"><div class="top"><span class="rk">%d</span><div class="tx"><div class="nm">%s</div><div class="cap">%s · %s · %s · %s</div></div>'
                 '<div class="rs">%s%s</div></div></div>') % (k + 2, e(v['name']), e(a['kind']), e(v['suburb'] or ''), price(v['price_tier'] or 1), e(drive), sc, want('#7C7FA6'))
    q = e(a['query'])
    screen = ('<div class="scr ascr">%s<div class="tbar">%s%s</div>'
              '<div class="abox">%s<span class="q" data-q="%s">%s</span></div>'
              '<p class="asum">%s <u>%s</u> %s, and %s reviewed it.</p>'
              '<div class="pick"><div class="pph"><img src="%s" alt="Photo of %s"><span class="credit">Photo: @%s</span><span class="gchip"><img src="%s" alt="">@%s%s</span></div>'
              '<div class="prow2"><span class="rk">1</span><div class="tx"><div class="pn">%s</div><div class="cap">%s · %s · %s · %s</div></div><span class="ps %s">%s</span></div>'
              '<div class="lby"><span class="stack">%s</span>Loved by @%s%s</div>'
              '<div class="save">%sWant to try</div></div>'
              '%s%s</div>') % (SBAR, BACK, SHARE, ASKI % ('#ECEBFF', '#ECEBFF', '#ECEBFF'), q, q,
                               e(a['intro']), e(P['name']), e(a['pick']['line']), many,
                               blob(a['pick']['photo']), e(P['name']), e(a['pick']['credit']), avatar(lead), lead, PLAY,
                               e(P['name']), e(a['kind']), e(P['suburb'] or ''), price(P['price_tier'] or 1), e(a['pick']['drive']), band(ps), f1(ps),
                               stack, lead, (' +%d' % (n - 1)) if n > 1 else '', want('#FF5A66'), rows, vp)
    return ('<div class="ask">'
            '<div class="ask-t rv"><h2 class="h2">Or just ask.</h2>'
            '<p class="lede">Type it the way you’d text a friend. reccos reads it, finds the places that fit, and shows you which foodies loved them.</p>'
            '<div class="prompt">%s<span>%s</span></div>'
            '<ul class="ask-n"><li>%s<span>Knows what’s open, how far it is and what it costs.</span></li><li>%s<span>Every foodie’s video of the place, a swipe apart.</span></li></ul></div>'
            '%s</div>') % (ASKI % ('#C4C6E3', '#C4C6E3', '#C4C6E3'), q, CLOCK, PLAYC, phone(screen))

def just_opened():
    tk = ''
    for (n, c, cu, sub, t, d, mo, note, first, soon) in TICKETS:
        hue, ground = CAT[c]
        if soon and d:
            stub = '<div class="tk-s" aria-label="Opens %s %s"><span class="k">Opens</span><span class="d">%s</span><span class="mo">%s</span></div>' % (d, mo, d, mo)
            act = '%sWant to try' % mk('lm-want', '', 'color:#ECEBFF')
        elif soon:
            stub = '<div class="tk-s" aria-label="Opens soon"><span class="k">Opens</span>%s<span class="mo">soon</span></div>' % mk('rx-fine', 'fine', 'color:#C4C6E3')
            act = '%sWant to try' % mk('lm-want', '', 'color:#ECEBFF')
        else:
            stub = '<div class="tk-s" aria-label="Opened %s %s"><span class="k">Opened</span><span class="d">%s</span><span class="mo">%s</span>%s</div>' % (d, mo, d, mo, SPARK)
            act = ('Give it the first recco' if first else 'Recommend it') + ' <span class="ar">→</span>'
        tk += ('<a class="tk%s" href="#get"><div class="tk-b" style="background:%s"><div class="tk-m"><div class="tk-h"><span class="mw">%s</span><div class="t"><div class="tk-n">%s</div><div class="cap">%s · %s</div></div></div>'
               '%s<span class="tk-a">%s</span></div>%s</div></a>') % (' soon' if soon else '', ground, mk('lm-' + c, '', 'color:%s' % hue), e(n), e(' · '.join(x for x in (cu, sub) if x)), price(t), ('<p class="tk-note">%s</p>' % e(note)) if note else '', act, stub)
    if not TICKETS: return ''
    if TOTAL_OPEN > len(TICKETS):
        tk += '<a class="tk all" href="#get" aria-label="See all %d openings in the app"><div class="tk-b"><span class="d tab">%d</span><span class="tk-a">See all →</span></div></a>' % (TOTAL_OPEN, TOTAL_OPEN)
    nav = ('<div class="rn-g"><button class="rn prev" type="button" aria-label="Scroll back" disabled>%s</button>'
           '<button class="rn next" type="button" aria-label="Scroll on">%s</button></div>') % (CHL, CHR)
    return ('<div class="jo"><div class="jo-h rv"><div><div class="sh">%s<h3 class="h3">Just opened</h3></div><p class="sh-l">The newest places in Melbourne, from the day they open.</p></div>%s</div>'
            '<div class="rail" data-loop>%s</div></div>') % (mk('lm-opened'), nav, tk)

def mine():
    import math
    hearts = ''.join('<i style="--dx:%dpx;--dy:%dpx;--rt:%ddeg">%s</i>' % (round(math.cos(math.radians(a)) * d), round(math.sin(math.radians(a)) * d), r, mk('rx-loved'))
                     for a, d, r in [(-90, 96, 0), (-125, 88, -18), (-55, 90, 16), (-155, 70, -24), (-25, 74, 22), (-108, 120, -8), (-72, 118, 10), (-140, 106, -14), (-40, 108, 14), (-90, 140, 4)])
    conf = ''.join('<b style="--dx:%dpx;--dy:%dpx;--rt:%ddeg;background:%s"></b>' % (round(math.cos(math.radians(a)) * d), round(math.sin(math.radians(a)) * d), r, c)
                   for a, d, r, c in [(-100, 80, 160, '#FFC247'), (-60, 84, -140, '#ECEBFF'), (-130, 92, 200, '#F5303F'), (-20, 66, -120, '#FFC247'), (-165, 64, 150, '#ECEBFF'), (-80, 130, -180, '#F5303F'), (-115, 126, 120, '#FFC247'), (-45, 124, -160, '#ECEBFF')])
    burst = '<span class="ring"></span>' + hearts + conf
    s1 = ('<div class="scr">%s<div class="tbar">%s</div><div class="hw">'
          '<div class="hw-h"><span class="mw">%s</span><div><div class="hw-n">Tori no Keiji</div><div class="hw-m">Ramen · CBD · %s</div></div></div>'
          '<div class="hw-p"><img src="%s" alt=""></div><div class="hw-q">How was it?</div>'
          '<div class="picks"><div class="pk lv"><div class="mm">%s<span class="burst">%s</span></div><span class="l">Loved it</span></div>'
          '<div class="pk fn"><div class="mm">%s</div><span class="l">It was fine</span></div>'
          '<div class="pk ds"><div class="mm">%s</div><span class="l">Didn’t like it</span></div></div>'
          '</div><p class="hw-note">Then a couple of quick head\u2011to\u2011heads to place it.</p><div class="home"></div></div>') % (
        SBAR, BACK, mk('lm-restaurants'), price(1), blob('ph-tori'), mk('rx-loved'), burst, mk('rx-fine'), mk('rx-disliked'))
    s2 = ('<div class="scr">%s<div class="tbar">%s<span style="font-size:14px;line-height:18px;color:#A6A8C8">1 of 2 at most</span><span style="width:24px"></span></div><div class="du">'
          '<div class="du-t">Which did you prefer?</div><div class="du-c">Placing it among your Loved $ restaurants</div>'
          '<div class="du-m"><div class="dc nw"><div class="in"><div class="ph"><img src="%s" alt=""></div><span class="lb">Just added</span><span class="n">Tori no Keiji</span><span class="m">CBD · $</span></div></div>'
          '<div class="du-d"><i></i>%s<i></i></div>'
          '<div class="dc ol"><div class="in"><div class="ph"><img src="%s" alt=""></div><span class="lb">On your list</span><span class="n">Ikkoryu Fukuoka Ramen</span><span class="m">CBD · $ · 9.4</span></div></div></div>'
          '<div class="tie">%sToo close to call</div></div><div class="home"></div></div>') % (SBAR, BACK, blob('ph-tori'), mk('rx-fine'), blob('ph-ikkoryu'), mk('rx-fine-s'))
    rows = ''.join('<div class="prow%s"><span class="rk">%d</span><div class="tx"><div class="nm">%s</div><div class="cap">%s · %s%s</div></div><span class="sc %s%s"%s>%s</span></div>' % (
        ' new' if new else '', i + 1, e(n), e(sub), price(t), ' · <span class="lov">Just added</span>' if new else '', band(s), ' cu' if new else '', (' data-to="%s" data-at="1150"' % f1(s)) if new else '', f1(s)) for i, (n, sub, t, s, new) in enumerate(SAM))
    s3 = ('<div class="scr">%s<div class="ml-h"><div class="lock" role="img" aria-label="my reccos"><span class="lw" aria-hidden="true">my</span><wbr>%s</div></div>%s'
          '<div class="mlrows">%s</div><div class="home"></div></div>') % (
        SBAR, wm(label='', live=False), ctabs([('restaurants', 'Restaurants', (5, 6), True), ('cafes', 'Cafés', 3, False), ('bars', 'Bars', 2, False), ('pubs', 'Pubs', 0, False)]), rows)
    chs = [('Give it a recco.', 'Loved it, it was fine, or didn’t like it. One tap, and reccos celebrates with you.'),
           ('A couple of quick head\u2011to\u2011heads.', 'Better than Ikkoryu? Pick two or three, and your score works itself out.'),
           ('Your list sorts itself.', 'Every place lands in order, with your score and what to order. Keep a weekly streak going and unlock the heart-eyes app icon.')]
    ch = ''.join(('<button class="ch" type="button"><span class="tl" aria-hidden="true"><i></i></span><span class="se" aria-hidden="true">'
                  '<svg class="a" viewBox="-224.5 -154 449 308"><ellipse cx="-112.5" cy="0" rx="108" ry="150" fill="currentColor"/><ellipse cx="112.5" cy="0" rx="108" ry="150" fill="currentColor"/></svg>'
                  '%s%s</span><span class="ct"><span class="h3">%s</span><span class="p">%s</span></span></button>') % (mk('rx-fine', 'n'), mk('rx-loved', 'd'), t, d) for t, d in chs)
    bars = ''.join('<button type="button" aria-label="Step %d: %s"><i></i></button>' % (i + 1, t) for i, (t, _) in enumerate(chs))
    return ('<section class="act w mine" id="mine">'
            '<div class="ahead rv"><div class="lock" role="img" aria-label="my reccos"><span class="lw" aria-hidden="true">my</span><wbr>%s</div>'
            '<h2 class="h2">Your places, in your order.</h2>'
            '<p class="lede">Been somewhere? Give it a recco, settle it in a couple of head\u2011to\u2011heads, and your list sorts itself. Then you’ve always got an answer when someone asks.</p></div>'
            '<div class="pin"><div class="bars" role="group" aria-label="Steps">%s</div><div class="chs">%s</div>'
            '<div class="pinside" data-loop>%s</div></div>%s</section>') % (wm(label=''), bars, ch, phone('<div class="ss">%s%s%s</div>' % (s1, s2, s3)), payoff())

def payoff():
    av = lambda c, t: '<span class="av" style="background:%s;color:%s">%s</span>' % (TINT[c], ACC[c], t)
    share = ''.join('<li><span class="r">%d</span><span class="n">%s</span><span class="s">%s</span></li>' % (i + 1, e(n), f1(s)) for i, (n, _, _, s, _) in enumerate(SAM[:5]))
    return ('<div class="pay" data-io>'
            '<div class="pay-t"><span class="pay-k">So next time the group chat asks,</span>'
            '<span class="pay-h">check my <span class="hl">reccos.</span></span>'
            '<p class="lede">One link with your best places, sorted by you, for anyone to open. No app needed to look.</p></div>'
            '<div class="thread" aria-label="The group chat again. Simon sends a link to simon’s reccos and says check my reccos. Julie: ok Tori no Keiji it is. Shayla: booked for 7:30.">'
            '<div class="msg q on" data-t="0"><span class="av ghost"></span><div class="mcol"><span class="who"><b>Julie</b> · 6:42 pm</span><span class="bub t1">where should we eat tonight?</span></div></div>'
            '<div class="msg q on" data-t="80">%s<span class="bub t2">anyone?</span></div>'
            '<div class="typing me" data-t="500" data-u="1250"><span class="dots"><i></i><i></i><i></i></span></div>'
            '<div class="me"><div class="lwrap"><div class="link q" data-t="1250"><div class="sharec"><div class="hh">Simon’s top 5</div><div class="ss2">restaurants in Melbourne</div><ol>%s</ol>%s</div>'
            '<div class="link-f"><b>simon’s reccos</b><span>reccos.app/@simon</span></div></div><span class="tap q" data-t="3150">%s</span></div>'
            '<span class="bub mine m2 q" data-t="1650">check my reccos</span></div>'
            '<div class="typing" data-t="2200" data-u="2950"><span class="dots"><i></i><i></i><i></i></span></div>'
            '<div class="msg q" data-t="2950">%s<div class="mcol"><span class="who"><b>Julie</b></span><span class="bub t1">ok Tori no Keiji it is</span></div></div>'
            '<div class="typing" data-t="3500" data-u="4200"><span class="dots"><i></i><i></i><i></i></span></div>'
            '<div class="msg q" data-t="4200">%s<div class="mcol"><span class="who"><b>Shayla</b></span><span class="bub t1">booked for 7:30</span></div></div>'
            '</div></div>') % (av(0, 'J'), share, mk('lm-restaurants', 'wm2'), mk('rx-loved'), av(0, 'J'), av(1, 'S'))

def creators():
    sts = ''
    n = len(STRIP)
    for rep in range(2):
        for k, (h, still, s) in enumerate(STRIP):
            sts += ('<div class="st" style="--bd:-%.1fs"%s><div class="st-f"><img src="%s" alt=""><span class="stc"><img src="%s" alt="">@%s</span></div><span class="stk">%s<b>%s</b></span></div>') % (
                (k + rep * n) * 0.96, ' aria-hidden="true"' if rep else '', blob(still), avatar(h), h, mk('rx-loved'), f1(s))
    who = []
    for h, _, _ in STRIP:
        if h not in who: who.append(h)
    label = 'Videos from %s and @%s, each with their score' % (', '.join('@' + h for h in who[:-1]), who[-1])
    return ('<section class="w" id="creators"><div class="crt rv">'
            '<div class="crt-t"><span class="eyebrow">%sFor creators</span>'
            '<h2 class="h2">Review Melbourne’s food? Your reccos might be ready.</h2>'
            '<p>We build your list from your videos. Check it in a few head\u2011to\u2011heads, get the tick, and share one link with your followers.</p>'
            '<div class="cta2"><a class="light" href="mailto:[contact email]">Get in touch</a><span class="mail">[contact email]</span></div></div>'
            '<div class="strip" data-loop role="img" aria-label="%s"><div class="strip-in" style="--md:%ds">%s</div></div>'
            '</div></section>') % (mk('lm-verified'), label, round(n * 2), sts)

def faq():
    cols = ['', '']
    half = (len(FAQ) + 1) // 2
    for i, (q, a) in enumerate(FAQ):
        cols[0 if i < half else 1] += ('<div class="qa"><button type="button" aria-expanded="false"><span>%s</span><span class="x" aria-hidden="true"></span></button>'
                        '<div class="ans"><div><p>%s</p></div></div></div>') % (e(q), a)
    return ('<section class="faq w" id="faq"><h2 class="h2 rv">Q&amp;A</h2><div class="faq-g"><div class="faq-c">%s</div><div class="faq-c">%s</div></div></section>') % tuple(cols)

def closing():
    return ('<section class="end w rv"><div><div class="lock" role="img" aria-label="make your own reccos"><span class="lw" aria-hidden="true">make your own</span><wbr>%s</div>'
            '<p>Find where Melbourne’s foodies eat, then recommend your own.</p></div>'
            '<a class="tix" href="#get" data-loop aria-label="Get the app, free on iPhone"><span class="tix-in"><span class="tix-k">Free on iPhone</span><span class="tix-r"><span class="tix-h">Get the app</span><span class="tix-go">%s</span></span></span></a>'
            '</section>'
            '<footer class="ft"><div class="w"><span class="ft-l"><a href="/terms">Terms</a> · <a href="/privacy">Privacy</a> · <a href="/guidelines">Guidelines</a></span></div></footer>') % (wm(label=''), ARROW)

def overlays():
    eyes = ''
    masks = ''
    for k, cx in enumerate((428.6, 653.6)):
        masks += ('<mask id="lch%d" maskUnits="userSpaceOnUse" x="%.1f" y="-6" width="236" height="312"><rect x="%.1f" y="-6" width="236" height="312" fill="#fff"/>'
                  '<rect x="%.1f" y="70" width="344" height="160" rx="60" fill="#000" transform="translate(%.1f 150) skewX(-10) translate(%.1f -150)"/></mask>') % (k, cx - 118, cx - 118, cx - 44, cx, -cx)
        eyes += '<ellipse cx="%.1f" cy="150" rx="108" ry="150" mask="url(#lch%d)"/>' % (cx, k)
    launch = ('<div class="launch" aria-hidden="true"><svg viewBox="0 -2 1116.65 304"><defs>%s</defs><g fill="#ECEBFF">'
              '<path class="lre" d="%s" fill-rule="evenodd"/><path class="los" d="%s" fill-rule="evenodd"/><g class="eyes">%s</g></g></svg></div>') % (masks, RE, OS, eyes)
    film = ('<div class="film" role="dialog" aria-modal="true" aria-label="How reccos works"><div class="film-bg"></div>'
            '<div class="film-p"><div class="pv">%s<span>The one-minute walkthrough plays here, with sound.</span></div><button class="film-x" type="button" aria-label="Close the walkthrough">%s</button></div></div>') % (wm(label='reccos', live=False), CLOSE)
    return launch + film

def css():
    return CSS.replace('@img:stroke', blob('stroke')).replace('@img:grain', blob('grain'))

def body(site=False):
    # On the site, a one-line script marks the page as scripted before anything paints, so nothing flashes in and
    # back out. Without JavaScript the page simply shows everything at rest.
    start = '<div class="rc"><script>document.currentScript.parentNode.classList.add("js")</script>' if site else '<div class="rc" ref="{{ rootRef }}">'
    return ('%s<div class="defs" aria-hidden="true"><svg width="0" height="0">%s</svg></div>'
            '<div class="pg">%s<main>%s%s%s%s%s%s</main></div>%s</div>') % (
        start, DEFS, header(), hero(), find(), mine(), creators(), faq(), closing(), overlays())

def canvas_page(w, h, title):
    """A board for the design canvas (its runtime runs the Component)."""
    return ('<!doctype html>\n<html lang="en-AU">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>%s</title>\n<script src="./support.js"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n<style>\n%s\n</style>\n</helmet>\n%s\n</x-dc>\n'
            '<script type="text/x-dc" data-dc-script data-props=\'{"$preview":{"width":%d,"height":%d}}\'>\n%s\n</script>\n</body>\n</html>\n') % (e(title), css(), body(), w, h, JS)

TITLE = 'reccos: Melbourne’s food creators’ reviews, in one place'
DESC = ('Melbourne’s food creators have reviewed hundreds of places on TikTok. reccos puts all their reviews in one place: '
        'scored, on a map and searchable, with the video a tap away. Free on iPhone.')

def site_page():
    """The real page. noindex until launch day (see README): the site stays down until reccos is in the App Store."""
    return ('<!doctype html>\n<html lang="en-AU">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="robots" content="noindex">\n'
            '<meta name="theme-color" content="#0B0C1E">\n<meta name="color-scheme" content="dark">\n'
            '<link rel="icon" href="../favicon.svg" type="image/svg+xml">\n<link rel="icon" href="../favicon-32.png" sizes="32x32" type="image/png">\n'
            '<link rel="apple-touch-icon" href="../apple-touch-icon.png">\n'
            '<meta property="og:type" content="website">\n<meta property="og:title" content="reccos">\n<meta property="og:description" content="%s">\n'
            '<meta property="og:image" content="https://slym00n.github.io/reccos/og.png">\n<meta name="twitter:card" content="summary_large_image">\n'
            '<style>\nhtml,body{margin:0;padding:0;background:#0B0C1E}\n%s\n</style>\n</head>\n<body>\n%s\n'
            '<script>\nclass DCLogic { constructor(props) { this.props = props || {}; } }\n%s\nnew Component({}).rootRef(document.querySelector(\'.rc\'));\n</script>\n'
            '</body>\n</html>\n') % (e(TITLE), e(DESC), e(DESC), css(), body(site=True), JS)

ROOT = os.path.dirname(os.path.dirname(HERE))

def shown():
    """What the page shows, in plain JSON next to it: handy to check a build, and the diff says what changed."""
    return {
        'facts': FACTS,
        'sort': [{'creator': h, 'followers': fl, 'rows': [[n, f1(s)] for n, _, _, s in rows]} for h, _, fl, _, _, rows, _ in CREW],
        'cards': [{'creator': h, 'reviews': n, 'followers': fl, 'top': [[p, f1(s)] for p, s, _ in top]} for h, _, n, fl, top in CREATORS],
        'ask': {'pick': ASKD['pick']['name'] if ASKD['pick'] else None, 'locals': f1(ASKD['pick_score']) if ASKD['pick_score'] is not None else None,
                'reviewed_by': [[h, f1(s)] for s, h in ASKD['revs']],
                'others': [[v['name'], f1(s) if s is not None else None] for v, s, _ in ASKD['others']]},
        'just_opened': {'total': TOTAL_OPEN, 'rail': [{'name': t[0], 'opens': not not t[9], 'date': ('%s %s' % (t[5], t[6])).strip(), 'first_recco': t[8]} for t in TICKETS]},
        'strip': [[h, f1(s)] for h, _, s in STRIP],
    }

def build_site():
    prepare(live.load())
    folder = os.path.join(ROOT, 'site', 'img')
    imgs = {os.path.splitext(f)[0]: f for f in os.listdir(folder)}
    def asset(k):
        if k not in imgs:
            raise SystemExit('Missing image: site/img/%s.*' % k)
        return 'img/' + imgs[k]
    OUT['asset'], OUT['avatar'] = asset, None
    # Don't publish a page that lost its data: a failed or empty read keeps the last good page (the run fails instead).
    if FACTS['foodies'] < 5 or len(CREATORS) < 3 or not CREW:
        raise SystemExit('The live data looks wrong (%r); keeping the current page.' % FACTS)
    _wm[0] = 0
    page = site_page()
    assert 'data:' not in page.replace('data-', ''), 'data URI found'
    with open(os.path.join(ROOT, 'site', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(page)
    with open(os.path.join(ROOT, 'site', 'data.json'), 'w', encoding='utf-8') as f:
        json.dump(shown(), f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write('\n')
    print('site/index.html: %d bytes; %d foodies, %d reviews, %d places; Just opened %d of %d'
          % (len(page), FACTS['foodies'], FACTS['reviews'], FACTS['places'], len(TICKETS), TOTAL_OPEN))

if __name__ == '__main__':
    build_site()
