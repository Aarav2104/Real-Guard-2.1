/* Reel Guard frontend. Every privacy decision comes from the Real Guard API; this file only renders and emits metadata. */
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const MY = 'captures_21.04', ACT = ['ALLOW', 'TRANSFORM', 'REDACT', 'BLOCK'];
const GL = { Photography: '📷', AI: '🤖', Tech: '💻', Travel: '✈️', Food: '🍜', Fitness: '🏋️', Music: '🎧', Art: '🎨', Fashion: '👗' };
const KWS = { Photography: /\b(photo\w*|camera|lens|film|shoot\w*)\b/i, AI: /\b(ai|ml|machine learning)\b/i, Tech: /\b(tech|software|python|code|coding)\b/i, Travel: /\b(travel|trip|hike|hiking)\b/i, Food: /\b(food|cook\w*|recipe)\b/i, Fitness: /\b(fit\w*|gym|workout)\b/i, Music: /\b(music|guitar|song)\b/i, Art: /\b(art|design|paint\w*)\b/i, Fashion: /\b(fashion|style|outfit)\b/i };
const catOf = t => Object.keys(KWS).find(k => KWS[k].test(t || '')); // display helper only; the guard runs server-side
let SID, SES, CAT, POSTS = [], BYID = {}, REELS = [], CRE = [], CBY = {}, EVN = 0, BOOT = true, cur = null, tick, io, stT, OUT = '';
const ST = { view: 'home', sub: 'flow', panel: null, prof: null, q: '', th: 0, tab: 'posts', nf: 'All', n: 12 };
const LIKES = new Set(), SAVES = new Set(), FOL = new Set(), SEEN = new Set(), MYPOSTS = [], COMM = {}, SENT = new Set();
const ME = { name: 'Aarav Menon', bio: '"Photographers Never Die."', email: 'aarav.demo@example.com', phone: '+91 90000 00000', age: 21, city: 'Coimbatore' };

/* ---------- icons ---------- */
const P = {
  ig: '<rect x="3" y="3" width="18" height="18" rx="5.5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.3" cy="6.7" r=".9" fill="currentColor" stroke="none"/>',
  home: '<path d="M3.5 11.2 12 3.8l8.5 7.4V20a1 1 0 0 1-1 1H15v-6.2H9V21H4.5a1 1 0 0 1-1-1z"/>',
  reels: '<rect x="3" y="3" width="18" height="18" rx="5.5"/><path d="M10.3 8.4v7.2l5.8-3.6z"/>',
  send: '<path d="M21.5 3 3 10.2l7 3.1 3 7.5z"/><path d="m10 13.3 11-10.3"/>',
  search: '<circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 5 5"/>',
  heart: '<path d="M12 20.6c-.3 0-8.2-4.7-8.2-10.9A4.6 4.6 0 0 1 8.4 5c1.4 0 2.8.7 3.6 2 .8-1.3 2.2-2 3.6-2a4.6 4.6 0 0 1 4.6 4.7c0 6.2-7.9 10.9-8.2 10.9z"/>',
  plus: '<path d="M12 4.5v15M4.5 12h15"/>',
  comment: '<path d="M4.2 19.8 5.4 16A8.6 8.6 0 1 1 8.3 18.7z"/>',
  repost: '<path d="M4 12V10a3 3 0 0 1 3-3h11"/><path d="m15 4 3 3-3 3"/><path d="M20 12v2a3 3 0 0 1-3 3H6"/><path d="m9 20-3-3 3-3"/>',
  bookmark: '<path d="M6.2 3.5h11.6v17L12 16.2 6.2 20.5z"/>',
  dots: '<circle cx="5" cy="12" r="1.4" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="1.4" fill="currentColor" stroke="none"/><circle cx="19" cy="12" r="1.4" fill="currentColor" stroke="none"/>',
  shield: '<path d="M12 3 4.5 6v5.6c0 4.4 3.1 8 7.5 9.4 4.4-1.4 7.5-5 7.5-9.4V6z"/><path d="m8.6 12.1 2.4 2.4 4.4-4.6"/>',
  menu: '<path d="M4 6.5h16M4 12h16M4 17.5h16"/>', up: '<path d="m6 14.5 6-6 6 6"/>', down: '<path d="m6 9.5 6 6 6-6"/>', close: '<path d="m5 5 14 14M19 5 5 19"/>',
  mute: '<path d="M4 9.5h3.6L12 6v12l-4.4-3.5H4z"/><path d="m16 9.5 5 5m0-5-5 5"/>', sound: '<path d="M4 9.5h3.6L12 6v12l-4.4-3.5H4z"/><path d="M16 9a4 4 0 0 1 0 6M18.5 6.5a8 8 0 0 1 0 11"/>',
  compose: '<path d="M12 4.5H7a3 3 0 0 0-3 3v9.5a3 3 0 0 0 3 3h9.5a3 3 0 0 0 3-3V12"/><path d="m17.3 3.7 3 3-8.3 8.3-3.6.6.6-3.6z"/>',
  phone: '<path d="M5 4h4l1.5 4-2 1.3a11 11 0 0 0 5.2 5.2L15 12.5l4 1.5v4a2 2 0 0 1-2 2A13 13 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
  video: '<rect x="3" y="6.5" width="12.5" height="11" rx="3"/><path d="m15.5 11 5-3v8l-5-3z"/>', info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5.5"/><circle cx="12" cy="7.8" r=".9" fill="currentColor" stroke="none"/>',
  mic: '<rect x="9" y="3.5" width="6" height="11" rx="3"/><path d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v3"/>', image: '<rect x="3.5" y="4.5" width="17" height="15" rx="3"/><circle cx="9" cy="10" r="1.6"/><path d="m4 17 5-4.5 4 3.5 3-2.5 4 3.5"/>',
  smile: '<circle cx="12" cy="12" r="9"/><path d="M8.5 14.2a4.2 4.2 0 0 0 7 0"/><circle cx="9" cy="10" r=".9" fill="currentColor" stroke="none"/><circle cx="15" cy="10" r=".9" fill="currentColor" stroke="none"/>',
  sticker: '<path d="M20 12a8 8 0 1 1-8-8h1.5L20 10.5z"/><path d="M13.5 4v4.5a2 2 0 0 0 2 2H20"/>', play: '<path d="M8.5 5.5v13l10.5-6.5z" fill="currentColor"/>', chev: '<path d="m7 10 5 5 5-5"/>',
  gear: '<circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1"/>', check: '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
  grid: '<rect x="4" y="4" width="6.5" height="6.5"/><rect x="13.5" y="4" width="6.5" height="6.5"/><rect x="4" y="13.5" width="6.5" height="6.5"/><rect x="13.5" y="13.5" width="6.5" height="6.5"/>', tag: '<path d="M3.5 3.5h8l9 9-8 8-9-9z"/><circle cx="8" cy="8" r="1.2"/>'
};
const FILL = new Set(['home', 'heart', 'bookmark', 'send']);
const ic = (n, on, sz = 24) => { const f = on && FILL.has(n); return `<svg class="${f ? 'f' : ''}" width="${sz}" height="${sz}" viewBox="0 0 24 24" stroke-width="${on && !f ? 2.5 : 1.9}">${P[n]}</svg>` };

/* ---------- api / events ---------- */
async function api(path, body, method) {
  const o = body !== undefined || method ? { method: method || 'POST', headers: { 'Content-Type': 'application/json' }, body: body !== undefined ? JSON.stringify(body) : undefined } : {};
  const r = await fetch('/api' + path, o);
  if (!r.ok) { let m = r.status; try { m = (await r.json()).detail || m } catch (e) {} throw new Error(m) }
  return r.json();
}
let tt; function toast(h) { const t = $('#t'); t.innerHTML = h; t.style.display = 'block'; clearTimeout(tt); tt = setTimeout(() => t.style.display = 'none', 1700) }
async function emit(field, value, source, cat, purpose) {
  try {
    const d = await api('/events', { session_id: SID, field, value, source: source || ST.view, purpose: purpose || 'recommendation', category: cat || null });
    EVN++; const b = $('#evc'); if (b) b.textContent = EVN;
    if (!BOOT) toast(`Real Guard · ${esc(field)} → <span class="a ${d.action}">${d.action}</span>`); return d;
  } catch (e) { toast('Guard error: ' + esc(e.message)) }
}

/* ---------- small components ---------- */
const hue = h => [...h].reduce((a, c) => (a * 31 + c.charCodeAt(0)) % 360, 7);
const av = (h, s) => `<span class="av" style="width:${s}px;height:${s}px;font-size:${Math.round(s * .42)}px;background:hsl(${hue(h)} 20% 30%)">${esc(h[0].toUpperCase())}</span>`;
const ring = (h, s, attrs = '') => `<span class="ring${SEEN.has(h) ? ' seen' : ''}" ${attrs}><span class="in">${av(h, s)}</span></span>`;
const fmt = n => n >= 1e4 ? Math.round(n / 1000) + 'K' : n >= 1000 ? (n / 1000).toFixed(1).replace('.0', '') + 'K' : String(n);
const grad = p => `linear-gradient(160deg,hsl(${p.hue} 32% 30%),hsl(${(p.hue + 40) % 360} 38% 12%))`;
const nLikes = p => p.likes + (LIKES.has(p.id) ? 1 : 0);
const link = t => esc(t).replace(/#(\w+)/g, '<button class="ht" data-a="tag" data-v="$1">#$1</button>');
const folBtn = (h, cls) => `<button class="${cls}${FOL.has(h) ? ' on' : ''}" data-a="follow" data-u="${esc(h)}">${FOL.has(h) ? 'Following' : 'Follow'}</button>`;
const iconBtn = (a, n, id, on, sz = 24) => `<button class="ib${on ? ' on' : ''}" data-a="${a}" data-id="${id}" data-sz="${sz}" aria-label="${a}">${ic(n, on, sz)}</button>`;
const userLink = h => `<button class="u" data-a="user" data-u="${esc(h)}">${esc(h)}</button>`;

function post(p) {
  const mine = p.by === MY;
  return `<article class="post" data-pid="${p.id}"><div class="ph">${mine ? av(MY, 36) : `<button data-a="user" data-u="${esc(p.by)}">${av(p.by, 36)}</button>`}<div class="meta">${userLink(p.by)}<span class="mu">• ${p.age}</span>${mine ? '' : '<span class="mu">•</span>' + folBtn(p.by, 'fl')}</div><button class="ib" data-a="more" style="width:32px;height:32px">${ic('dots', 0, 22)}</button></div>
<div class="media" data-dbl="${p.id}" style="background:${grad(p)}"><span class="glyph">${GL[p.cat]}</span></div>
<div class="act">${iconBtn('like', 'heart', p.id, LIKES.has(p.id))}${iconBtn('comments', 'comment', p.id, 0)}${iconBtn('share', 'send', p.id, 0)}<span class="sp"></span>${iconBtn('save', 'bookmark', p.id, SAVES.has(p.id))}</div>
<b data-lk="${p.id}">${nLikes(p).toLocaleString()} likes</b><div class="cap">${userLink(p.by)} ${link(p.cap)}</div>
<button class="mu" data-a="comments" data-id="${p.id}">View all ${p.ncom + (COMM[p.id] || []).length} comments</button>
<div class="cin"><input placeholder="Add a comment…" data-ci="${p.id}"><button class="fl" data-a="cpost" data-id="${p.id}">Post</button></div></article>`;
}
const tile = p => `<div class="tl" data-a="open" data-id="${p.id}" style="background:${grad(p)}"><span class="glyph">${GL[p.cat]}</span>${p.kind === 'reel' ? `<span class="pb">${ic('play', 0, 14)}</span>` : ''}<span class="hv"><span>♥ ${fmt(p.likes)}</span><span>● ${p.ncom}</span></span></div>`;

/* ---------- static content ---------- */
const THREADS = [
  { h: 'lens.stories', last: 'Something exciting is coming out', t: '1w', msgs: [{ sys: 'Sep 23, 2026, 7:22 PM' }, { me: 1, text: '👍' }, { sys: 'Sep 23, 2026, 11:58 PM' }, { text: 'Something exciting is coming out' }] },
  { h: 'mira.codes', last: 'Did you see the new model release?', t: '3d', msgs: [{ sys: 'Sep 29, 2026, 9:10 AM' }, { text: 'Did you see the new model release?' }] },
  { h: 'wander.south', last: 'Trail was amazing, sending photos', t: '5d', msgs: [{ sys: 'Sep 27, 2026, 6:40 PM' }, { text: 'Trail was amazing, sending photos' }] },
  { h: 'devdesk.co', last: 'Thanks for the follow!', t: '2w', msgs: [{ sys: 'Sep 18, 2026, 2:05 PM' }, { text: 'Thanks for the follow!' }] }];
const NOTIFS = [
  { k: 'follow', who: 'mira.codes', txt: 'started following you.', t: '42m', grp: 'Today', fb: 1, fy: 0 },
  { k: 'follow', who: 'lens.stories', txt: 'started following you.', t: 'Sep 23', grp: 'This month', fb: 1, fy: 1 },
  { k: 'like', who: 'devdesk.co', more: ' and 10 others', txt: 'liked your comment: Great shot', t: 'Sep 22', grp: 'This month', cat: 'Photography', fy: 1 },
  { k: 'comment', who: 'thread.theory', txt: 'commented: Love the framing', t: 'Sep 20', grp: 'This month', cat: 'Fashion', fy: 0 },
  { k: 'follow', who: 'canvas.club', txt: 'started following you.', t: 'Sep 18', grp: 'This month', fb: 1, fy: 0 },
  { k: 'like', who: 'wander.south', more: ' and 4 others', txt: 'liked your photo.', t: 'Sep 16', grp: 'This month', cat: 'Travel', fy: 1 }];

/* ---------- views ---------- */
function railHTML() {
  const v = ST.view, n = ST.panel === 'notif', b = (a, i, tip, on, x = '') => `<button class="rb" data-a="${a}" ${x} data-tip="${tip}" aria-label="${tip}">${ic(i, on, 26)}</button>`;
  return `<span class="rb logo">${ic('ig', 0, 28)}</span>${b('nav', 'home', 'Home', v === 'home' && !n, 'data-v="home"')}${b('nav', 'reels', 'Reels', v === 'reels' && !n, 'data-v="reels"')}${b('nav', 'send', 'Messages', v === 'messages' && !n, 'data-v="messages"')}${b('nav', 'search', 'Search', v === 'search' && !n, 'data-v="search"')}${b('notif', 'heart', 'Notifications', n)}${b('create', 'plus', 'Create', 0)}<button class="rb" data-a="nav" data-v="profile" data-me="1" data-tip="Profile" aria-label="Profile"><span class="pa${v === 'profile' && !ST.prof && !n ? ' on' : ''}">${av(MY, 28)}</span></button><span class="sp"></span><button class="rb" data-a="nav" data-v="privacy" data-tip="Data Privacy Analysis" aria-label="Data Privacy Analysis">${ic('shield', v === 'privacy' && !n, 26)}<span class="bd" id="evc">${EVN}</span></button><button class="rb" data-a="menu" data-tip="More" aria-label="More">${ic('menu', 0, 26)}</button>`;
}
const VIEWS = {
  home() {
    const feed = [...MYPOSTS.filter(p => p.fresh), ...POSTS].slice(0, ST.n), sug = CRE.filter(h => h !== MY).slice(0, 5);
    const sts = [`<div class="st"><button data-a="create">${ring(MY, 60).replace('class="ring', 'class="ring seen')}</button><span class="n">Your story</span></div>`, ...CRE.slice(0, 10).map(h => `<div class="st"><button data-a="story" data-u="${esc(h)}">${ring(h, 60)}</button><span class="n">${esc(h)}</span></div>`)].join('');
    return `<div class="home"><div class="col"><div class="stories">${sts}</div>${feed.map(post).join('')}${ST.n < POSTS.length ? '<div style="text-align:center;padding:8px 0 40px"><button class="chip" data-a="more-posts">Load more</button></div>' : ''}</div>
<div class="side"><div class="sg">${av(MY, 44)}<div class="t"><b>${MY}</b><div class="mu">${esc(ME.name)}</div></div></div><div class="row2" style="justify-content:space-between;margin:12px 0 4px"><b class="mu">Suggested for you</b></div>
${sug.map(h => `<div class="sg"><button data-a="user" data-u="${esc(h)}">${av(h, 40)}</button><div class="t">${userLink(h)}<div class="mu sm">${CBY[h]} creator</div></div>${folBtn(h, 'fl')}</div>`).join('')}<div class="mu sm" style="margin-top:28px">Prototype · synthetic data only · © 2026 Reel Guard</div></div></div>`;
  },
  reels() {
    const r = p => p.ad ? `<section class="rv" data-i="${REELS.indexOf(p)}"><div class="vid ad"><div class="t1"><span class="brand">N</span><div><b>Nimbus Labs</b><div class="sm" style="color:#6a727b">Sponsored</div></div><span class="tag">AD</span></div>
<div class="hero"><div><div class="eyebrow">NOW HIRING</div><div class="big2">Build what ships.</div></div></div><h2>Software Engineering Internship</h2><div class="sub">Remote · 3 months · Paid stipend</div><div class="pills"><span>Deadline Oct 31</span><span>Open to students</span><span>214 applicants</span></div><ul><li>${ic('check', 0, 18)} Mentorship from senior engineers</li><li>${ic('check', 0, 18)} Ship real features to production</li><li>${ic('check', 0, 18)} Full-time offer track</li></ul>
<button class="cta" data-a="apply">Apply now</button><div class="note">Opens an application form. Submitted fields pass through Real Guard first.</div></div><div class="rcol"><div class="rc">${iconBtn('like', 'heart', p.id, LIKES.has(p.id), 28)}</div><div class="rc">${iconBtn('share', 'send', p.id, 0, 28)}</div><div class="rc">${iconBtn('save', 'bookmark', p.id, SAVES.has(p.id), 28)}</div></div></section>`
      : `<section class="rv" data-i="${REELS.indexOf(p)}"><div class="vid" data-dbl="${p.id}" style="background:${grad(p)}"><span class="glyph">${GL[p.cat]}</span><span class="wtc" id="wt${REELS.indexOf(p)}">0s</span><span class="mt" data-a="mute">${ic('mute', 0, 18)}</span>
<div class="vo"><div class="r1"><button data-a="user" data-u="${esc(p.by)}">${av(p.by, 34)}</button>${userLink(p.by)}<span>•</span>${folBtn(p.by, 'fl').replace('class="fl', 'class="fl" style="color:#fff')}</div><div>${link(p.cap)}</div><div class="sm" style="margin-top:6px;opacity:.85">♪ Original audio · ${esc(p.by)}</div></div></div>
<div class="rcol"><div class="rc">${iconBtn('like', 'heart', p.id, LIKES.has(p.id), 28)}<span data-lkn="${p.id}">${fmt(nLikes(p))}</span></div><div class="rc">${iconBtn('comments', 'comment', p.id, 0, 28)}<span>${fmt(p.ncom * 120)}</span></div><div class="rc">${iconBtn('repost', 'repost', p.id, 0, 28)}<span>${fmt(p.ncom * 9)}</span></div><div class="rc">${iconBtn('share', 'send', p.id, 0, 28)}</div><div class="rc">${iconBtn('save', 'bookmark', p.id, SAVES.has(p.id), 28)}</div><div class="rc">${iconBtn('more', 'dots', p.id, 0, 28)}</div><div class="tile" style="background:${grad(p)}"></div></div></section>`;
    return `<div class="rs" id="rs">${REELS.map(r).join('')}</div><div class="ud"><button data-a="rup" aria-label="Previous reel">${ic('up', 0, 26)}</button><button data-a="rdn" aria-label="Next reel">${ic('down', 0, 26)}</button></div>`;
  },
  messages() {
    const t = THREADS[ST.th];
    return `<div class="msgs"><div class="ml"><div class="mh"><span style="display:flex;align-items:center;gap:6px">${MY} ${ic('chev', 0, 18)}</span><button data-a="create">${ic('compose', 0, 26)}</button></div><label class="sb">${ic('search', 0, 20)}<input placeholder="Search" id="msq"></label>
<div class="notes"><div class="nt"><span class="b">Your note</span>${av(MY, 64)}<span class="mu">Your note</span></div><div class="nt"><span class="b">Working late</span>${av('mira.codes', 64)}<span class="mu">mira.codes</span></div></div>
<div class="mt2"><span>Messages</span><span class="mu">Requests</span></div>${THREADS.map((x, i) => `<div class="th${i === ST.th ? ' on' : ''}" data-a="thread" data-i="${i}">${av(x.h, 52)}<div class="t"><div>${esc(x.h)}</div><div class="mu sm">${esc(x.msgs.at(-1).text || x.last)} · ${x.t}</div></div></div>`).join('')}</div>
<div class="mr"><div class="mrh">${av(t.h, 44)}<div class="t"><b>${esc(t.h)}</b><div class="mu sm">${esc(t.h)}</div></div><div class="ics">${ic('phone', 0, 26)}${ic('video', 0, 26)}${ic('info', 0, 26)}</div></div>
<div class="mb2" id="chat">${t.msgs.map(m => m.sys ? `<div class="dt">${m.sys}</div>` : `<div class="bub${m.me ? ' me' : ''}">${esc(m.text)}</div>`).join('')}</div>
<div class="mi">${ic('smile', 0, 26)}<input id="dmi" placeholder="Message…"><button class="fl" data-a="dm">Send</button>${ic('mic', 0, 24)}${ic('image', 0, 24)}${ic('sticker', 0, 24)}</div></div></div>`;
  },
  search() {
    const q = ST.q.toLowerCase(), c = catOf(ST.q), res = q ? POSTS.filter(p => p.cat === c || p.cap.toLowerCase().includes(q) || p.by.includes(q)) : POSTS;
    return `<div class="wrap" style="padding-top:28px"><label class="sbar">${ic('search', 0, 22)}<input id="q" placeholder="Search" value="${esc(ST.q)}" autocomplete="off"></label>
<div class="chips">${CAT.categories.map(k => `<button class="chip" data-a="tag" data-v="${k.toLowerCase()}">#${k.toLowerCase()}</button>`).join('')}</div>
${q ? `<div class="mu" style="max-width:935px;margin:0 auto 12px">${res.length} results for “${esc(ST.q)}”</div>` : ''}${res.length ? `<div class="grid">${res.map(tile).join('')}</div>` : '<div class="empty">No results found.</div>'}</div>`;
  },
  profile() {
    const h = ST.prof || MY, own = h === MY, all = own ? MYPOSTS : POSTS.filter(p => p.by === h);
    const list = ST.tab === 'saved' ? POSTS.filter(p => SAVES.has(p.id)) : ST.tab === 'reels' ? all.filter(p => p.kind === 'reel') : ST.tab === 'tagged' ? [] : all;
    const tabs = own ? [['posts', 'grid', 'POSTS'], ['saved', 'bookmark', 'SAVED'], ['tagged', 'tag', 'TAGGED']] : [['posts', 'grid', 'POSTS'], ['reels', 'reels', 'REELS']];
    const base = hue(h), stats = own ? [all.length, 8, 15 + FOL.size] : [all.length, 120 + base * 7, 80 + base % 90];
    return `<div class="wrap" style="padding-top:40px"><div class="ptop">${ring(h, 140).replace('class="ring', 'class="ring seen')}<div class="info"><div class="pr1"><h2>${esc(h)}</h2>${own ? `<button class="btn g" data-a="edit">Edit profile</button><button class="btn g" data-a="archive">View archive</button>` : `${folBtn(h, 'btn')}<button class="btn g" data-a="msg" data-u="${esc(h)}">Message</button>`}</div>
<div class="stat"><span><b>${stats[0]}</b> posts</span><span><b>${stats[1]}</b> followers</span><span><b>${stats[2]}</b> following</span></div><div><b>${esc(own ? ME.name : h.replace(/[._]/g, ' '))}</b></div><div>${own ? esc(ME.bio) : esc((CBY[h] || '') + ' creator · synthetic account')}</div></div></div>
<div class="hl"><div><span class="c">${ic('plus', 0, 26)}</span>New</div><div><span class="c">${av('Travel', 60)}</span>Travel</div><div><span class="c">${av('Gear', 60)}</span>Gear</div></div>
<div class="tabs">${tabs.map(t => `<button class="${ST.tab === t[0] ? 'on' : ''}" data-a="ptab" data-v="${t[0]}">${ic(t[1], 0, 14)} ${t[2]}</button>`).join('')}</div>
${list.length ? `<div class="grid">${list.map(tile).join('')}</div>` : `<div class="empty">${ST.tab === 'saved' ? 'Save posts to see them here.' : ST.tab === 'tagged' ? 'Photos of you will appear here.' : 'No posts yet.'}</div>`}</div>`;
  }
};

/* ---------- notifications panel ---------- */
function panelHTML() {
  if (ST.panel !== 'notif') return '';
  const f = ST.nf, list = NOTIFS.filter(n => f === 'All' || (f === 'People you follow' && n.fy) || (f === 'Comments' && n.k === 'comment') || (f === 'Follows' && n.k === 'follow'));
  const grp = g => { const x = list.filter(n => n.grp === g); return x.length ? `<h3>${g}</h3>${x.map(n => `<div class="row">${ring(n.who, 40)}<div class="t"><b>${esc(n.who)}</b>${esc(n.more || '')} ${esc(n.txt)} <span class="mu">${n.t}</span></div>${n.fb ? folBtn(n.who, 'btn') : `<span class="th2" style="background:${grad({ hue: hue(n.cat || 'x') })}">${GL[n.cat] || ''}</span>`}</div>`).join('')}` : '' };
  return `<div class="pn"><button class="x" data-a="notif" aria-label="Close">${ic('close', 0, 24)}</button><h1>Notifications</h1><div class="chips">${['All', 'People you follow', 'Comments', 'Follows'].map(c => `<button class="chip${f === c ? ' on' : ''}" data-a="nf" data-v="${c}">${c}</button>`).join('')}</div>${grp('Today')}${grp('This month')}${list.length ? '' : '<div class="empty">Nothing here yet.</div>'}</div>`;
}

/* ---------- Data Privacy Analysis ---------- */
const pct = v => v == null ? 'n/a' : v.toFixed(1) + '%', tag = a => `<span class="a ${a}">${a}</span>`;
const head = '<th>Field</th><th>Original</th><th>Class</th><th>Action</th><th>Method</th><th>Protected</th><th>Rule</th>';
const prow = e => `<tr><td>${esc(e.field)}</td><td>${esc(String(e.original).slice(0, 40))}</td><td>${esc(e.classification.replace('_', ' ').toLowerCase())}</td><td>${tag(e.action)}</td><td>${e.method}</td><td>${e.protected == null ? '—' : esc(e.protected)}</td><td class="mu">${esc(e.rule)}</td></tr>`;
async function privacyData() {
  const code = encodeURIComponent(SES.jurisdiction.code);
  const [events, m, recs, plist, srcs, llm] = await Promise.all([api(`/events?session_id=${SID}`), api(`/metrics?session_id=${SID}`), api(`/recommendations?session_id=${SID}`), api(`/policies?jurisdiction=${code}`), api(`/policies/${code}/sources`), api('/llm/status')]);
  return { events, m, recs, plist, srcs, llm, ses: SES, code: SES.jurisdiction.code };
}
const SUBS = {
  flow(D) {
    const m = D.m, p = D.ses.policy, v = D.ses.policy_validation, llm = D.plist.find(x => x.origin === 'llm'), s0 = D.srcs[0], types = new Set(D.events.map(e => e.field)).size;
    const st = [['User activity', `${m.records} interactions captured across ${types} metadata types`], ['Metadata collection', 'field, value, source, purpose, timestamp → POST /api/events'], ['Jurisdiction detection', `${D.code} — ${D.ses.jurisdiction.source}`],
      ['Policy discovery', s0 ? `last fetch: ${s0.status}${s0.error ? ' (' + s0.error + ')' : ''} at ${s0.fetched_at}` : 'not run yet — use Discover in the Policy tab'],
      ['LLM policy structuring', llm ? `latest candidate: ${llm.status}` : 'not run yet (needs OPENROUTER_API_KEY and fetched source text)'], ['Policy validation', `${p.id}: ${v.valid ? 'passed' : 'FAILED'} · ${v.warnings.length} warnings`],
      ['Policy repository', `active: ${p.id} (origin: ${p.origin}, version: ${p.version})${D.ses.fallback ? ' — FALLBACK strict policy' : ''}`], ['Real Guard: classify → evaluate', `${m.records} deterministic decisions · avg ${m.latency_avg_ms} ms · p95 ${m.latency_p95_ms} ms`],
      ['Transformation', `${m.counts.TRANSFORM} transformed · ${m.counts.REDACT} redacted · ${m.counts.BLOCK} blocked · ${m.counts.ALLOW} allowed`], ['Recommendation-safe metadata', 'only protected values reach the recommender'], ['Recommendation system', D.recs.items[0] ? `top pick: ${D.recs.items[0].cat} — ${D.recs.items[0].cap}` : 'no signal yet']];
    return `<div class="card">${st.map((x, i) => `<div class="step"><b>${i + 1}</b><div><div style="font-weight:600">${x[0]}</div><div class="mu sm">${esc(x[1])}</div></div></div>`).join('')}</div>`;
  },
  policy(D) {
    const p = D.ses.policy, v = D.ses.policy_validation, j = D.ses.jurisdiction, opts = [['', 'Auto-detect from session'], ['IN', 'India'], ['EU', 'European Union'], ['US-CA', 'California'], ['BR', 'Brazil (no policy)'], ['UNKNOWN', 'Unknown']];
    return `<div class="card"><div class="g2"><div><div class="mu sm">Detected jurisdiction</div><div class="num">${esc(j.code)}</div><div class="sm mu">${esc(j.source)}</div></div><div><div class="mu sm">Active policy</div><b>${esc(p.regulation)}</b><div class="sm mu">${esc(p.id.split(':').slice(0, 2).join(':'))} · ${esc(p.version)} · origin ${esc(p.origin)}</div></div><div><div class="mu sm">Source</div>${esc(p.source)}<div class="sm mu">Retrieved: ${esc(p.retrieved_at || 'offline snapshot')}</div></div><div><div class="mu sm">Validation</div>${v.valid ? '<span class="ok">Passed</span>' : '<span class="err">FAILED</span>'}</div></div>
<label class="mu sm">Simulate platform region signal (policy-update test: all records are reprocessed)</label><select class="apin" id="sim">${opts.map(o => `<option value="${o[0]}"${(j.signals.platform_region || '') === o[0] ? ' selected' : ''}>${o[1]}</option>`).join('')}</select>${D.ses.fallback ? '<div class="err">No validated policy for this jurisdiction — strict fallback applied.</div>' : ''}</div>
<div class="card tw"><b>Rules applied</b><table><tr><th>Field</th><th>Action</th><th>Method</th><th>Param</th><th>Reference</th></tr>${p.rules.map(r => `<tr><td>${r.field}</td><td>${tag(r.action)}</td><td>${r.method}</td><td>${r.param ?? ''}</td><td class="mu">${esc(r.ref)}</td></tr>`).join('')}</table></div>
<div class="card"><b>Policy lifecycle for ${esc(D.code)}</b><div class="mu sm">Discover official sources → LLM structures a candidate → validator gate → you activate. The LLM never makes runtime decisions.</div>
<div class="sm" style="margin-top:8px">LLM provider: <b>${esc(D.llm.provider || 'n/a')}</b> · model: <b>${esc(D.llm.model || 'n/a')}</b> · ${D.llm.configured ? '<span class="ok">API key configured</span>' : `<span class="err">${esc(D.llm.key_env || 'API key')} missing — set it in backend/.env and restart</span>`}</div>
<div class="row2" style="margin:12px 0"><button class="btn g" data-a="discover">1 · Discover sources</button><button class="btn g" data-a="structure">2 · Structure with LLM</button></div>
<div class="tw"><table><tr><th>Policy version</th><th>Origin</th><th>Status</th><th>Errors</th><th></th></tr>${D.plist.map(x => `<tr><td>${esc(x.id.split(':').slice(0, 2).join(':') + ' · ' + x.created_at.slice(11, 19))}</td><td>${x.origin}</td><td>${x.status}</td><td>${x.validation.errors.length}</td><td>${x.validation.valid && x.status !== 'active' ? `<button class="chip" data-a="activate" data-id="${esc(x.id)}">Activate</button>` : ''}</td></tr>`).join('')}</table></div>
<div class="mu sm" style="margin-top:12px">Source fetch log</div><div class="tw"><table><tr><th>When</th><th>Source</th><th>Status</th><th>Detail</th></tr>${D.srcs.map(x => `<tr><td>${esc(x.fetched_at)}</td><td>${esc(x.name)}</td><td>${x.status}</td><td class="mu">${esc(x.error || (x.sha256 || '').slice(0, 12))}</td></tr>`).join('') || '<tr><td colspan="4" class="mu">No fetches yet.</td></tr>'}</table></div><pre id="out" style="display:${OUT ? 'block' : 'none'}">${esc(OUT)}</pre></div>
<div class="card"><b>Validator playground</b><textarea class="apin" id="vp">${esc(JSON.stringify({ jurisdiction: 'IN', regulation: 'Test', source: 'x', version: '1', rules: [{ field: 'email', action: 'ALLOW', method: 'pass', ref: 'r' }, { field: 'age', action: 'TRANSFORM', method: 'age_range', param: 0, ref: '' }] }, null, 1))}</textarea><button class="btn g" data-a="vcheck">Validate</button><pre id="vo" style="display:none"></pre></div>`;
  },
  cmp: D => `<div class="card tw"><table><tr>${head}</tr>${[...D.events].reverse().slice(0, 120).map(prow).join('') || '<tr><td>No events yet.</td></tr>'}</table></div>`,
  ads(D) {
    const ev = D.events.filter(e => e.ad_id && e.purpose === 'job_application');
    const apply = `<div class="card row2" style="justify-content:space-between"><div><b>${esc(CAT.ad.name)}</b><div class="mu sm">Third-party application form. Every submitted field goes through Real Guard.</div></div><button class="btn" data-a="apply">Apply now</button></div>`;
    if (!ev.length) return apply + '<div class="card mu">No application submitted yet.</div>';
    const g = {}; ev.forEach(e => (g[e.ts] ||= []).push(e));
    return apply + Object.entries(g).map(([ts, es]) => { const c = {}; ACT.forEach(a => c[a] = es.filter(e => e.action === a).length); return `<div class="card"><b>${esc(CAT.ad.name)}</b><div class="mu sm" style="margin:4px 0 10px">Submitted ${esc(ts)} · ${es.length} fields · ${ACT.map(a => `${tag(a)} ${c[a]}`).join(' ')}</div><div class="tw"><table><tr>${head}</tr>${es.map(prow).join('')}</table></div></div>` }).join('');
  },
  agg(D) {
    const m = D.m, tot = m.records || 1, cols = { ALLOW: '#3ecf8e', TRANSFORM: '#e8b04a', REDACT: '#b79cff', BLOCK: '#ff6b78' }; let acc = 0;
    const cg = ACT.map(k => { const a = acc, b = acc + m.counts[k] / tot * 100; acc = b; return `${cols[k]} ${a}% ${b}%` }).join(',');
    return `<div class="g2"><div class="card"><div class="mu sm">Privacy risk reduction</div><div class="num">${pct(m.risk_reduction_pct)}</div></div><div class="card"><div class="mu sm">Recommendation utility retained</div><div class="num">${pct(m.utility_retained_pct)}</div></div><div class="card"><div class="mu sm">Records processed</div><div class="num">${m.records}</div></div><div class="card"><div class="mu sm">Guard latency avg / p95</div><div class="num" style="font-size:20px;line-height:36px">${m.latency_avg_ms} / ${m.latency_p95_ms} ms</div></div></div>
<div class="g2"><div class="card"><b>Action distribution</b><div class="row2" style="gap:20px;margin-top:12px"><div class="donut" style="background:conic-gradient(${m.records ? cg : '#262a30 0 100%'})"></div><div>${ACT.map(k => `<div class="lg">${tag(k)} ${m.counts[k]} (${(m.counts[k] / tot * 100).toFixed(0)}%)</div>`).join('')}</div></div><div class="mu sm" style="margin-top:10px">Transformed records stay in the stream with less sensitive values, so the record count does not shrink.</div></div>
<div class="card"><b>Privacy risk (weighted exposure)</b><div class="sm mu" style="margin-top:8px">Before: ${m.risk_before}</div><div class="bar"><i style="width:100%"></i></div><div class="sm mu">After: ${m.risk_after}</div><div class="bar"><i style="width:${m.risk_before ? m.risk_after / m.risk_before * 100 : 0}%"></i></div><b>Recommendation utility</b><div class="sm mu" style="margin-top:8px">Baseline: 100%</div><div class="bar"><i style="width:100%"></i></div><div class="sm mu">Protected: ${pct(m.utility_retained_pct)}</div><div class="bar"><i style="width:${m.utility_retained_pct || 0}%"></i></div></div></div>
<div class="card tw"><b>By classification</b><table><tr><th>Class</th>${ACT.map(a => `<th>${a}</th>`).join('')}</tr>${Object.entries(m.by_class).map(([k, c]) => `<tr><td>${k}</td>${ACT.map(a => `<td>${c[a]}</td>`).join('')}</tr>`).join('')}</table></div>
<div class="card"><b>Transformation correctness</b><div class="mu sm">Runs fixed cases against the India reference policy.</div><button class="btn g" data-a="selftest" style="margin-top:10px">Run self-test</button><pre id="st" style="display:none"></pre></div>
<div class="card sm mu"><b style="color:var(--tx)">Method.</b> Risk = Σ category weight × residual factor (allow 1, pseudonym 0.4, range/region/bucket/category/device/precision 0.3, redact/block 0); weights: direct 10, sensitive 9, quasi/location 5, behavioral 2, recommendation 1. Reduction = (baseline − protected) / baseline × 100. Utility = baseline-scored value of the top-5 chosen from the protected profile ÷ that of the top-5 chosen from the raw profile × 100. Weights are author-chosen assumptions: figures are only meaningful relative to each other, for this session's synthetic data.</div>`;
  },
  rec(D) {
    const L = (t, items) => `<div class="card"><b>${t}</b>${items.map((p, i) => `<div class="step"><b>${i + 1}</b><div>${GL[p.cat]} ${esc(p.cap)}<div class="mu sm">@${p.by} · score ${p.score}</div></div></div>`).join('')}</div>`;
    return `<div class="g2">${L('Baseline (raw metadata, evaluation only)', D.m.recs_raw)}${L('Protected (Real Guard output)', D.m.recs_protected)}</div><div class="card mu sm">Top-5 overlap: ${D.m.top5_overlap}/5 · Simulated recommender, not Instagram's algorithm. The baseline never reaches the recommender.</div>`;
  }
};
async function privacyView() {
  const D = await privacyData(), subs = [['flow', 'Metadata flow'], ['policy', 'Policy'], ['cmp', 'Original vs protected'], ['ads', 'Third-party ads'], ['agg', 'Aggregate & charts'], ['rec', 'Recommendations']];
  return `<div class="wrap"><div class="h">Data Privacy Analysis</div><div class="mu sm" style="margin-bottom:14px">Prototype evaluation on synthetic interactions. Not legal advice; no guarantee of compliance or anonymity.</div><div class="row2" style="margin-bottom:16px;overflow-x:auto;flex-wrap:nowrap">${subs.map(x => `<button class="chip${ST.sub === x[0] ? ' on' : ''}" data-a="sub" data-s="${x[0]}">${x[1]}</button>`).join('')}</div>${SUBS[ST.sub](D)}</div>`;
}

/* ---------- shell ---------- */
async function flush() { if (!cur) return; const s = Math.round((Date.now() - cur.t) / 1000), p = REELS[cur.i]; cur = null; if (s >= 1) emit('watch_time', s, p.ad ? 'ad:reel' : 'reels', p.cat, p.ad ? 'advertisement' : 'recommendation') }
async function render() {
  if (ST.view !== 'reels') await flush(); clearInterval(tick);
  $('#rail').innerHTML = railHTML(); $('#panel').innerHTML = panelHTML();
  try { $('#main').innerHTML = ST.view === 'privacy' ? await privacyView() : VIEWS[ST.view]() } catch (e) { $('#main').innerHTML = `<div class="wrap"><div class="card err">Could not load: ${esc(e.message)}</div></div>` }
  if (ST.view !== 'messages') $('#main').insertAdjacentHTML('beforeend', `<button class="mp" data-a="nav" data-v="messages">${ic('send', 0, 26)}<span>Messages</span><span class="stk">${THREADS.slice(0, 2).map(t => av(t.h, 28)).join('')}</span></button>`);
  if (ST.view === 'reels') {
    io = new IntersectionObserver(es => es.forEach(en => { if (en.isIntersecting && en.intersectionRatio >= .6) { flush(); cur = { i: +en.target.dataset.i, t: Date.now() } } }), { root: $('#rs'), threshold: .6 });
    $$('.rv').forEach(r => io.observe(r));
    tick = setInterval(() => { if (cur) { const e = $('#wt' + cur.i); if (e) e.textContent = Math.round((Date.now() - cur.t) / 1000) + 's' } }, 500);
  }
  if (ST.view === 'messages') { const c = $('#chat'); if (c) c.scrollTop = c.scrollHeight }
  const sim = $('#sim'); if (sim) sim.onchange = async () => { try { SES = await api(`/session/${SID}/region`, { region: sim.value || 'auto' }); toast('Policy → ' + esc(SES.policy.id.split(':')[0])) } catch (e) { toast(esc(e.message)) } render() };
}
const modal = h => { $('#m').innerHTML = h }, closeModal = () => { clearTimeout(stT); const was = $('.sv'); $('#m').innerHTML = ''; if (was) render() };
const xbtn = `<button class="x" data-a="close" aria-label="Close">${ic('close', 0, 22)}</button>`;
function sync(id) {
  const p = BYID[id]; if (!p) return;
  $$(`[data-a=like][data-id="${id}"]`).forEach(b => { const on = LIKES.has(id); b.classList.toggle('on', on); b.innerHTML = ic('heart', on, +b.dataset.sz) });
  $$(`[data-a=save][data-id="${id}"]`).forEach(b => { const on = SAVES.has(id); b.classList.toggle('on', on); b.innerHTML = ic('bookmark', on, +b.dataset.sz) });
  $$(`[data-lk="${id}"]`).forEach(e => e.textContent = nLikes(p).toLocaleString() + ' likes'); $$(`[data-lkn="${id}"]`).forEach(e => e.textContent = fmt(nLikes(p)));
}
function setLike(id, on) { on ? LIKES.add(id) : LIKES.delete(id); sync(id); if (on) emit('like', id, ST.view, BYID[id].cat) }
const cmList = id => [...(BYID[id].comments || []), ...(COMM[id] || [])].map(c => `<div class="cm">${av(c.by, 32)}<div><b>${esc(c.by)}</b> ${esc(c.text)}</div></div>`).join('');
function postComment(id, input) {
  const text = input.value.trim(); if (!text) return; (COMM[id] ||= []).push({ by: MY, text }); input.value = ''; emit('comment', text, ST.view, BYID[id].cat, 'engagement');
  const l = $('#cl'); if (l) l.innerHTML = cmList(id); const b = $(`.post[data-pid="${id}"] [data-a=comments].mu`); if (b) b.textContent = `View all ${BYID[id].ncom + COMM[id].length} comments`;
}
function openProfile(h) { ST.prof = h === MY ? null : h; ST.view = 'profile'; ST.tab = 'posts'; ST.panel = null; if (h !== MY) emit('profile_visit', h, 'profile', CBY[h]); render() }
function showStory(i) {
  clearTimeout(stT); const q = CRE.slice(0, 10); if (i < 0 || i >= q.length) return closeModal();
  const h = q[i], p = POSTS.find(x => x.by === h); SEEN.add(h); emit('story_view', h, 'stories', CBY[h]);
  modal(`<div class="sv"><div class="svb" style="background:${grad(p)}"><div class="pgb"><i></i></div><div class="svh" style="z-index:2">${av(h, 36)}<b>${esc(h)}</b><span class="mu">${p.age}</span>${xbtn}</div><span class="glyph" style="font-size:96px">${GL[p.cat]}</span><div style="margin-top:24px;font-size:18px">${esc(p.cap)}</div><button style="position:absolute;inset:0 0 0 65%" data-a="snext" data-i="${i}" aria-label="Next"></button><button style="position:absolute;inset:0 65% 0 0" data-a="sprev" data-i="${i}" aria-label="Previous"></button></div></div>`);
  stT = setTimeout(() => showStory(i + 1), 5000);
}
const field = (id, label, v = '') => `<label class="lab">${label}</label><input class="inp" id="${id}" value="${esc(v)}">`;
function openForm() { modal(`<div class="ov"><div class="dlg w"><div class="dh">Application · Nimbus Labs${xbtn}</div><div class="db"><div class="mu sm" style="margin-bottom:8px">Software Engineering Internship. Use synthetic data only.</div><div id="fe" class="err sm"></div>${[['name', 'Full name'], ['email', 'Email'], ['phone', 'Phone'], ['age', 'Age'], ['city', 'City'], ['skills', 'Skills'], ['education', 'Education'], ['job_interest', 'Job interest'], ['resume', 'Resume file name']].map(f => field('f_' + f[0], f[1])).join('')}<button class="btn" data-a="submit" style="width:100%">Submit application</button></div></div></div>`) }
function openCreate() { modal(`<div class="ov"><div class="dlg w"><div class="dh">Create new post${xbtn}</div><div class="db"><label class="lab">Topic</label><select class="inp" id="cr_cat">${CAT.categories.map(c => `<option>${c}</option>`).join('')}</select><label class="lab">Caption</label><textarea class="inp" id="cr_cap" placeholder="Write a caption…"></textarea>${field('cr_loc', 'Add location (city)')}<button class="btn" data-a="publish" style="width:100%">Share</button></div></div></div>`) }
function openEdit() { modal(`<div class="ov"><div class="dlg w"><div class="dh">Edit profile${xbtn}</div><div class="db">${[['name', 'Name'], ['email', 'Email'], ['phone', 'Phone'], ['age', 'Age'], ['city', 'City']].map(f => field('ep_' + f[0], f[1], ME[f[0]])).join('')}${field('ep_bio', 'Bio', ME.bio)}<button class="btn" data-a="saveprofile" style="width:100%">Submit</button></div></div></div>`) }
const about = () => modal(`<div class="ov"><div class="dlg w"><div class="dh">About this prototype${xbtn}</div><div class="db"><p>Reel Guard is an Instagram-inspired <b>research prototype</b>. All accounts and content are synthetic. Every interaction becomes metadata that passes through Real Guard before reaching the simulated recommender.</p><p class="mu" style="margin-top:10px">It does not integrate with Instagram, does not guarantee legal compliance, and generalisation does not guarantee anonymity. See Data Privacy Analysis for what happened to each field.</p></div></div></div>`);

/* ---------- events ---------- */
document.addEventListener('click', async e => {
  const mnu = $('.mnu'); if (mnu && !e.target.closest('.mnu') && !e.target.closest('[data-a=menu]')) mnu.remove();
  if (ST.panel && !e.target.closest('.pn') && !e.target.closest('[data-a=notif]')) { ST.panel = null; render() }
  if (e.target.classList.contains('ov')) return closeModal();
  const b = e.target.closest('[data-a]'); if (!b) return; const a = b.dataset.a, id = b.dataset.id, p = BYID[id];
  try {
    switch (a) {
      case 'nav': ST.view = b.dataset.v; ST.panel = null; if (b.dataset.me || b.dataset.v === 'profile') { ST.prof = null; ST.tab = 'posts' } render(); break;
      case 'notif': ST.panel = ST.panel ? null : 'notif'; render(); break;
      case 'nf': ST.nf = b.dataset.v; render(); break;
      case 'create': openCreate(); break;
      case 'menu': { const m = document.createElement('div'); m.className = 'mnu'; m.innerHTML = `<button data-a="about">About this prototype</button><button data-a="reset">Reset demo data</button>`; document.body.appendChild(m); e.stopPropagation(); break }
      case 'about': $('.mnu')?.remove(); about(); break;
      case 'reset': $('.mnu')?.remove(); await api(`/session/${SID}/reset`, {}); [LIKES, SAVES, FOL, SEEN].forEach(s => s.clear()); Object.keys(COMM).forEach(k => delete COMM[k]); EVN = 0; BOOT = true; await seedProfile(); BOOT = false; toast('Demo data reset'); render(); break;
      case 'close': closeModal(); break;
      case 'like': setLike(id, !LIKES.has(id)); break;
      case 'save': { const on = !SAVES.has(id); on ? SAVES.add(id) : SAVES.delete(id); sync(id); if (on) emit('save', id, ST.view, p.cat); break }
      case 'repost': emit('repost', id, ST.view, p.cat); break;
      case 'comments': modal(`<div class="ov"><div class="dlg w"><div class="dh">Comments${xbtn}</div><div class="db"><div id="cl">${cmList(id)}</div><div class="cin" style="margin-top:8px"><input id="cmi" placeholder="Add a comment…" data-ci="${id}" autofocus><button class="fl" data-a="cpost" data-id="${id}" data-in="cmi">Post</button></div></div></div></div>`); break;
      case 'cpost': postComment(id, b.dataset.in ? $('#' + b.dataset.in) : $(`[data-ci="${id}"]`)); break;
      case 'share': modal(`<div class="ov"><div class="dlg"><div class="dh">Share${xbtn}</div><div class="db">${THREADS.map(t => `<div class="sg">${av(t.h, 44)}<div class="t"><b>${esc(t.h)}</b></div><button class="btn" data-a="sendto" data-id="${id}" data-h="${esc(t.h)}">Send</button></div>`).join('')}</div></div></div>`); break;
      case 'sendto': b.textContent = 'Sent'; b.classList.add('g'); emit('share', id, ST.view, p.cat); break;
      case 'follow': { const u = b.dataset.u, on = !FOL.has(u); on ? FOL.add(u) : FOL.delete(u); $$(`[data-a=follow][data-u="${u}"]`).forEach(x => { x.classList.toggle('on', on); x.textContent = on ? 'Following' : 'Follow' }); if (on) emit('follow', u, ST.view, CBY[u]); break }
      case 'user': openProfile(b.dataset.u); break;
      case 'tag': emit('hashtag', '#' + b.dataset.v, ST.view, catOf(b.dataset.v)); ST.q = b.dataset.v; ST.view = 'search'; ST.panel = null; modal(''); render(); break;
      case 'open': modal(`<div class="ov"><div class="dlg w" style="padding:0 0 8px"><div class="dh">${esc(p.by)}${xbtn}</div><div style="padding:8px 16px 0">${post(p)}</div></div></div>`); break;
      case 'more': case 'archive': toast('Not available in this prototype'); break;
      case 'more-posts': ST.n += 9; render(); break;
      case 'story': showStory(CRE.slice(0, 10).indexOf(b.dataset.u)); break;
      case 'snext': showStory(+b.dataset.i + 1); break;
      case 'sprev': showStory(+b.dataset.i - 1); break;
      case 'mute': { const on = b.dataset.on !== '1'; b.dataset.on = on ? '1' : '0'; b.innerHTML = ic(on ? 'sound' : 'mute', 0, 18); break }
      case 'rup': case 'rdn': { const r = $('#rs'); r.scrollBy({ top: (a === 'rdn' ? 1 : -1) * r.clientHeight, behavior: 'smooth' }); break }
      case 'thread': ST.th = +b.dataset.i; render(); break;
      case 'dm': sendDm(); break;
      case 'msg': { let i = THREADS.findIndex(t => t.h === b.dataset.u); if (i < 0) { THREADS.push({ h: b.dataset.u, last: '', t: 'now', msgs: [] }); i = THREADS.length - 1 } ST.th = i; ST.view = 'messages'; render(); break }
      case 'ptab': ST.tab = b.dataset.v; render(); break;
      case 'edit': openEdit(); break;
      case 'saveprofile': { let n = 0; for (const k of ['name', 'email', 'phone', 'age', 'city']) { const v = $('#ep_' + k).value.trim(); if (v && String(ME[k]) !== v) { ME[k] = v; n++; await emit(k, v, 'profile', null, 'profile') } } ME.bio = $('#ep_bio').value.trim() || ME.bio; closeModal(); toast(n ? `${n} field(s) sent through Real Guard` : 'No changes'); render(); break }
      case 'publish': {
        const cap = $('#cr_cap').value.trim(), cat = $('#cr_cat').value, loc = $('#cr_loc').value.trim(); if (!cap) return toast('Add a caption first');
        const np = { id: 'u' + Date.now(), cat, by: MY, cap, likes: 0, ncom: 0, age: 'now', kind: 'photo', hue: (CAT.categories.indexOf(cat)) * 40 + 15, comments: [], fresh: 1 }; MYPOSTS.unshift(np); BYID[np.id] = np;
        await emit('caption', cap, 'post_creation', cat, 'post_creation'); if (loc) await emit('city', loc, 'post_creation', cat, 'post_creation'); closeModal(); ST.view = 'home'; render(); break
      }
      case 'apply': openForm(); break;
      case 'submit': {
        const g = k => $('#f_' + k).value.trim(); if (!g('name')) return $('#fe').textContent = 'Name is required.'; if (!/^\S+@\S+\.\S+$/.test(g('email'))) return $('#fe').textContent = 'Enter a valid email.';
        const items = ['name', 'email', 'phone', 'age', 'city', 'skills', 'education', 'job_interest', 'resume'].filter(k => g(k)).map(k => ({ field: k, value: g(k) }));
        const r = await api('/events/batch', { session_id: SID, items, source: 'ad:nimbus_labs', purpose: 'job_application', ad_id: CAT.ad.id, category: 'Tech' }); EVN += r.decisions.length; $('#evc').textContent = EVN;
        modal(`<div class="ov"><div class="dlg"><div class="dh">Application submitted${xbtn}</div><div class="db"><p>${r.decisions.length} fields went through Real Guard before reaching the recommender.</p><p class="mu" style="margin:8px 0 14px">See Data Privacy Analysis → Third-party ads.</p><button class="btn" data-a="close">Done</button></div></div></div>`); if (ST.view === 'privacy') render(); break
      }
      case 'sub': ST.sub = b.dataset.s; render(); break;
      case 'discover': OUT = JSON.stringify((await api(`/policies/${SES.jurisdiction.code}/discover`, {})).results, null, 1); render(); break;
      case 'structure': { const r = await api(`/policies/${SES.jurisdiction.code}/structure`, {}); OUT = (r.ok ? 'Candidate policy created and passed validation. Review it, then Activate.' : 'Not completed: ' + (r.message || (r.validation ? r.validation.errors.join('; ') : r.status))) + '\n' + JSON.stringify(r, null, 1); render(); break }
      case 'activate': OUT = JSON.stringify(await api(`/policies/${encodeURIComponent(id)}/activate`, {}), null, 1); SES = await api(`/session/${SID}`); await api(`/session/${SID}/reprocess`, {}); render(); break;
      case 'vcheck': { let pol; try { pol = JSON.parse($('#vp').value) } catch (err) { return show('#vo', 'Invalid JSON: ' + err.message) } const v = await api('/policies/validate', { policy: pol }); show('#vo', (v.valid ? 'VALID' : 'REJECTED — not activated') + '\n• ' + [...v.errors, ...v.warnings.map(w => '(warning) ' + w)].join('\n• ')); break }
      case 'selftest': { const r = await api('/selftest'); show('#st', `${r.passed}/${r.total} passed (${r.policy.split(':')[0]})\n` + r.cases.map(c => `${c.pass ? '✓' : '✗'} ${c.field}: ${c.input} → ${c.got} (expected ${c.expected})`).join('\n')); break }
    }
  } catch (err) { toast(esc(err.message)) }
});
const show = (id, t) => { const o = $(id); if (o) { o.style.display = 'block'; o.textContent = t } };
function sendDm() { const i = $('#dmi'), text = i.value.trim(); if (!text) return; THREADS[ST.th].msgs.push({ me: 1, text }); emit('dm', text, 'messages', catOf(text), 'messaging'); render() }
async function doSearch(t) { ST.q = t; emit('search', t, 'search', catOf(t)); await render(); const q = $('#q'); if (q) { q.focus(); q.setSelectionRange(t.length, t.length) } }
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { if ($('.mnu')) $('.mnu').remove(); else if ($('#m').innerHTML) closeModal(); else if (ST.panel) { ST.panel = null; render() } return }
  if (e.key !== 'Enter') return; const t = e.target;
  if (t.id === 'q' && t.value.trim()) doSearch(t.value.trim()); else if (t.id === 'dmi') sendDm(); else if (t.dataset && t.dataset.ci) postComment(t.dataset.ci, t);
});
document.addEventListener('dblclick', e => { const m = e.target.closest('[data-dbl]'); if (!m) return; const id = m.dataset.dbl; if (!LIKES.has(id)) setLike(id, true); const h = document.createElement('span'); h.className = 'pop'; h.innerHTML = ic('heart', 1, 84); m.appendChild(h); setTimeout(() => h.remove(), 700) });

/* ---------- boot ---------- */
async function seedProfile() { for (const [f, v] of [['account_id', MY], ['name', ME.name], ['email', ME.email], ['phone', ME.phone], ['age', ME.age], ['city', ME.city], ['geo', '11.0168,76.9558'], ['device', navigator.userAgent]]) await emit(f, v, 'profile', null, 'profile') }
(async function boot() {
  try {
    CAT = await api('/catalog'); POSTS = CAT.posts; POSTS.forEach(p => { BYID[p.id] = p; CBY[p.by] ??= p.cat; if (!CRE.includes(p.by)) CRE.push(p.by) }); BYID[CAT.ad.id] = CAT.ad; CBY[MY] = 'Photography';
    const rl = POSTS.filter(p => p.kind === 'reel'); REELS = [...rl.slice(0, 3), CAT.ad, ...rl.slice(3)];
    for (let i = 0; i < 6; i++) { const c = ['Photography', 'Travel', 'Art'][i % 3], mp = { id: 'm' + i, cat: c, by: MY, cap: `Archive frame ${i + 1} #${c.toLowerCase()}`, likes: 20 + i * 7, ncom: i, age: '2w', kind: 'photo', hue: CAT.categories.indexOf(c) * 40 + 15, comments: [] }; MYPOSTS.push(mp); BYID[mp.id] = mp }
    const s = await api('/session', { tz: Intl.DateTimeFormat().resolvedOptions().timeZone, lang: navigator.language }); SID = s.session_id; SES = await api('/session/' + SID);
    await seedProfile(); BOOT = false; render();
  } catch (e) { $('#main').innerHTML = `<div class="wrap"><div class="card err">Cannot reach the Real Guard API (${esc(e.message)}). Start the backend: <code>uvicorn app.main:app</code> from <code>backend/</code>.</div></div>` }
})();
