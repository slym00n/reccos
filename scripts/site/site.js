// reccos website, hi-fi. The page is static HTML; this class only adds motion and the few interactions.
// Everything is imperative and class-based, so nothing re-renders under the animations.
class Component extends DCLogic {
  constructor(props) {
    super(props);
    this._offs = [];
    this._t = [];
    this.rootRef = (el) => {
      if (el === this._el) return;
      this.down();
      this._el = el || null;
      if (el) {
        el.classList.add('js');
        setTimeout(() => { if (this._el === el) { try { this.up(el); } catch (e) { el.classList.add('rm'); } } }, 0);
      }
    };
  }

  renderVals() { return { rootRef: this.rootRef }; }

  componentWillUnmount() { this.down(); }

  later(fn, ms) {
    const id = setTimeout(() => { this._t = this._t.filter((x) => x !== id); if (this._el) fn(); }, ms);
    this._t.push(id);
    return id;
  }

  on(t, ev, fn, o) { if (!t) return; t.addEventListener(ev, fn, o); this._offs.push(() => t.removeEventListener(ev, fn, o)); }

  down() {
    this._t.forEach((id) => clearTimeout(id));
    this._t = [];
    this._offs.forEach((f) => { try { f(); } catch (e) {} });
    this._offs = [];
    if (this._raf) cancelAnimationFrame(this._raf);
    this._raf = 0;
  }

  $(s, r) { return (r || this.root).querySelector(s); }
  $$(s, r) { return Array.from((r || this.root).querySelectorAll(s)); }
  io(cb, opts) {
    if (typeof IntersectionObserver === 'undefined') return null;
    const o = new IntersectionObserver(cb, opts);
    this._offs.push(() => o.disconnect());
    return o;
  }

  up(root) {
    this.root = root;
    let rm = false;
    try { rm = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
    this.rm = rm;
    if (rm) root.classList.add('rm');
    // On the canvas the board is drawn at full height, so nothing scrolls: loops run on timers instead.
    const se = document.scrollingElement || document.documentElement;
    this.cv = se.scrollHeight <= window.innerHeight + 60 || window.innerHeight > 2400;
    root.classList.toggle('cv', this.cv);
    try { if (/Android/i.test(navigator.userAgent)) root.classList.add('android'); } catch (e) {}
    this.reveal();
    this.header();
    this.blink();
    const d = this.launch();
    this.hero(d);
    this.sort(d + 1500);
    this.ask();
    this.steps();
    this.thread();
    this.strip();
    this.rail();
    this.faq();
    this.film();
  }

  reveal() {
    const els = this.$$('.rv,[data-io]');
    if (this.rm) { els.forEach((e) => e.classList.add('in')); return; }
    const once = this.io((es) => es.forEach((en) => { if (en.isIntersecting) { en.target.classList.add('in'); once.unobserve(en.target); } }), { rootMargin: '0px 0px -12% 0px', threshold: 0.01 });
    if (!once) { els.forEach((e) => e.classList.add('in')); return; }
    els.forEach((e) => once.observe(e));
    // Loops stop when they're off screen.
    const vis = this.io((es) => es.forEach((en) => en.target.classList.toggle('paused', !en.isIntersecting)), { rootMargin: '160px 0px' });
    if (vis) this.$$('[data-loop]').forEach((e) => vis.observe(e));
  }

  header() {
    const root = this.root;
    const f = () => root.classList.toggle('scrolled', (window.scrollY || 0) > 8);
    f();
    this.on(window, 'scroll', f, { passive: true });
    this.$$('a[href^="#"]').forEach((a) => this.on(a, 'click', (e) => {
      const id = a.getAttribute('href').slice(1);
      const t = id && root.querySelector('#' + id);
      if (!t) return;
      e.preventDefault();
      t.scrollIntoView({ behavior: this.rm ? 'auto' : 'smooth', block: 'start' });
    }));
    if (this.cv) return;
    const links = this.$$('.nav a');
    const map = new Map();
    links.forEach((a) => { const s = root.querySelector(a.getAttribute('href')); if (s) map.set(s, a); });
    const top = this.$('.hero');
    if (top) map.set(top, null);
    const spy = this.io((es) => es.forEach((en) => {
      if (!en.isIntersecting) return;
      const a = map.get(en.target);
      links.forEach((l) => l.classList.toggle('on', l === a));
    }), { rootMargin: '-45% 0px -50% 0px' });
    if (spy) map.forEach((a, s) => spy.observe(s));
  }

  // The wordmark blinks now and then, as in the app: shut for 120ms, sometimes twice.
  blink() {
    if (this.rm) return;
    this.$$('svg.wm.live').forEach((s, i) => {
      const shut = (ms) => { s.classList.add('blink'); this.later(() => s.classList.remove('blink'), ms); };
      const loop = (first) => this.later(() => {
        shut(240);
        if (Math.random() < 0.25) this.later(() => shut(200), 420);
        loop(false);
      }, (first ? 2600 + i * 1100 : 7500) + Math.random() * 3000);
      loop(true);
    });
  }

  // First visit only: the app's launch (eyes, then the letters slide out from behind them).
  launch() {
    if (this.rm) return 0;
    let seen = false;
    try { seen = window.localStorage.getItem('reccos.web.launch') === '1'; window.localStorage.setItem('reccos.web.launch', '1'); } catch (e) {}
    if (seen && !this.cv) return 0;
    const L = this.$('.launch');
    if (!L) return 0;
    this.root.classList.add('launching');
    this.later(() => L.classList.add('out'), 1300);
    this.later(() => { this.root.classList.remove('launching'); L.classList.remove('out'); }, 1700);
    return 1250;
  }

  // The group chat asks, then the headline lands as the answer.
  hero(d) {
    const h = this.$('.hero');
    if (!h) return;
    const seq = [['.m0', 0], ['.st1', 420], ['.m1', 600], ['.h1', 900], ['.lede', 1010], ['.get', 1120], ['.facts', 1230]];
    seq.forEach(([s, t]) => {
      const e = h.querySelector(s);
      if (!e) return;
      if (this.rm) e.classList.add('on'); else this.later(() => e.classList.add('on'), d + 180 + t);
    });
    if (this.rm) return;
    // The group chat repeats: it holds, fades out, then asks again, bubble by bubble.
    const chat = h.querySelector('.chat');
    const parts = [['.m0', 0], ['.st1', 420], ['.m1', 600]].map(([s, t]) => [h.querySelector(s), t]).filter(([e]) => e);
    const HOLD = 6000, OUT = 400, GAP = 700;
    const again = () => {
      if (chat.classList.contains('paused') || document.hidden) { this.later(again, 800); return; }
      parts.forEach(([e]) => e.classList.add('out'));
      this.later(() => {
        parts.forEach(([e]) => e.classList.remove('on', 'out'));
        parts.forEach(([e, t]) => this.later(() => e.classList.add('on'), GAP + t));
        this.later(again, GAP + 600 + HOLD);
      }, OUT);
    };
    this.later(again, d + 180 + 600 + HOLD);
  }

  // The sort: one creator at a time (@eatwithkevin, @melbfoodieee, @brosonbites). Their video tiles fly into the phone
  // and land as scored rows (a round-up video lands as several), the list holds, then the next creator's feed comes in.
  sort(d) {
    const st = this.$('.sort');
    if (!st) return;
    const groups = this.$$('.tg', st).map((g) => this.$$('.tile', g));
    const screens = this.$$('.ks', st);
    if (this.rm) { if (screens[0]) this.$$('.krow', screens[0]).forEach((r) => r.classList.add('on')); return; }
    const GAP = 340, HOLD = 4600, SWAP = 520;
    let g = 0;
    const fly = (t, rows) => {
      const r0 = rows[0];
      if (!r0) return;
      const a = t.getBoundingClientRect(), b = r0.getBoundingClientRect();
      const tx = b.left + b.width * 0.3, ty = b.top + b.height / 2;
      t.style.setProperty('--fx', Math.round(tx - (a.left + a.width / 2)) + 'px');
      t.style.setProperty('--fy', Math.round(ty - (a.top + a.height / 2)) + 'px');
      t.style.setProperty('--fs', Math.max(0.14, (b.height * 1.1) / a.height).toFixed(3));
      t.classList.add('fly');
      rows.forEach((r, i) => this.later(() => r.classList.add('on'), 430 + i * 130));
    };
    const cycle = () => {
      if (st.classList.contains('paused') || document.hidden) { this.later(cycle, 700); return; }
      const tiles = groups[g] || [], scr = screens[g];
      const rows = scr ? this.$$('.krow', scr) : [];
      tiles.forEach((t, k) => {
        const idx = (t.getAttribute('data-rows') || String(k)).split(',').map(Number);
        this.later(() => fly(t, idx.map((i) => rows[i]).filter(Boolean)), k * GAP);
      });
      const extra = rows.length - tiles.length;
      const end = (tiles.length - 1) * GAP + 640 + Math.max(0, extra) * 130 + HOLD;
      this.later(() => rows.forEach((r) => r.classList.add('off')), end);
      this.later(() => {
        rows.forEach((r) => r.classList.remove('on', 'off'));
        tiles.forEach((t) => { t.classList.add('hid'); t.classList.remove('fly'); });
        g = (g + 1) % groups.length;
        screens.forEach((s, i) => s.classList.toggle('on', i === g));
        const next = groups[g] || [];
        next.forEach((t) => { t.classList.add('hid'); t.classList.remove('fly'); });
        void st.offsetWidth;
        next.forEach((t, i) => this.later(() => t.classList.remove('hid'), SWAP + i * 70));
        this.later(cycle, SWAP + next.length * 70 + 1100);
      }, end + 300);
    };
    this.later(cycle, d);
  }

  // Ask reccos: the request types itself, the results bounce up, then the pick's video opens in the in-app player
  // and swipes through every foodie's video of the place.
  ask() {
    const s = this.$('.ascr');
    if (!s) return;
    const q = s.querySelector('.q');
    const full = q.getAttribute('data-q') || q.textContent;
    if (this.rm) { q.textContent = full; s.classList.add('done'); return; }
    const vp = s.querySelector('.vp'), chip = s.querySelector('.gchip');
    const rail = vp && vp.querySelector('.vr');
    const cards = vp ? this.$$('.vc', vp) : [], metas = vp ? this.$$('.vm', vp) : [], dots = vp ? this.$$('.vd i', vp) : [];
    const STEP = 2600;
    const show = (i, now) => {
      if (!rail) return;
      if (now) rail.classList.add('nt');
      rail.style.translate = (-i * 314) + 'px 0';
      cards.forEach((c, k) => { c.classList.remove('live'); if (k === i) { void c.offsetWidth; c.classList.add('live'); } });
      metas.forEach((m, k) => m.classList.toggle('on', k === i));
      dots.forEach((d, k) => d.classList.toggle('on', k === i));
      if (now) { void rail.offsetWidth; rail.classList.remove('nt'); }
    };
    let busy = false;
    const play = (after) => {
      if (!vp || !chip) { after(); return; }
      this.later(() => chip.classList.add('tap'), 1500);
      this.later(() => { chip.classList.remove('tap'); show(0, true); vp.classList.add('open'); }, 1700);
      for (let i = 1; i < cards.length; i++) this.later(() => show(i), 1700 + STEP * i);
      this.later(() => vp.classList.remove('open'), 1700 + STEP * cards.length);
      this.later(after, 1700 + STEP * cards.length + 400);
    };
    const run = (next) => {
      if (busy) return;
      busy = true;
      s.classList.remove('done');
      if (vp) vp.classList.remove('open');
      q.textContent = '';
      let i = 0;
      const type = () => {
        if (i <= full.length) { q.textContent = full.slice(0, i); i += 1; this.later(type, 34 + Math.random() * 46); }
        else this.later(() => { s.classList.add('done'); play(() => { busy = false; next(); }); }, 320);
      };
      this.later(type, 450);
    };
    // The whole demo loops: once the player closes, the results rest for a beat, then the request types again.
    // It only plays while it's on screen; off screen it waits and picks up when it comes back.
    let vis = this.cv, started = false;
    const loop = () => {
      if (!vis || document.hidden) { this.later(loop, 800); return; }
      run(() => this.later(loop, 2400));
    };
    const host = this.$('.ask');
    const o = this.cv ? null : this.io((es) => es.forEach((en) => {
      vis = en.isIntersecting;
      if (vis && !started) { started = true; loop(); }
    }), { threshold: 0.35 });
    if (o && host) o.observe(host); else { vis = true; started = true; loop(); }
  }

  // My reccos: three steps beside a pinned phone. Wide windows follow the scroll; narrow ones, and the canvas,
  // play it as a story that moves on by itself.
  steps() {
    const sec = this.$('.mine');
    if (!sec) return;
    const chs = this.$$('.ch', sec), scrs = this.$$('.ss .scr', sec), bars = this.$$('.bars button', sec);
    const DUR = 5600;
    sec.style.setProperty('--dur', DUR + 'ms');
    let cur = -1, timer = 0, vis = this.cv;
    const go = (k) => {
      if (k === cur) return;
      cur = k;
      chs.forEach((c, i) => { c.classList.toggle('now', i === k); c.classList.toggle('done', i < k); c.setAttribute('aria-current', i === k ? 'step' : 'false'); });
      bars.forEach((b) => b.classList.remove('now'));
      void sec.offsetWidth;
      bars.forEach((b, i) => { b.classList.toggle('now', i === k); b.classList.toggle('done', i < k); });
      scrs.forEach((s, i) => { s.classList.toggle('on', i === k); s.classList.remove('play'); });
      const s = scrs[k];
      if (s && !this.rm) { void s.offsetWidth; s.classList.add('play'); }
      if (s) s.querySelectorAll('.cu').forEach((n) => this.count(n));
    };
    const wide = () => { const pg = this.$('.pg'); return !!pg && pg.clientWidth > 1000; };
    const auto = () => this.cv || !wide();
    const tick = () => {
      if (timer) clearTimeout(timer);
      timer = 0;
      if (!auto() || this.rm) return;
      timer = this.later(() => { if (vis) go((cur + 1) % chs.length); tick(); }, DUR);
    };
    const pin = sec.querySelector('.pin'), side = sec.querySelector('.pinside');
    // Wide and scrolling: the steps and phone stay pinned, and progress through the pin's track picks the step.
    // On a short laptop screen the pinned phone shrinks to fit under the header (at most the design's 0.8).
    const fit = () => {
      if (this.cv) { sec.style.removeProperty('--pz'); return; }
      sec.style.setProperty('--pz', Math.max(0.6, Math.min(0.8, (window.innerHeight - 178) / 844)).toFixed(3));
    };
    fit();
    const run = () => Math.max(1, pin.offsetHeight - (side ? side.offsetHeight : 0));
    const list = sec.querySelector('.chs');
    const fills = chs.map((c) => c.querySelector('.tl'));
    const byScroll = () => {
      if (list) list.classList.toggle('auto', auto());
      if (auto() || !pin) return;
      const p = (110 - pin.getBoundingClientRect().top) / run();
      go(Math.max(0, Math.min(chs.length - 1, Math.floor(p * chs.length))));
      // The rail fills with the scroll, so it shows how far through the three steps you are.
      fills.forEach((f, i) => { if (f) f.style.setProperty('--f', Math.max(0, Math.min(1, p * chs.length - i)).toFixed(3)); });
    };
    const jump = (i) => {
      if (auto() || !pin) { go(i); tick(); return; }
      const y = window.scrollY + pin.getBoundingClientRect().top - 110 + ((i + 0.5) / chs.length) * run();
      window.scrollTo({ top: Math.max(0, y), behavior: this.rm ? 'auto' : 'smooth' });
    };
    chs.forEach((c, i) => this.on(c, 'click', () => jump(i)));
    bars.forEach((b, i) => this.on(b, 'click', () => { go(i); tick(); }));
    go(0);
    let raf = 0;
    this.on(window, 'scroll', () => { if (!raf) raf = requestAnimationFrame(() => { raf = 0; byScroll(); }); }, { passive: true });
    byScroll();
    const seen = this.io((es) => es.forEach((en) => {
      const was = vis;
      vis = en.isIntersecting || this.cv;
      if (vis && !was && auto()) { cur = -1; go(0); tick(); }
    }), { threshold: 0.3 });
    if (seen && pin) seen.observe(pin); else vis = true;
    tick();
    let rt = 0;
    this.on(window, 'resize', () => { clearTimeout(rt); rt = setTimeout(() => { fit(); tick(); byScroll(); }, 200); });
  }

  // The payoff thread picks up where the hero's chat left off.
  thread() {
    const t = this.$('.thread');
    if (!t) return;
    const items = this.$$('[data-t]', t);
    if (this.rm) { items.forEach((e) => { if (!e.classList.contains('typing')) e.classList.add('on'); }); return; }
    let busy = false;
    const play = () => {
      if (busy) return;
      busy = true;
      items.forEach((e) => e.classList.remove('on'));
      let last = 0;
      items.forEach((e) => {
        const at = +e.getAttribute('data-t'), un = e.getAttribute('data-u');
        last = Math.max(last, at, un ? +un : 0);
        this.later(() => e.classList.add('on'), at);
        if (un) this.later(() => e.classList.remove('on'), +un);
      });
      this.later(() => { busy = false; }, last + 200);
    };
    if (this.cv) { play(); const again = () => this.later(() => { play(); again(); }, 12500); again(); return; }
    const o = this.io((es) => es.forEach((en) => { if (en.isIntersecting) { play(); o.disconnect(); } }), { threshold: 0.45 });
    if (o) o.observe(t); else play();
  }

  // The creators' film strip: each still gets its score slapped on as it passes the middle.
  strip() {
    const s = this.$('.strip');
    if (!s || this.rm) return;
    const sts = this.$$('.st', s);
    const loop = () => {
      this._raf = requestAnimationFrame(loop);
      if (s.classList.contains('paused') || document.hidden) return;
      const r = s.getBoundingClientRect();
      const mid = r.left + r.width * 0.5;
      sts.forEach((st) => {
        const k = st.querySelector('.stk');
        if (!k) return;
        const b = st.getBoundingClientRect();
        const c = b.left + b.width / 2;
        const on = k.classList.contains('on');
        if (!on && c <= mid && c > mid - 90) { k.classList.remove('off'); k.classList.add('on'); }
        else if (on && (b.right < r.left + 10 || c > mid + 40)) { k.classList.remove('on'); k.classList.add('off'); }
      });
    };
    loop();
  }

  // Just opened: arrows page through the tickets, and a mouse can drag the rail. Touch and trackpads scroll it natively.
  rail() {
    const r = this.$('.jo .rail');
    if (!r) return;
    const prev = this.$('.jo .rn.prev'), next = this.$('.jo .rn.next');
    const step = () => { const t = r.querySelector('.tk'); return (t ? t.offsetWidth : 320) + (parseFloat(getComputedStyle(r).columnGap) || 14); };
    const sync = () => {
      const max = r.scrollWidth - r.clientWidth;
      if (prev) prev.disabled = r.scrollLeft <= 4;
      if (next) next.disabled = r.scrollLeft >= max - 4;
    };
    const page = (dir) => {
      const s = step(), pad = parseFloat(getComputedStyle(r).paddingLeft) || 0;
      const n = Math.max(1, Math.floor((r.clientWidth - pad) / s));
      const at = Math.round(r.scrollLeft / s);
      r.scrollTo({ left: Math.max(0, (at + dir * n) * s), behavior: this.rm ? 'auto' : 'smooth' });
    };
    this.on(prev, 'click', () => page(-1));
    this.on(next, 'click', () => page(1));
    this.on(r, 'scroll', sync, { passive: true });
    this.on(window, 'resize', sync);
    sync();
    // Mouse drag, then settle on the nearest ticket in the direction of the drag.
    let d = null;
    const kill = (e) => { e.preventDefault(); e.stopImmediatePropagation(); };
    this.on(r, 'dragstart', (e) => e.preventDefault());
    this.on(r, 'pointerdown', (e) => {
      if (e.pointerType !== 'mouse' || e.button !== 0) return;
      const b = r.getBoundingClientRect();
      d = { x: e.clientX, s: r.scrollLeft, k: (b.width / r.offsetWidth) || 1, id: e.pointerId, moved: false };
    });
    this.on(r, 'pointermove', (e) => {
      if (!d || e.pointerId !== d.id) return;
      const dx = (e.clientX - d.x) / d.k;
      if (!d.moved && Math.abs(dx) > 6) { d.moved = true; r.classList.add('drag'); try { r.setPointerCapture(d.id); } catch (er) {} }
      if (d.moved) r.scrollLeft = d.s - dx;
    });
    const end = (e) => {
      if (!d || e.pointerId !== d.id) return;
      const was = d; d = null;
      if (!was.moved) return;
      r.addEventListener('click', kill, true);
      this.later(() => r.removeEventListener('click', kill, true), 60);
      const s = step(), f = r.scrollLeft / s;
      const fwd = r.scrollLeft > was.s;
      const i = fwd ? Math.ceil(f - 0.25) : Math.floor(f + 0.25);
      r.scrollTo({ left: Math.max(0, i * s), behavior: this.rm ? 'auto' : 'smooth' });
      this.later(() => r.classList.remove('drag'), this.rm ? 0 : 480);
    };
    this.on(r, 'pointerup', end);
    this.on(r, 'pointercancel', end);
  }

  // A new score counts up over 600ms, as in the app.
  count(n) {
    const to = parseFloat(n.getAttribute('data-to'));
    const at = +(n.getAttribute('data-at') || 0);
    if (this.rm || !(to > 0)) { n.textContent = to.toFixed(1); return; }
    n.textContent = '0.0';
    this.later(() => {
      const t0 = performance.now();
      const step = (t) => {
        if (!this._el) return;
        const p = Math.min(1, (t - t0) / 600);
        n.textContent = (to * (1 - Math.pow(1 - p, 3))).toFixed(1);
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    }, at);
  }

  faq() {
    this.$$('.qa').forEach((q) => {
      const b = q.querySelector('button');
      this.on(b, 'click', () => {
        const o = !q.classList.contains('open');
        q.classList.toggle('open', o);
        b.setAttribute('aria-expanded', o ? 'true' : 'false');
      });
    });
  }

  // Watch the film: the player grows out of the button, and shrinks back into it.
  film() {
    const f = this.$('.film'), p = this.$('.film-p');
    if (!f || !p) return;
    let from = null;
    const fromRect = () => {
      const a = from.getBoundingClientRect(), b = p.getBoundingClientRect();
      const s = Math.max(0.04, Math.min(a.width / b.width, a.height / b.height));
      return 'translate(' + Math.round(a.left + a.width / 2 - (b.left + b.width / 2)) + 'px,' + Math.round(a.top + a.height / 2 - (b.top + b.height / 2)) + 'px) scale(' + s.toFixed(3) + ')';
    };
    const open = (e) => {
      e.preventDefault();
      from = e.currentTarget.querySelector('.pl') || e.currentTarget;
      f.classList.add('open');
      if (!this.rm) {
        p.style.transition = 'none';
        p.style.transform = fromRect();
        p.style.opacity = '0';
        void p.offsetWidth;
        p.style.transition = 'transform 560ms var(--glide), opacity 160ms linear';
        p.style.transform = 'none';
        p.style.opacity = '1';
      }
      requestAnimationFrame(() => f.classList.add('show'));
      const x = f.querySelector('.film-x');
      if (x) x.focus({ preventScroll: true });
    };
    const close = () => {
      if (!f.classList.contains('open')) return;
      f.classList.remove('show');
      const back = () => { f.classList.remove('open'); p.style.transform = ''; p.style.opacity = ''; p.style.transition = ''; };
      if (this.rm || !from) back();
      else {
        p.style.transition = 'transform 380ms var(--glide), opacity 200ms linear 160ms';
        p.style.transform = fromRect();
        p.style.opacity = '0';
        this.later(back, 400);
      }
      if (from) { const b = from.closest('button') || from; b.focus({ preventScroll: true }); }
    };
    this.$$('[data-film]').forEach((b) => this.on(b, 'click', open));
    this.on(f.querySelector('.film-x'), 'click', close);
    this.on(f.querySelector('.film-bg'), 'click', close);
    this.on(document, 'keydown', (e) => { if (e.key === 'Escape') close(); });
  }
}
