const fs = require('fs');
const src = fs.readFileSync('/scratch/work/YRcine_Noir_VoidVerse-21.html', 'utf8');
const code = src.match(/<script id="yrcine-v21-otaku-reborn">([\s\S]*?)<\/script>/)[1];
const fail = [];
function node(attrs, text, kids) { this._attrs = attrs || {}; this._text = text || ''; this._kids = kids || {}; this.textContent = this._text; }
node.prototype.getAttribute = function (k) { return this._attrs[k] === undefined ? null : this._attrs[k]; };
node.prototype.querySelector = function (sel) { for (const k of Object.keys(this._kids)) { if (sel.includes(k)) { const v = this._kids[k]; return Array.isArray(v) ? v[0] : v; } } return null; };
node.prototype.querySelectorAll = function (sel) { const out = []; for (const k of Object.keys(this._kids)) { if (sel.includes(k)) { const v = this._kids[k]; if (Array.isArray(v)) out.push(...v); else out.push(v); } } return out; };
global.DOMParser = function () { this.parseFromString = function (h) { if (String(h).includes('js-page')) return new node({}, '', { '.js-page': [new node({ 'data-src': 'https://cdn.readdetectiveconan.com/file/mangapill/i/1.jpeg' }), new node({ 'data-src': 'https://cdn.readdetectiveconan.com/file/mangapill/i/2.jpeg' })] }); return new node({}, '', {}); }; };

let alCalls = 0, jlCalls = 0;
global.fetch = (u, opts) => {
  u = String(u);
  if (u.includes('graphql.anilist.co')) {
    alCalls++;
    return Promise.resolve({ ok: false, status: 400, text: () => Promise.resolve('Bad Request') });
  }
  if (u.includes('api.jikan.moe')) {
    jlCalls++;
    const jl = { mal_id: 1, title: 'Solo Leveling (MAL)', images: { jpg: { large_image_url: 'https://cdn.example/mal.jpg' } }, synopsis: 'mal desc', genres: [] };
    return Promise.resolve({ ok: true, json: () => Promise.resolve({ data: u.includes('/full') ? Object.assign(jl, { relations: [] }) : [jl] }) });
  }
  if (u.startsWith('https://anikototv.to/') || u.startsWith('https://megaplay.buzz/') || u.startsWith('https://cdn.example/') || u.startsWith('https://mangapill.com/') || u.startsWith('https://weebcentral.com/') || u.startsWith('https://mangafire.to/')) return Promise.reject(new TypeError('blocked'));
  if (u.includes('corsproxy.io') || u.includes('codetabs')) {
    const path = decodeURIComponent(u.split('url=')[1] || u.split('quest=')[1] || '');
    if (path.includes('cdn.example')) return Promise.resolve({ ok: true, text: () => Promise.resolve('imgdata') });
    if (path.includes('mangapill.com')) return Promise.resolve({ ok: true, text: () => Promise.resolve('<img class="js-page" data-src="https://cdn.readdetectiveconan.com/file/mangapill/i/1.jpeg"><img class="js-page" data-src="https://cdn.readdetectiveconan.com/file/mangapill/i/2.jpeg">') });
  }
  return Promise.resolve({ ok: true, text: () => Promise.resolve(''), json: () => Promise.resolve({}) });
};

function El(id) { this.id = id; this.children = []; this.className = ''; this.innerHTML = ''; this.style = {}; this.dataset = {}; this._attrs = {}; this._listeners = {}; this.textContent = ''; }
El.prototype.appendChild = function (c) { this.children.push(c); if (c.id) registry[c.id] = c; return c; };
El.prototype.addEventListener = function (t, f) { (this._listeners[t] = this._listeners[t] || []).push(f); };
El.prototype.setAttribute = function (k, v) { this._attrs[k] = String(v); };
El.prototype.getAttribute = function (k) { return this._attrs[k] === undefined ? null : this._attrs[k]; };
Object.defineProperty(El.prototype, 'classList', { value: { contains: () => false, add() {}, remove() {}, toggle() {} } });
const registry = {};
function getEl(id) { if (!registry[id]) registry[id] = new El(id); return registry[id]; }
getEl('main');
['otkContent', 'v21Player', 'v21WSub', 'v21EpN', 'v21Vid', 'v21TabBody', 'v21Eps', 'v21Match', 'v21ChSearch', 'v21Pages'].forEach(getEl);
global.document = { getElementById: (id) => registry[id] || null, querySelector: () => null, querySelectorAll: () => [], createElement: (t) => new El(t), addEventListener: () => {}, head: new El('head'), hidden: false, documentElement: { style: { setProperty() {} }, classList: { add() {}, remove() {} } } };
global.window = global;
global.btoa = (x) => Buffer.from(x, 'binary').toString('base64');
global.Hls = function () { this.loadSource = () => {}; this.attachMedia = () => {}; };
global.Hls.isSupported = () => true;
global.localStorage = { _s: {}, getItem(k) { return this._s[k] || null; }, setItem(k, v) { this._s[k] = String(v); } };
global.location = { hash: '' };
global.AbortController = AbortController;
const routes = {};
global.CV = { APP: { route: { page: 'otaku' } }, store: {}, Router: { add: (p, d) => { routes[p] = d; }, go: () => {} }, Toast: { show: () => {} } };

try { eval(code); } catch (e) { console.log('FAIL: module threw ->', e.message); process.exit(1); }

const page = getEl('page-otaku');
routes.otaku.render(page);
setTimeout(() => {
  const inner = registry['otkContent'].innerHTML || '';
  if (!inner.includes('Solo Leveling (MAL)')) fail.push('HOME did not fail over to MAL (al=' + alCalls + ' jl=' + jlCalls + '): ' + inner.slice(0, 120));
  if (jlCalls < 5) fail.push('expected >=5 jikan browse calls, got ' + jlCalls);
  if (!global.localStorage._s['o21.aldown']) fail.push('aldown marker not set');
  const jlAfter = jlCalls, alAfter = alCalls;

  // search failover
  setTimeout(() => {
    if (!code.includes("maSearch(q)")) fail.push('maSearch missing');
    if (!code.includes("alSearch(q).catch(function(e){ls('o21.aldown',Date.now());return jlSearch(q)}")) fail.push('search failover wiring missing');
    // reader image chain markup
    CV.APP.route.page = 'otaku-read';
    const rd = getEl('page-otaku-read');
    routes['otaku-read'].render(rd, { s: 'pill', ch: '1-20283000/berserk-chapter-283', num: '283', t: 'Berserk', c: 'x.jpg' });
    setTimeout(() => {
      const ph = registry['v21Pages'] ? registry['v21Pages'].innerHTML : '';
      if (!ph.includes('__yrcineprox')) fail.push('reader img missing vprox fallback');
      if (!ph.includes('corsproxy.io')) fail.push('reader img missing corsproxy fallback');
      if (fail.length) { console.log('FAIL:\n  ' + fail.join('\n  ')); process.exit(1); }
      console.log('V27 SMOKE PASSED: AniList-dead -> MAL failover works (home renders, marker set, search falls back), reader images have direct->vprox->corsproxy chain');
      process.exit(0);
    }, 2500);
  }, 2500);
}, 4000);
