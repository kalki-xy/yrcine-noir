#!/usr/bin/env python3
# v29: anime playback via Videasy (TMDB) — replaces megaplay/anikoto stream chain
import base64
src = '/workspace/notes/v28-build.py'
html = '/workspace/outputs/01M2MPMCFN47CW997EDAVS7Y0Q/YRcine_Noir_VoidVerse-28.html'
s = open(src).read()
app = open(html, encoding='utf8').read()

def span(a, b):
    i = app.find(a)
    assert i >= 0, 'start marker missing: ' + a[:40]
    j = app.find(b, i)
    assert j >= 0, 'end marker missing: ' + b[:40]
    return app[i:j]

# ── A. anime watch: replace W21 renderWatch + playEp (stream resolution) ──
OLD_A = span("function renderWatch(el,params){\n  var id=String(params.id||''),ep=String(params.ep||'1');", "var _hlsP21=null;")
assert OLD_A.count('OTK') == 0
NEW_A = r"""function renderWatch(el,params){
  var id=String(params.id||''),ep=String(params.ep||'1');
  if(!id){CV.Router.go('otaku');return}
  W21.ep=parseInt(ep,10)||1;
  W21.k=String(params.k||'');
  W21.ctx={id:id,t:params.t?decodeURIComponent(params.t):'',c:params.c?decodeURIComponent(params.c):''};
  W21.list=[];
  var title=W21.ctx.t;
  el.innerHTML='<div class="otk-watch" style="grid-template-columns:1fr;max-width:1000px">'
    +'<div><button class="mv-back" data-action="o21-back">\u2190 Back</button>'
    +'<h2 class="mv-wtitle">'+esc(title||'Now Playing')+'</h2>'
    +'<div class="mv-wsub" id="v21WSub">Episode '+esc(ep)+' \u00b7 Videasy</div>'
    +'<div class="otk-player" id="v21Player" style="margin-bottom:12px"><div class="otk-player-overlay"><div class="spinner"></div><small style="color:var(--text-3)">Finding on TMDB\u2026</small></div></div>'
    +'<div class="mv-srvrow">'
    +'<button class="mv-srv" data-action="o21-epnav" data-d="-1">\u2039 Prev</button>'
    +'<span id="v21EpN" style="font:700 12px var(--mono)">EP '+esc(ep)+'</span>'
    +'<button class="mv-srv" data-action="o21-epnav" data-d="1">Next \u203a</button>'
    +'<span style="border-left:1px solid var(--hairline);margin:0 2px;height:18px"></span>'
    +'<a class="mv-srv" style="text-decoration:none" id="v21Ext" target="_blank" rel="noopener">Open externally \u2197</a>'
    +'</div>'
    +'<div class="mv-note" style="margin-top:10px">Streams via Videasy (TMDB) \u2014 multi-language subtitles are inside the player.</div>'
    +'</div></div>';
  playEp(el);
}
function v21TmdbKey(){
  var k='';
  try{k=String(localStorage.getItem('mv.tmdb.key')||'').trim()}catch(e){}
  return k;
}
function v21TmdbFind(a){
  var q=encodeURIComponent(a.t||''),k=v21TmdbKey();
  if(!q||!k)return Promise.reject(new Error('TMDB key not set'));
  var B='https://api.themoviedb.org/3/search/';
  function pick(r,isTv){
    var ja=(r.results||[]).filter(function(x){return x.original_language==='ja'});
    var list=ja.length?ja:(r.results||[]);
    if(!list.length)return null;
    return {id:list[0].id,type:isTv?'tv':'movie',name:isTv?(list[0].name||list[0].original_name):(list[0].title||list[0].original_title)};
  }
  return fetch(B+'tv?api_key='+encodeURIComponent(k)+'&query='+q+'&language=en-US').then(function(r){return r.json()})
    .then(function(r1){var m=pick(r1,true);if(m)return m;
      return fetch(B+'movie?api_key='+encodeURIComponent(k)+'&query='+q+'&language=en-US').then(function(r){return r.json()})
        .then(function(r2){return pick(r2,false)});
    });
}
function playEp(el){
  var box=document.getElementById('v21Player');
  var sub=document.getElementById('v21WSub');
  if(!box)return;
  var a=W21.ctx;
  var m=null,ck='x';
  try{ck='ot.vtmdb.'+a.id;var c=JSON.parse(ls('ot.vtmdb')||'{}');if(c[ck]&&Date.now()-(c[ck].t||0)<1209600000)m=c[ck]}catch(e){}
  var go=function(m2){
    var url=m2.type==='tv'?('https://player.videasy.net/tv/'+m2.id+'/1/'+(W21.ep||1)):('https://player.videasy.net/movie/'+m2.id);
    try{var c2=JSON.parse(ls('ot.vtmdb')||'{}');c2[ck]={id:m2.id,type:m2.type,t:Date.now()};ls('ot.vtmdb',JSON.stringify(c2))}catch(e){}
    if(sub)sub.textContent='Episode '+W21.ep+' \u00b7 '+(m2.name||a.t);
    box.innerHTML='<iframe src="'+url+'" style="position:absolute;inset:0;width:100%;height:100%;border:0" allow="autoplay; fullscreen; encrypted-media; picture-in-picture" allowfullscreen referrerpolicy="no-referrer"></iframe>';
    var ext=document.getElementById('v21Ext');if(ext)ext.href=url;
    saveCW(a.id,{id:a.id,title:a.t,cover:a.c,episode:String(W21.ep),progress:0,timestamp:Date.now()});
  };
  if(m){go(m);return}
  v21TmdbFind(a).then(function(m2){if(!m2)throw new Error('No TMDB match for this title');go(m2)})
  .catch(function(e){
    box.innerHTML='<div class="otk-player-overlay"><b>Couldn\u2019t play this on Videasy</b><small>'+esc(e.message||'')+'</small><div style="display:flex;gap:8px;margin-top:8px"><button class="mv-srv" data-action="o21-epnav" data-d="0">Retry</button></div></div>';
  });
}
"""
# ls() helper must exist in that scope
assert 'function ls(' in app

# ── B. anime episode list: local (from AniList/MAL count), no AniKoto ──
OLD_B = span("function loadAnimeEpisodes(){", "/* settings page */")
NEW_B = r"""function loadAnimeEpisodes(){
  var box=document.getElementById('v21Eps');
  var lbl=document.getElementById('v21Match');
  if(!box)return;
  var n=parseInt(D21.eps,10)||0;
  if(!n)n=24;
  if(lbl)lbl.textContent=n+' episodes \u00b7 Videasy';
  var h='';
  for(var i=1;i<=n;i++){
    h+='<div class="v21-ep" data-action="o21-ep" data-id="'+esc(D21.id)+'" data-k="'+esc(D21.k||'')+'" data-ep="'+i+'" data-t="'+esc(D21.title)+'" data-c="'+esc(D21.cover)+'" data-num="'+i+'">'
      +'<span class="v21-ep-n">EP '+i+'</span>'
      +'<span class="v21-ep-t"></span>'
      +'<span class="v21-ep-m">videasy</span></div>';
  }
  D21.chs=[];
  box.innerHTML=h;
}
"""

# ── C. skDetail: keep episode count on D21 ──
OLD_C = "D21={id:id,type:'anime',title:d.title,cover:d.cover,desc:d.desc,src:'',matched:null,chs:[],tab:'chapters'};"
assert app.count(OLD_C) == 1
NEW_C = "D21={id:id,type:'anime',title:d.title,cover:d.cover,desc:d.desc,eps:(d.episodes||d.eps||0),src:'',matched:null,chs:[],tab:'chapters'};"

# ── 0. version + banner ──
assert "CV.VERSION='28.0.0';" in s
s = s.replace("CV.VERSION='28.0.0';", "CV.VERSION='29.0.0';")
old_banner = "console.log('[YRcine v28] movies: 7 live embed sources (videasy/vidfast/vidlink/vidsrc.pm/vidsrc.cc/2embed/vidsrc.to)');"
assert old_banner in s
s = s.replace(old_banner, "console.log('[YRcine v29] anime playback via Videasy/TMDB; local episode lists');")

# ── emit build statements (base64, inserted just before the final write) ──
anchor = "s = s.replace('</body>', BLOCK, 1)"
assert s.count(anchor) == 1
def blk(old, new, tag):
    bo = base64.b64encode(old.encode()).decode()
    bn = base64.b64encode(new.encode()).decode()
    return ("import base64 as _b64v29\n"
            "_O = _b64v29.b64decode('" + bo + "').decode()\n"
            "_N = _b64v29.b64decode('" + bn + "').decode()\n"
            "assert s.count(_O) == 1, '" + tag + " span not unique'\n"
            "s = s.replace(_O, _N)\n")
ins = blk(OLD_A, NEW_A, 'watch') + blk(OLD_B, NEW_B, 'eplist') + blk(OLD_C, NEW_C, 'skdetail')
s = s.replace(anchor, anchor + '\n' + ins)

out = '/scratch/work/v29-build.py'
open(out, 'w').write(s)
import py_compile
py_compile.compile(out, doraise=True)
print('v29-build.py written, python OK')
