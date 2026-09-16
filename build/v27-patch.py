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
s = s.replace(OLD , NEW)

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
OLD3 = "      var prox=MPP[0]+encodeURIComponent(u);\n      return '<img src=\"'+esc(u)+'\" loading=\"lazy\" alt=\"\" onerror=\"if(this.dataset.p!!==\\'2\\'){this.dataset.p=\\'2\\';this.src=\\''+prox+'\\'}\">';"
assert OLD3 in s, 'reader img line not found'
NEW = "      var prox=MPP[0]+encodeURIComponent(u);\n      var v2='';try{v2=VPROX_B+b64u(u)}catch(e){\n      return '<img src=\"'+esc(u)+'\" loading=\"lazy\" alt=\"\" onerror=\"if(!this.dataset.p&&this.dataset.v!==\\'1\\'){this.dataset.v=\\'1\\';this.src=\\''+v2+'\\'}else if(this.dataset.v===\\'1\\'){this.dataset.v=\\'2\\';this.src=\\''+prox+'\\'}\">';"
s = s.replace(OLD3, NEW3)

# add b64u + VPROX_B helpers next to MPP definition
OLD4 = None
import re
m = re.search(r"var MPP=\][^WIp×NÊ—NÈ‹ÊB˜\ÜÙ\K	ÓTYˆ›İ›İ[™	ÂœÈHËœ™\XÙJK™Ü›İ\

KK™Ü›İ\

H
È—˜\ˆ”“ÖĞIÚÎ‹ËÛYYØ\^K˜^‹××Ş\˜Ú[™\›ŞÉÎ×™[˜İ[ÛˆJ
^Ü™]\›ˆØJ
Kœ™\XÙJ×
ËÙË	ËIÊKœ™\XÙJ×ËÙË	×ÉÊKœ™\XÙJÏJÉË	ÉÊ_HŠB‚ˆÈˆ˜[›™\‚œÈHËœ™\XÙJ˜ÛÛœÛÛK›ÙÊ	ÖÖU&6–æRc#eÒ&FRÖÆ–Ö—B×&ööbæ”Æ—7BÂ66†W2ÂF†VÖRvW2ÂÆ–v‡BÖöFRr“²"À¢&6öç6öÆRæÆör‚uµ•&6–æRc#uÒæ”Æ—7CÂÓäÔÂWFòÖf–Æ÷fW"²Öæv–ÆÂ4Dâ–ÖvRf—‚r“²" ¦÷WBÒr÷67&F6‚÷v÷&²÷c#rÖ'V–ÆBç’p¦÷Vâ†÷WBÂwrr’çw&—FR‡2¦–×÷'B•ö6ö×–ÆP§•ö6ö×–ÆRæ6ö×–ÆR†÷WBÂF÷&—6SÕG'VR§&–çB‚wc#rÖ'V–ÆBç’w&—GFVâÂ—F†öâô²r¦f÷"fVB–â²vÄF÷vâ‚’rÂvó#æÆF÷vârÂue$õ…ô"rÂv#cGRrÂw&VFFWFV7F—fRuÓ ¢&–çB‚‚tô²r–bfVB–â2VÇ6RtÔ•52r’ÂfVB