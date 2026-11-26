"""Live data for the landing page.

Reads reccos' public Supabase API with the app's publishable key: the same public reads the web profile makes, so
nothing here is more than anyone can already see in the app. Row-level security hides suspended and hidden people.
Standard library only, so the scheduled GitHub Action needs no installs.
"""
import json
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from zoneinfo import ZoneInfo

SUPABASE_URL = 'https://hlwwmqttvnimvvfjofrh.supabase.co'
KEY = 'sb_publishable_GdTbYMGmWCygM9LpnRC-Dg_YrrOFSJW'  # public by design: the app and web profile ship it
PAGE = 1000


def get(path):
    """Every row for a PostgREST query, a page at a time. Paths must give an order, so the pages don't overlap."""
    out, start = [], 0
    while True:
        req = urllib.request.Request(f'{SUPABASE_URL}/rest/v1/{path}', headers={
            'apikey': KEY, 'Authorization': 'Bearer ' + KEY, 'Range-Unit': 'items', 'Range': f'{start}-{start + PAGE - 1}'})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    rows = json.load(r)
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(2 * (attempt + 1))
        out += rows
        if len(rows) < PAGE:
            return out
        start += PAGE


def ids_in(ids):
    return 'in.(%s)' % ','.join(str(i) for i in sorted(ids))


def storage(bucket, path):
    return f'{SUPABASE_URL}/storage/v1/object/public/{bucket}/{urllib.parse.quote(path)}'


def fixed1(x):
    """A score as the app shows it: JavaScript's toFixed(1), which rounds a tie up (Python's % rounds it to even)."""
    return str(Decimal(x).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))


def melbourne_today():
    return datetime.now(ZoneInfo('Australia/Melbourne')).date()


def load():
    profiles = get('profiles?select=id,username,display_name,avatar_path,creator_verified_at,creator_focus,follower_label,tint'
                   '&is_creator=is.true&order=id')
    by_id = {p['id']: p for p in profiles}
    reccos = []
    users = sorted(by_id)
    for k in range(0, len(users), 40):
        reccos += get('reccos?select=id,user_id,venue_id,category,score,position&user_id=in.(%s)&order=id'
                      % ','.join(users[k:k + 40]))
    opened = get('just_opened?select=venue_id,opened_on,created_at,sort,badge,note&order=venue_id')
    locals_ = {r['venue_id']: r for r in get('venue_locals?select=venue_id,n,score&order=venue_id')}
    reviews = get('creator_reviews?select=user_id,venue_id&order=user_id,venue_id')

    want = {r['venue_id'] for r in reccos} | {o['venue_id'] for o in opened}
    venues = {}
    wl = sorted(want)
    for k in range(0, len(wl), 150):
        for v in get('venues?select=id,name,category,suburb,price_tier,cuisine,status&id=%s&order=id' % ids_in(wl[k:k + 150])):
            venues[v['id']] = v

    creators = {}
    for p in profiles:
        mine = [r for r in reccos if r['user_id'] == p['id'] and r['venue_id'] in venues]
        cats = {}
        for r in mine:
            cats.setdefault(r['category'], []).append(r)
        for c in cats:
            cats[c].sort(key=lambda r: (-r['score'], r['position'] if r['position'] is not None else 0, r['id']))
        creators[p['username']] = {
            'id': p['id'], 'handle': p['username'], 'name': p['display_name'] or p['username'],
            'focus': p['creator_focus'] or '', 'followers': p['follower_label'] or '',
            'avatar': storage('avatars', p['avatar_path']) if p['avatar_path'] else None,
            'verified': bool(p['creator_verified_at']), 'tint': p['tint'] if p['tint'] is not None else 0,
            'reviews': len(mine),
            'counts': {c: len(v) for c, v in cats.items()},
            'top': {c: [{'venue': r['venue_id'], 'score': r['score']} for r in v] for c, v in cats.items()},
        }

    reviewers = {}
    for r in reviews:
        reviewers.setdefault(r['venue_id'], set()).add(r['user_id'])

    return {
        'today': melbourne_today().isoformat(),
        'facts': {'foodies': len(profiles), 'reviews': len([r for r in reccos if r['venue_id'] in venues]),
                  'places': len({r['venue_id'] for r in reccos if r['venue_id'] in venues})},
        'creators': creators,
        'venues': venues,
        'locals': {k: {'n': v['n'], 'score': v['score']} for k, v in locals_.items()},
        'reviewers': {k: len(v) for k, v in reviewers.items()},
        'opened': opened,
    }


# ---------- Just opened: the app's rules (reccos-app src/lib/openings.ts and useOpenings.ts) ----------
RAIL_MAX, SOON_HELD = 6, 2
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def _d(iso):
    return date.fromisoformat(iso[:10])


def is_live(o, today):
    if o['opened_on']:
        return today - timedelta(days=21) <= _d(o['opened_on']) <= today + timedelta(days=60)
    return not o['created_at'] or _d(o['created_at']) >= today - timedelta(days=42)


def is_soon(o, v, today):
    return _d(o['opened_on']) > today if o['opened_on'] else v['status'] == 'opening_soon'


def _by_opening_key(o, today):
    if not o['opened_on']:
        return (2, 0, o['sort'] or 0)
    d = _d(o['opened_on'])
    if d > today:
        return (1, d.toordinal(), o['sort'] or 0)
    return (0, -d.toordinal(), o['sort'] or 0)


def tickets(D):
    """Every live opening as a ticket, then the rail's pick of them, as Find shows to someone with no reccos yet."""
    today = date.fromisoformat(D['today'])
    out = []
    for o in D['opened']:
        v = D['venues'].get(o['venue_id'])
        if not v or v['status'] == 'closed' or not is_live(o, today):
            continue
        reccod = D['locals'].get(v['id'], {}).get('n', 0)
        rev = D['reviewers'].get(v['id'], 0)
        soon = is_soon(o, v, today)
        dm = None
        if o['opened_on']:
            d = _d(o['opened_on'])
            dm = (str(d.day), MON[d.month - 1])
        out.append({'o': o, 'v': v, 'soon': soon, 'dm': dm, 'first': not rev and not reccod, 'talk': max(reccod, rev)})
    out.sort(key=lambda t: _by_opening_key(t['o'], today))

    opened, soon = [], []
    for t in out:
        o = t['o']
        if t['soon']:
            close = max(0.0, 1 - (_d(o['opened_on']) - today).days / 60) if o['opened_on'] else 0.0
            soon.append((close, t))
        else:
            fresh = max(0.0, 1 - (today - _d(o['opened_on'])).days / 21) if o['opened_on'] else 0.5
            opened.append((fresh + 0.5 * min(3, t['talk']), t))
    # Python's sort is stable, so equal scores keep the by-opening order, as the app's comparator does.
    opened.sort(key=lambda x: -x[0])
    soon.sort(key=lambda x: -x[0])
    n_opened = min(len(opened), RAIL_MAX - min(SOON_HELD, len(soon)))
    n_soon = min(len(soon), RAIL_MAX - n_opened)
    rail = [t for _, t in opened[:n_opened]] + [t for _, t in soon[:n_soon]]
    return rail, len(out)
