"""The site's document pages: Terms of Use, Privacy Policy and Community Guidelines (the app's own legal text, from
legal.json; see sync_legal.py) and Help. They read like the app's legal reader: clause numbers in slate, defined
terms in ink, cross-references and the other documents as links, Contents on small screens.
"""
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = {'terms': 'Terms of Use', 'privacy': 'Privacy Policy', 'guide': 'Community Guidelines'}
SLUG = {'terms': 'terms', 'privacy': 'privacy', 'guide': 'guidelines', 'help': 'support'}
BY_NAME = {v: k for k, v in NAMES.items()}


def e(s):
    return html.escape(s, quote=True)


def rd(name):
    return open(os.path.join(HERE, name), encoding='utf-8').read()


# ---------- the legal text, as the app's lib/legal.ts reads it ----------
def runs(s, key, ids):
    """A paragraph's text. Only the first mention of each target in a paragraph is a link, as in the app."""
    out, seen = [], set()

    def text(t):
        pos = 0
        for m in re.finditer(r'\b(Terms of Use|Privacy Policy|Community Guidelines)\b|\b(?:sections?|clauses?) (\d+)(?:\.(\d+))?|\bPart (B)\b', t):
            link = None
            if m.group(1):
                d = BY_NAME[m.group(1)]
                if d != key and d not in seen:
                    seen.add(d)
                    link = '../%s/' % SLUG[d]
            elif m.group(2):
                fine = 'lg-%s-%s' % (m.group(2), m.group(3)) if m.group(3) else None
                to = fine if fine and fine in ids else 'lg-%s' % m.group(2)
                if to in ids and to not in seen:
                    seen.add(to)
                    link = '#' + to
            elif m.group(4):
                to = 'lg-part-' + m.group(4).lower()
                if to in ids and to not in seen:
                    seen.add(to)
                    link = '#' + to
            if link:
                out.append(e(t[pos:m.start()]))
                out.append('<a class="lk" href="%s">%s</a>' % (link, e(m.group(0))))
                pos = m.end()
        out.append(e(t[pos:]))

    pos = 0
    for m in re.finditer(r'\*\*(.+?)\*\*|\*(.+?)\*|\[([^\]]+)\]\((https?:[^)]+)\)', s):
        text(s[pos:m.start()])
        if m.group(1) is not None:
            out.append('<b>%s</b>' % e(m.group(1)))
        elif m.group(2) is not None:
            out.append('<i>%s</i>' % e(m.group(2)))
        else:
            out.append('<a class="lk" href="%s" rel="noopener" target="_blank">%s</a>' % (e(m.group(4)), e(m.group(3))))
        pos = m.end()
    text(s[pos:])
    return ''.join(out)


def legal(key, L):
    src = L['docs'][key]['x']
    ids = set()
    for k, t in src:
        h = re.match(r'^(\d+)\.\s', t) if k == 'H' else None
        if h: ids.add('lg-%s' % h.group(1))
        p = re.match(r'^\*\*(\d+)\.(\d+)\*\*', t) if k == 'P' else None
        if p: ids.add('lg-%s-%s' % (p.group(1), p.group(2)))
        pt = re.match(r'^Part ([A-Z])', t) if k == 'PART' else None
        if pt: ids.add('lg-part-%s' % pt.group(1).lower())
    parts = any(k == 'PART' for k, _ in src)
    hs = 'h3' if parts else 'h2'
    body, toc, lead, tail = [], [], '', ''
    open_sec = open_list = False
    n_sec = 0

    def close_list():
        nonlocal open_list
        if open_list:
            body.append('</ul>')
            open_list = False

    def close_sec():
        nonlocal open_sec
        close_list()
        if open_sec:
            body.append('</section>')
            open_sec = False

    for k, t in src:
        if k == 'PART':
            close_sec()
            m = re.match(r'^(Part ([A-Z])):\s*(.*)$', t)
            label, title = (m.group(1), m.group(3)) if m else (t, '')
            pid = 'lg-part-%s' % (m.group(2).lower() if m else 'x')
            body.append('<div class="part" id="%s"><div class="part-k">%s</div><h2 class="part-t">%s</h2></div>' % (pid, e(label), e(title)))
            toc.append('<li class="tp"><a href="#%s">%s</a></li>' % (pid, e('%s · %s' % (label, title) if title else label)))
        elif k == 'H':
            close_sec()
            m = re.match(r'^(\d+)\.\s+(.*)$', t)
            n_sec += 1
            sid = 'lg-%s' % m.group(1) if m else 'lg-h%d' % n_sec
            num = '<span class="n">%s</span>' % m.group(1) if m else ''
            body.append('<section class="sec" id="%s"><%s class="sec-h">%s<span>%s</span></%s>' % (sid, hs, num, e(m.group(2) if m else t), hs))
            toc.append('<li><a href="#%s">%s<span>%s</span></a></li>' % (sid, ('<span class="n">%s</span>' % m.group(1)) if m else '', e(m.group(2) if m else t)))
            open_sec = True
        elif k == 'I':
            lead = runs(t, key, ids)
        elif k == 'T':
            tail = runs(t, key, ids)
        elif k == 'P':
            close_list()
            m = re.match(r'^\*\*(\d+)\.(\d+)\*\*\s*', t)
            if m:
                body.append('<p id="lg-%s-%s"><span class="cn">%s.%s</span>%s</p>' % (m.group(1), m.group(2), m.group(1), m.group(2), runs(t[m.end():], key, ids)))
            else:
                body.append('<p>%s</p>' % runs(t, key, ids))
        else:  # L and B: list items, lettered or bulleted
            if not open_list:
                body.append('<ul class="dl">')
                open_list = True
            m = re.match(r'^(\([a-z]+\))\s+', t) if k == 'L' else None
            mark = '<span class="lab">%s</span>' % m.group(1) if m else '<span class="dot" aria-hidden="true"></span>'
            body.append('<li>%s<span>%s</span></li>' % (mark, runs(t[m.end():] if m else t, key, ids)))
    close_sec()
    if tail:
        body.append('<p class="tail">%s</p>' % tail)
    return {'lead': lead, 'body': ''.join(body), 'toc': toc, 'sections': n_sec}


# ---------- Help ----------
def help_doc():
    lk = lambda href, t: '<a class="lk" href="%s">%s</a>' % (href, t)
    secs = [
        ('signin', 'Signing in', [
            'reccos is on iPhone, and you sign in with Apple, so there’s no password to remember.']),
        ('profile', 'Your name, username and photo', [
            'Tap your photo at the top of My reccos to open Settings. Your name, username, Instagram, TikTok and profile photo are all there.']),
        ('delete', 'Deleting your account', [
            'In Settings, tap Delete account, then tap again to confirm. We delete your profile, photo, reccos, notes, saves and follows, and it can’t be undone.',
            'The %s says what we keep and for how long.' % lk('../privacy/#lg-9', 'Privacy Policy')]),
        ('report', 'Reporting someone, or wrong details', [
            'On someone’s reccos, tap More, then Report. On a place, tap Something wrong? to report wrong hours or prices. Or email us.',
            'The %s say what isn’t allowed, and what happens after a report.' % lk('../guidelines/', 'Community Guidelines')]),
        ('privacy', 'Your privacy', [
            'Who can see what is in %s, and how to see or correct the information we hold about you is in %s. To ask, email us.'
            % (lk('../privacy/#lg-7', 'What’s public'), lk('../privacy/#lg-11', 'Your choices and rights'))]),
        ('creators', 'For food creators', [
            'Review Melbourne’s food on TikTok? Your reccos might be ready. Email us, and if your list is ready we’ll send you a link to check it and get the tick.']),
    ]
    body = ''.join('<section class="sec" id="%s"><h2 class="sec-h"><span>%s</span></h2>%s</section>' % (i, e(h), ''.join('<p>%s</p>' % p for p in ps)) for i, h, ps in secs)
    toc = ['<li><a href="#%s"><span>%s</span></a></li>' % (i, e(h)) for i, h, _ in secs]
    return {'body': body, 'toc': toc, 'sections': len(secs)}


# ---------- pages ----------
def page(B, key, L, depth='../'):
    """One document page. B is the landing page's build module (its header parts, marks, styles and wordmark)."""
    if key == 'help':
        D = help_doc()
        title, kicker, updated = 'Help', 'Support', ''
        lead = 'Answers to the usual questions are below. For anything else, email us: we read everything.'
    else:
        D = legal(key, L)
        title, kicker, updated = NAMES[key], 'Legal', L['updated']
        lead = D['lead']
    B._wm[0] = 0
    contents = ('<details class="toc-s"><summary><b>Contents</b><span>%d sections</span><i aria-hidden="true">%s</i></summary><ol>%s</ol></details>'
                % (D['sections'], B.CHEV, ''.join(D['toc']))) if D['sections'] > 8 else ''
    others = [k for k in ('terms', 'privacy', 'guide', 'help') if k != key]
    label = lambda k: 'Help' if k == 'help' else NAMES[k]
    also = ''.join('<a href="%s%s/"><span>%s</span>%s</a>' % (depth, SLUG[k], e(label(k)), B.CHEV) for k in others)
    contact = ('<div class="help-c"><div><div class="help-k">Email us</div><div class="help-m">[contact email]</div></div>'
               '<a class="light" href="mailto:[contact email]">Write to us</a></div>') if key == 'help' else ''
    body = ('<div class="rc doc-page"><script>document.currentScript.parentNode.classList.add("js")</script>'
            '<div class="defs" aria-hidden="true"><svg width="0" height="0">%s</svg></div><div class="pg">'
            '<header class="hd"><div class="w"><a class="brand" href="%s" aria-label="reccos home">%s</a><span class="hd-sp"></span>'
            '<a class="gta" href="%s#get"><span class="chip" aria-hidden="true">%s%s</span>Get the app</a></div><span class="prog" aria-hidden="true"></span></header>'
            '<main class="doc w" id="top"><div class="doc-h"><div class="doc-k">%s</div><h1 class="doc-t">%s</h1>%s%s</div>%s'
            '<div class="doc-g"><nav class="toc" aria-label="Contents"><div class="toc-k">On this page</div><ol>%s</ol></nav>'
            '<article class="doc-a">%s%s<div class="also"><div class="also-k">Also read</div><div class="also-g">%s</div></div>'
            '<a class="totop" href="#top">Back to top</a></article></div></main>'
            '<footer class="ft"><div class="w"><span class="ft-l"><a href="%sterms/">Terms</a> · <a href="%sprivacy/">Privacy</a> · <a href="%sguidelines/">Guidelines</a></span></div></footer>'
            '</div></div>') % (
        B.DEFS, depth, B.wm(label='reccos'), depth, B.mk('rx-fine-s', 'eo'), B.mk('rx-loved', 'eh'),
        e(kicker), e(title), ('<div class="doc-u">%s</div>' % e(updated)) if updated else '',
        ('<p class="doc-lead">%s</p>' % lead) if lead else '', contents,
        ''.join(D['toc']), contact, D['body'], also, depth, depth, depth)
    desc = {'terms': 'The terms for using reccos, the app for recommending and finding Melbourne’s restaurants, cafés, bars and pubs.',
            'privacy': 'What reccos collects, how we use it, who sees what, and your choices.',
            'guide': 'How to keep reccos honest, respectful and useful.',
            'help': 'Help with reccos: signing in, your account, deleting it, reporting, privacy, and getting in touch.'}[key]
    return ('<!doctype html>\n<html lang="en-AU">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<title>%s · reccos</title>\n<meta name="description" content="%s">\n<meta name="robots" content="noindex">\n'
            '<meta name="theme-color" content="#0B0C1E">\n<meta name="color-scheme" content="dark">\n'
            '<link rel="icon" href="%sfavicon.svg" type="image/svg+xml">\n<link rel="icon" href="%sfavicon-32.png" sizes="32x32" type="image/png">\n'
            '<link rel="apple-touch-icon" href="%sapple-touch-icon.png">\n'
            '<style>\nhtml,body{margin:0;padding:0;background:#0B0C1E}\n%s\n%s\n</style>\n</head>\n<body>\n%s\n<script>\n%s\n</script>\n</body>\n</html>\n'
            ) % (e(title), e(desc), depth, depth, depth, B.css(), rd('docs.css'), body, rd('docs.js'))


def build_all(B, root):
    L = json.loads(rd('legal.json'))
    for key in ('terms', 'privacy', 'guide', 'help'):
        d = os.path.join(root, 'site', SLUG[key])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(page(B, key, L))
    return L['updated']
