"""Copy the legal documents from the app, so the website shows the same words.

    python3 scripts/site/sync_legal.py ../reccos-app

The app's src/lib/legalText.ts is the source (it's generated from the legal drafts). This writes legal.json next to
this file; build.py renders it as /terms, /privacy and /guidelines. Run it whenever the app's legal text changes.
"""
import json, os, re, sys

app = sys.argv[1] if len(sys.argv) > 1 else '../reccos-app'
src = open(os.path.join(app, 'src/lib/legalText.ts'), encoding='utf-8').read()
out = {
    'version': re.search(r"LEGAL_VERSION = '([^']+)'", src).group(1),
    'updated': re.search(r"LEGAL_UPDATED = '([^']+)'", src).group(1),
    'docs': {},
}
for key in ('terms', 'privacy', 'guide'):
    m = re.search(key + r': \{\s*title: "([^"]*)",\s*x: (\[.*?\n    \]),\n  \}', src, re.S)
    if not m:
        raise SystemExit('Could not read the %s document from legalText.ts' % key)
    body = re.sub(r',(\s*\])$', r'\1', m.group(2))
    out['docs'][key] = {'title': m.group(1), 'x': json.loads(body)}
here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, 'legal.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
    f.write('\n')
print('legal.json: %s, %s' % (out['version'], ', '.join('%s %d blocks' % (k, len(d['x'])) for k, d in out['docs'].items())))
