#!/usr/bin/env python3
# v27: AniList->MAL auto-failover (CGNAT 400s) + Mangapill CDN image fix
# Generates v27-build.py from v26-build.py (same output as the original v27 patcher).
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
core = body.rstrip()
assert core.endswith('}')
core = core[:-1].rstrip()   # drop the function's closing brace
assert core.endswith(';')
core = core[:-1].rstrip()    # drop the trailing ';' of the .then(...) call
core = core + "\n    .catch(function(){return []});\n}\n"
s = s[:i] + core + s[j:]

# 3. reader image chain: direct -> native vprox -> corsproxy
ANCHOR = "      var prox=MPP[0]+encodeURIComponent(u);"
assert s.count(ANCHOR) == 1
i = s.find(ANCHOR)
j = s.find("\n", i) + 1
k = s.find("\n", j)
old_line = s[j:k]
assert old_line.startswith("      return '<img"), 'unexpected img line: ' + old_line[:60]
B = chr(92)  # backslash
NEW3 = (
    "      var v2='';try{v2=VPROX_B+b64u(u)}catch(e){}\n"
    "      return '<img src=\"" + "'+esc(u)+'" + "\" loading=\"lazy\" alt=\"\" onerror=\""
    "if(!this.dataset.p&&this.dataset.v!==" + B + "'1" + B + "'){this.dataset.v=" + B + "'1" + B + "';this.src=" + B + "'" + "'+v2+'" + B + "'}else if(this.dataset.v===" + B + "'1" + B + "'){this.dataset.v=" + B + "'2" + B + "';this.src=" + B + "'" + "'+prox+'" + B + "'}" + "\">';"
)
s = s[:j] + NEW3 + s[k:]

# add b64u + VPROX_B helpers next to MPP definition
import re
m = re.search(r"var MPP=\[[^\]]*\];", s)
assert m, 'MPP def not found'
s = s.replace(m.group(0), m.group(0) + "\nvar VPROX_B='https://megaplay.buzz/__yrcineprox/';\nfunction b64u(x){return btoa(x).replace(/" + B + "+/g,'-').replace(/" + B + "//g,'_').replace(/=+$/,'')}")


# 4. banner
s = s.replace("console.log('[YRcine v26] rate-limit-proof AniList, caches, theme pages, light mode');",
              "console.log('[YRcine v27] AniList<->MAL auto-failover + Mangapill CDN image fix');")

out = '/scratch/work/v27-build.py'
open(out, 'w').write(s)
import py_compile
py_compile.compile(out, doraise=True)
print('v27-build.py written, python OK')
