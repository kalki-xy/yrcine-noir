#!/usr/bin/env python3
# v27: AniList->MAL auto-failover (CGNAT 400s), Mangapill CDN image fix (readdetectiveconan referer + vprox fallback)
src = '/workspace/notes/v26-build.py'
s = open(src).read()

def span(start_marker, end_marker, new_block):
    global s
    assert s.count(start_marker) == 1, 'start not unique: ' + start_marker[:60]
    i = s.find(start_marker)
    j = s.find(end_marker, i + len(start_marker))
    assert j >= 0, 'end missing: ' + end_marker[:60]
    s = s[:i] + new_block + s[j:]

# 0. version
assert "CV.VERSION='26.0.0';" in s
s = s.replace("CV.VERSION='26.0.0';", "CV.VERSION='27.0.0';")

# 1. maSearch/maBrowse/maInfo failover
OLD = "function maSearch(q){return ameta()==='mal'?jlSearch(q):alSearch(q)}\nfunction maBrowse(kind){return ameta()==='mal'?jlBrowse(kind):alBrowse(kind)}\nfunction maInfo(id){return id.indexOf('mal:')===0?jlInfo(id.slice(4)):alInfo(id)}"
assert OLD in s
NEW = r'''function alDown(){var t=+ls('o21.aldown')||0;return !!t&&Date.now()-t<6e5}
function jlDown(){var t=+ls('o21.jldown')||0;return !!t&&Date.now()-t<6e5}
function maSearch(q){
  if(ameta()==='mal'||alDown())return jlSearch(q).catch(function(e){if(ameta()==='mal'&&jlDown())throw e;ls('o21.jldown',Date.now());return alSearch(q)});
  return alSearch(q).catch(function(e){ls('o21.aldown',Date.now());return jlSearch(q)});
}
function maBrowse(kind){
  if(ameta()==='mal'||alDown())return jlBrowse(kind).catch(function(e){if(ameta()==='mal'&&jlDown())throw e;ls('o21.jldown',Date.now());return alBrowse(kind)});
  return alBrowse(kind).catch(function(e){ls('o21.aldown',Date.now());return jlBrowse(kind)});
}
function maInfo(id){
  if(id.indexOf('mal:')===0)return jlInfo(id.slice(4));
  return alInfo(id).catch(function(e){ls('o21.aldown',Date.now());throw e});
}'''
s = s.replace(OLD, NEW)

# 2. alMangaChars: degrade to empty instead of erroring the tab
OLD2 = "function alMangaChars(title){\n  return alPost("
assert OLD2 in s
i = s.find(OLD2)
j = s.find("/* home layout */", i)
assert j > 0
body = s[i:j]
assert body.rstrip().endswith('}')
s = s[:i] + body.rstrip()[:-1] + ").catch(function(){return []});\n}\n" + s[j:]

# 3. reader image chain: direct -> native vprox -> corsproxy
OLD3 = "      var prox=MPP[0]+encodeURIComponent(u);\n      return '<img src="'+esc(u)+'" loading="lazy" alt="" onerror="if(this.dataset.p!=='2'){this.dataset.p='2';this.src=''+prox+''}">';"
assert OLD3 in s, 'reader img line not found'
NEW3 = "      var prox=MPP[0]+encodeURIComponent(u);\n      var v2='';try{v2=VPROX_B+b64u(u)}catch(e){}\n      return '<img src="'+esc(u)+'" loading="lazy" alt="" onerror="if(!this.dataset.p&&this.dataset.v!=='1'){this.dataset.v='1';this.src=''+v2+''}else if(this.dataset.v==='1'){this.dataset.v='2';this.src=''+prox+''}">';"
s = s.replace(OLD3, NEW3)

# add b64u + VPROX_B helpers next to MPP definition
OLD4 = None
import re
m = re.search(r"var MPP=\[[^\]]*\];", s)
assert m, 'MPP def not found'
s = s.replace(m.group(0), m.group(0) + "\nvar VPROX_B='https://megaplay.buzz/__yrcineprox/';\nfunction b64u(x){return btoa(x).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')}")

# 4. banner
s = s.replace("console.log('[YRcine v26] rate-limit-proof AniList, caches, theme pages, light mode');",
              "console.log('[YRcine v27] AniList<->MAL auto-failover + Mangapill CDN image fix');")

out = '/scratch/work/v27-build.py'
open(out, 'w').write(s)
import py_compile
py_compile.compile(out, doraise=True)
print('v27-build.py written, python OK')
for feat in ['alDown()', 'o21.aldown', 'VPROX_B', 'b64u', 'readdetective']:
    print(('OK  ' if feat in s else 'MISS '), feat)
