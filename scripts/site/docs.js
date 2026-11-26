// Document pages: the header's glass and reading bar, Contents that follows the text, the wordmark's blink.
(function () {
  const root = document.querySelector('.rc');
  if (!root) return;
  let rm = false;
  try { rm = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  if (rm) root.classList.add('rm');
  const bar = root.querySelector('.hd .prog');
  let raf = 0;
  const onScroll = () => {
    raf = 0;
    const y = window.scrollY || 0;
    root.classList.toggle('scrolled', y > 8);
    const max = document.documentElement.scrollHeight - window.innerHeight;
    if (bar) bar.style.setProperty('--p', max > 0 ? Math.min(1, y / max).toFixed(4) : '0');
  };
  window.addEventListener('scroll', () => { if (!raf) raf = requestAnimationFrame(onScroll); }, { passive: true });
  onScroll();

  // Contents keeps up with the text: the section you're reading is marked, and stays in view in the column.
  const links = Array.from(root.querySelectorAll('.toc a[href^="#"]'));
  const byId = new Map(links.map((a) => [a.getAttribute('href').slice(1), a]));
  const secs = Array.from(root.querySelectorAll('.doc-a .sec[id]'));
  if ('IntersectionObserver' in window && secs.length) {
    let current = null;
    const seen = new Set();
    const mark = () => {
      const first = secs.find((s) => seen.has(s.id));
      if (!first || first === current) return;
      current = first;
      links.forEach((a) => a.classList.toggle('on', a === byId.get(first.id)));
      const a = byId.get(first.id), box = root.querySelector('.toc');
      if (a && box && box.scrollHeight > box.clientHeight) {
        const t = a.offsetTop - box.clientHeight / 2;
        box.scrollTo({ top: Math.max(0, t), behavior: rm ? 'auto' : 'smooth' });
      }
    };
    const io = new IntersectionObserver((es) => {
      es.forEach((en) => { if (en.isIntersecting) seen.add(en.target.id); else seen.delete(en.target.id); });
      mark();
    }, { rootMargin: '-96px 0px -55% 0px' });
    secs.forEach((s) => io.observe(s));
  }

  // A link inside the page glides there (and closes Contents on small screens).
  root.addEventListener('click', (ev) => {
    const a = ev.target.closest && ev.target.closest('a[href^="#"]');
    if (!a) return;
    const id = a.getAttribute('href').slice(1);
    const t = id && document.getElementById(id);
    if (!t) return;
    ev.preventDefault();
    const fold = a.closest('details');
    if (fold) fold.open = false;
    t.scrollIntoView({ behavior: rm ? 'auto' : 'smooth', block: 'start' });
    history.replaceState(null, '', '#' + id);
    // :target only updates on a real navigation, so re-run the "you jumped here" mark by hand.
    t.classList.remove('jumped'); void t.offsetWidth; t.classList.add('jumped');
  });

  // The wordmark blinks now and then, as in the app.
  const wm = root.querySelector('.brand .wm');
  if (wm && !rm) {
    const blink = () => {
      wm.classList.add('blink');
      setTimeout(() => wm.classList.remove('blink'), 240);
      setTimeout(blink, 7000 + Math.random() * 5000);
    };
    setTimeout(blink, 3000);
  }
})();
