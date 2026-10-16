// Screen scanner: runs in the page and returns a list of problems on the current screen.
// Checks: bad text (undefined/NaN/...), bad inline styles, layout overflow, clipped or spilling text,
// interactive elements covered by something else, low contrast, small tap targets, a11y names, duplicate ids.
(opts) => {
  opts = opts || {};
  const host = document.querySelector('#app > div');
  if (!host) return [{ kind: 'fatal', msg: 'app root not found', where: '' }];
  const R = host.getBoundingClientRect();
  const out = [];
  const seen = new Set();
  const short = s => String(s || '').trim().replace(/\s+/g, ' ').slice(0, 70);
  const desc = el => {
    if (!el || !el.tagName) return '';
    const lab = el.getAttribute && (el.getAttribute('aria-label') || el.getAttribute('title'));
    const t = lab || el.innerText || el.value || '';
    return el.tagName.toLowerCase() + (t ? ' "' + short(t) + '"' : '');
  };
  const add = (kind, msg, el) => {
    const k = kind + '|' + msg + '|' + desc(el);
    if (seen.has(k)) return;
    seen.add(k);
    out.push({ kind, msg, where: desc(el) });
  };
  const cs = el => getComputedStyle(el);
  const isVisible = el => {
    const r = el.getBoundingClientRect();
    if (r.width < 0.5 || r.height < 0.5) return false;
    for (let e = el; e && e !== document.body; e = e.parentElement) {
      const s = cs(e);
      if (s.display === 'none' || s.visibility === 'hidden' || parseFloat(s.opacity) === 0) return false;
    }
    return true;
  };
  const all = Array.from(host.querySelectorAll('*'));

  // 1. Bad words in visible text and in attributes.
  const BAD = /\b(undefined|NaN|null|Infinity|true|false)\b|\[object Object\]|\{\{|\}\}/;
  const walker = document.createTreeWalker(host, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = walker.nextNode())) {
    const t = n.nodeValue;
    if (t && BAD.test(t) && n.parentElement && isVisible(n.parentElement)) add('bad-text', 'text contains "' + t.match(BAD)[0] + '": ' + short(t), n.parentElement);
  }
  all.forEach(el => {
    ['aria-label', 'title', 'placeholder', 'value', 'min', 'type'].forEach(a => {
      const v = el.getAttribute(a);
      if (v != null && /\b(undefined|NaN|null|Infinity)\b|\[object Object\]|\{\{/.test(v)) add('bad-attr', a + '="' + short(v) + '"', el);
    });
    const st = el.getAttribute('style');
    if (st && /\b(undefined|NaN|null|Infinity)\b|\[object Object\]/.test(st)) add('bad-style', short(st.match(/[^;]*(undefined|NaN|null|Infinity|\[object Object\])[^;]*/)[0]), el);
  });

  // Elements clipped by an ancestor with overflow other than visible.
  const clipRect = (el, all) => {
    let r = { left: -1e9, right: 1e9, top: -1e9, bottom: 1e9 };
    for (let e = el.parentElement; e && e !== host; e = e.parentElement) {
      const s = cs(e);
      const b = e.getBoundingClientRect();
      // Full-width containers (the screen, scroll areas, sheets) only clip at the screen edge: that is what we look for.
      if (!all && b.width >= R.width - 1) continue;
      if (s.overflowX !== 'visible' || s.overflowY !== 'visible') {
        r = { left: Math.max(r.left, b.left), right: Math.min(r.right, b.right), top: Math.max(r.top, b.top), bottom: Math.min(r.bottom, b.bottom) };
      }
    }
    return r;
  };

  // 2. Anything sticking out of the app sideways (not clipped by an ancestor).
  all.forEach(el => {
    if (!isVisible(el)) return;
    const r = el.getBoundingClientRect();
    if (r.right > R.right + 1 || r.left < R.left - 1) {
      const c = clipRect(el);
      const visRight = Math.min(r.right, c.right), visLeft = Math.max(r.left, c.left);
      if (visRight > R.right + 1 || visLeft < R.left - 1) add('overflow-x', 'sticks out of the app by ' + Math.round(Math.max(r.right - R.right, R.left - r.left)) + 'px', el);
    }
  });
  // Scroll areas that scroll sideways.
  all.forEach(el => {
    const s = cs(el);
    if ((s.overflowY === 'auto' || s.overflowY === 'scroll') && isVisible(el) && el.scrollWidth > el.clientWidth + 1) add('hscroll', 'scroll area is ' + (el.scrollWidth - el.clientWidth) + 'px wider than its box', el);
  });

  // 3. Clipped, spilling or squashed text.
  all.forEach(el => {
    if (!isVisible(el)) return;
    const hasText = Array.from(el.childNodes).some(c => c.nodeType === 3 && c.nodeValue.trim());
    if (!hasText) return;
    const s = cs(el);
    if (s.display === 'inline') return;
    const w = el.clientWidth, sw = el.scrollWidth;
    if (sw > w + 1) {
      if (s.overflowX === 'hidden' || s.overflowX === 'clip') {
        if (s.textOverflow === 'ellipsis') { if (opts.truncation) add('truncated', 'text cut with … (' + sw + ' > ' + w + 'px)', el); }
        else add('clipped-x', 'text cut off sideways (' + sw + ' > ' + w + 'px)', el);
      } else add('spill-x', 'text spills out of its box (' + sw + ' > ' + w + 'px)', el);
    }
    const h = el.clientHeight, shh = el.scrollHeight;
    if (shh > h + 2 && h > 0) {
      if (s.overflowY === 'hidden' || s.overflowY === 'clip') add('clipped-y', 'text cut off vertically (' + shh + ' > ' + h + 'px)', el);
      else if (s.height !== 'auto' && (el.tagName === 'BUTTON' || /height/.test(el.getAttribute('style') || ''))) add('spill-y', 'text taller than its fixed-height box (' + shh + ' > ' + h + 'px)', el);
    }
  });

  // 4. Interactive elements: covered, too small, unnamed.
  const inter = all.filter(el => /^(BUTTON|INPUT|SELECT|TEXTAREA|A|LABEL)$/.test(el.tagName) && isVisible(el));
  const overlays = all.filter(el => {
    if (el.getAttribute('role') === 'dialog') return true;
    const s = cs(el), b = el.getBoundingClientRect();
    return s.position === 'absolute' && parseInt(s.zIndex, 10) >= 10 && Math.abs(b.width - R.width) < 2 && Math.abs(b.height - R.height) < 2;
  });
  const scrollers = all.filter(el => { const s = cs(el); return (s.overflowY === 'auto' || s.overflowY === 'scroll'); });
  inter.forEach(el => {
    if (el.tagName === 'INPUT' && el.type === 'file') return;
    const r = el.getBoundingClientRect();
    // whole-screen scrim buttons behind sheets
    if (r.width >= R.width - 1 && r.height >= R.height * 0.8) return;
    const name = (el.getAttribute('aria-label') || el.innerText || el.value || el.getAttribute('placeholder') || '').trim();
    if (el.tagName === 'BUTTON' && !name) add('a11y', 'button without a name', el);
    if (/^(INPUT|SELECT|TEXTAREA)$/.test(el.tagName) && !el.getAttribute('aria-label') && !(el.id && document.querySelector('label[for="' + el.id + '"]'))) add('a11y', 'field without a label', el);
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    const clip = clipRect(el, true);
    const m = 4; // centres right at the edge of a scroll area are half scrolled out of view
    const inView = cx > clip.left + m && cx < clip.right - m && cy > clip.top + m && cy < clip.bottom - m && cx > R.left && cx < R.right && cy > R.top && cy < R.bottom && cy < window.innerHeight && cx < window.innerWidth;
    if (!inView) return;
    if (!el.disabled && el.tagName !== 'LABEL' && (r.width < 40 || r.height < 40)) add('small-target', 'tap target ' + Math.round(r.width) + '×' + Math.round(r.height) + 'px', el);
    const top = document.elementFromPoint(cx, cy);
    if (!top || el === top || el.contains(top) || top.contains(el)) return;
    // The floating Character button rises over the bottom of the scroll area by design; content there can be scrolled up.
    if (top.closest('nav')) return;
    // Covered by an open modal is expected; covered by anything else is not.
    // Covered by an overlay that does not contain the element (a sheet or pop-up on top) is expected.
    if (overlays.some(o => o.contains(top) && !o.contains(el))) return;
    add('covered', 'covered by ' + desc(top), el);
  });

  // 5. Contrast of visible text.
  const parse = c => {
    if (!c) return null;
    let m = c.match(/^rgba?\(([^)]+)\)$/);
    if (m) { const p = m[1].split(/[\s,\/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
    m = c.match(/^color\(srgb ([^)]+)\)$/);
    if (m) { const p = m[1].split(/[\s\/]+/).filter(Boolean).map(Number); return [p[0] * 255, p[1] * 255, p[2] * 255, p.length > 3 ? p[3] : 1]; }
    return null;
  };
  const blend = (top, bot) => { const a = top[3]; return [top[0] * a + bot[0] * (1 - a), top[1] * a + bot[1] * (1 - a), top[2] * a + bot[2] * (1 - a), 1]; };
  const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const bgOf = el => {
    const layers = [];
    for (let e = el; e; e = e.parentElement) {
      const s = cs(e);
      if (s.backgroundImage && s.backgroundImage !== 'none') return null;
      const c = parse(s.backgroundColor);
      if (c && c[3] > 0) { layers.push(c); if (c[3] >= 1) break; }
    }
    let base = [255, 255, 255, 1];
    for (let i = layers.length - 1; i >= 0; i--) base = blend(layers[i], base);
    return base;
  };
  if (opts.contrast !== false) all.forEach(el => {
    const hasText = Array.from(el.childNodes).some(c => c.nodeType === 3 && c.nodeValue.trim());
    if (!hasText || !isVisible(el)) return;
    for (let e = el; e && e !== host; e = e.parentElement) if (parseFloat(cs(e).opacity) < 1) return; // dimmed on purpose
    const r = el.getBoundingClientRect();
    const cx = r.left + Math.min(r.width / 2, 8), cy = r.top + r.height / 2;
    const top = document.elementFromPoint(cx, cy);
    if (top && !(el === top || el.contains(top) || top.contains(el))) return; // covered
    const s = cs(el);
    const fg = parse(s.color), bg = bgOf(el);
    if (!fg || !bg) return;
    const fgB = fg[3] < 1 ? blend(fg, bg) : fg;
    const cr = ratio(fgB, bg);
    const size = parseFloat(s.fontSize), bold = parseInt(s.fontWeight, 10) >= 700;
    const large = size >= 24 || (bold && size >= 18.66);
    const need = large ? 3 : 4.5;
    if (cr < need) add('contrast', 'contrast ' + cr.toFixed(2) + ' < ' + need + ' (' + s.color + ' on ' + bg.map(v => Math.round(v)).slice(0, 3).join(',') + ', ' + size + 'px)', el);
  });

  // 6. Duplicate ids.
  const ids = {};
  all.forEach(el => { if (el.id) ids[el.id] = (ids[el.id] || 0) + 1; });
  Object.keys(ids).forEach(id => { if (ids[id] > 1) add('dup-id', 'id "' + id + '" used ' + ids[id] + ' times', null); });

  return out;
}
