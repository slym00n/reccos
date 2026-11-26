# reccos

The public web pages for reccos, served by GitHub Pages.

- **Web profile:** `https://slym00n.github.io/reccos/?u=<username>` shows that person's reccos. It's one static page (`index.html`) that reads public data with the app's public (publishable) key. The app's code is in a separate, private repo; this page is a copy of its `web/index.html`.
- **Landing page:** `site/`, generated from live data, with `site/terms/`, `site/privacy/`, `site/guidelines/` and `site/support/` (Help). It stays out of search (`noindex`) until reccos is in the App Store.

## Landing page

`site/index.html` is built by `scripts/site/build.py` from reccos' public data, the same reads the web profile makes:

- the hero's counts (foodies, reviews, places);
- the creator cards (photo, followers, reviews, top 3), the hero's sort and the creators strip;
- Just opened, by the app's rules (`src/lib/openings.ts`): live window, 6 tickets with at most 2 opening soon, "Give it the first recco" until someone has, and See all with the total;
- Or just ask: the pick's Locals score and the foodies who reviewed it.

Who and what is featured is chosen in `scripts/site/content.json`; everything else is live. The My reccos steps and the group chat are a scripted story and don't change.

**Refresh:** `.github/workflows/landing-data.yml` rebuilds the page every hour and commits only when it changed. Run it by hand from the Actions tab ("Landing page data", Run workflow). A failed read fails the run and keeps the last good page. `site/data.json` lists what the page shows, so each commit's diff says what changed.

**Terms, Privacy, Guidelines:** the app's own legal text, rendered like the app's legal reader. `scripts/site/legal.json` is copied from the app's `src/lib/legalText.ts` with `python3 scripts/site/sync_legal.py <path to reccos-app>`; run it whenever the app's legal text changes. **Help** (`site/support/`) is written in `scripts/site/docs.py`; it's the support URL App Store review asks for.

**Build locally:** `python3 scripts/site/build.py` (Python 3.9+, standard library only).

**At launch:** remove the `robots` noindex line in `site_page()`, put in Apple's badge artwork and the App Store link, point the QR at the real download link, fill in the contact email, and move the page to the domain's root (keeping `?u=` profile links working).
