#!/usr/bin/env python3
# v30: TMDB-native anime section — browse/detail/seasons/episodes via TMDB,
# sub/dub watch (Videasy sub / vidsrc.to ds_lang dub), TMDB characters+related
import base64
src = '/workspace/notes/v29-build.py'
html = '/workspace/outputs/01M2MRYF12F7VVW511M1NPQAA1/YRcine_Noir_VoidVerse-29.html'
s = open(src).read()
app = open(html, encoding='utf8').read()

def span(a, b, last=False):
    i = app.rfind(a) if last else app.find(a)
    assert i >= 0, 'start marker missing: ' + a[:50]
    j = app.find(b, i)
    assert j >= 0, 'end marker missing: ' + b[:50]
    return app[i:j]

# A. helpers + loadAnimeHome (TMDB discover/trending)
OLD_A = span("function loadAnimeHome(c){", "function tagHeroData(items){")
NEW_A = r"""function tKey21(){try{return String(localStorage.getItem('mv.tmdb.key')||'').trim()}catch(e){return ''}}
function tFetch21(path){
  var k=tKey21();
  if(!k)return Promise.reject(new Error('set your TMDB key in the Movies section first'));
  var ck='o21.tc.'+path;
  try{var c=JSON.parse(ls(ck)||'null');if(c&&Date.now()-c.t<9e5)return Promise.resolve(c.d)}catch(e){}
  return fjson('https://api.themoviedb.org/3'+path+(path.indexOf('?')>=0?'&':'?')+'api_key='+encodeURIComponent(k))
    .then(function(j){try{ls(ck,JSON.stringify({t:Date.now(),d:j}))}catch(e){}return j});
}
function tIsAnim(m){var g=m.genre_ids||[];return g.indexOf(16)>=0&&['ja','zh','ko'].indexOf(m.original_language)>=0}
function tCard(m){return {id:m.id,title:m.name||m.original_name||m.title||'?',cover:m.poster_path?('https://image.tmdb.org/t/p/w342'+m.poster_path):'',banner:m.backdrop_path?('https://image.tmdb.org/t/p/w780'+m.backdrop_path):'',year:(m.first_air_date||m.release_date||'').slice(0,4),score:Math.round((m.vote_average||0)*10)}}
function tPluck(r){return (r.results||[]).filter(tIsAnim).map(tCard)}
function loadAnimeHome(c){
  var lay=layout(false);
  var need={};lay.forEach(function(sx){need[sx[0]]=1});
  var dsc='with_genres=16&with_original_language=ja&include_null_first_air_dates=false&sort_by=popularity.desc';
  function t(k){
    if(k==='trending')return tFetch21('/trending/tv/week').then(tPluck).then(function(x){return x.slice(0,24)});
    if(k==='seasonal'){var d=new Date(Date.now()-40*864e5);var ds=d.toISOString().slice(0,10);var de=new Date().toISOString().slice(0,10);
      return tFetch21('/discover/tv?'+dsc+'&air_date.gte='+ds+'&air_date.lte='+de).then(tPluck);}
    if(k==='top')return tFetch21('/discover/tv?'+dsc.replace('sort_by=popularity.desc','sort_by=vote_average.desc')+'&vote_count.gte=400').then(tPluck);
    if(k==='random'){var p=1+Math.floor(Math.random()*15);return tFetch21('/discover/tv?'+dsc+'&page='+p).then(tPluck);}
    return tFetch21('/discover/tv?'+dsc).then(tPluck);
  }
  var kinds=['trending','seasonal','top','popular','random'];
  Promise.all(kinds.map(function(k){return need[k]?t(k).catch(function(){return null}):null}))
    .then(function(rs){
      if(CV.APP.route.page!=='otaku')return;
      var data={};kinds.forEach(function(k,i){if(rs[i]&&rs[i].length)data[k]=rs[i]});
      var trend=data.trending||data.popular||[];
      if(!Object.keys(data).length){c.innerHTML=emptyBox('TMDB anime feed unreachable \u2014 check your TMDB key (Movies \u2699) and connection.');return}
      var hh='';
      lay.forEach(function(sx){
        var id=sx[0];
        if(id==='hero'&&trend.length){hh+=heroHTML(trend.slice(0,4),'anime');tagHeroData(trend);}
        else if(id==='continue')hh+=contRow(false);
        else if(id==='favorites')hh+=favRow(false);
        else if(id==='trending'&&data.trending)hh+=sec('Trending Anime',data.trending.slice(0,20),'anime');
        else if(id==='seasonal'&&data.seasonal)hh+=sec('Airing Now',data.seasonal.slice(0,20),'anime');
        else if(id==='top'&&data.top)hh+=sec('Top Rated Anime',data.top.slice(0,20),'anime');
        else if(id==='popular'&&data.popular)hh+=sec('Popular Anime',data.popular.slice(0,20),'anime');
        else if(id==='random'&&data.random)hh+=sec('Random Picks',data.random.slice(0,20),'anime');
        else if(id==='latest'&&data.popular)hh+=sec('Popular Anime',data.popular.slice(0,20),'anime');
      });
      c.innerHTML=hh;startHero();
    });
}
"""

# B. doSearch (anime -> TMDB tv+movie)
OLD_B = span("function doSearch(c,q,isM){", "function emptyBox(msg){")
NEW_B = r"""function doSearch(c,q,isM){
  c.innerHTML='<div class="state-box" style="padding:24px"><div class="spinner"></div></div>';
  if(isM){
    mgSearch(q)
      .then(function(items){c.innerHTML=items.length?sec(srcLabel()+' Results',items,'manga'):emptyBox('No results for \u201C'+q+'\u201D')})
      .catch(function(e){c.innerHTML=emptyBox(srcLabel()+' search failed: '+e.message)});
  }else{
    if(!tKey21()){c.innerHTML=emptyBox('Set your TMDB key in the Movies section first');return}
    tFetch21('/search/tv?query='+encodeURIComponent(q)+'&include_adult=false').then(function(r1){
      var tv=tPluck(r1);
      return tFetch21('/search/movie?query='+encodeURIComponent(q)+'&include_adult=false').then(function(r2){
        if(CV.APP.route.page!=='otaku')return;
        var mv=(r2.results||[]).filter(tIsAnim).map(tCard);
        var h='';
        if(tv.length)h+=sec('Anime Series',tv.slice(0,24),'anime');
        if(mv.length)h+=sec('Anime Movies',mv.slice(0,24),'animem');
        c.innerHTML=h||emptyBox('No results for \u201C'+q+'\u201D on TMDB');
      });
    }).catch(function(e){c.innerHTML=emptyBox('TMDB search failed: '+e.message)});
  }
}
"""

# C. skDetail (TMDB tv, movie fallback)
OLD_C = span("function skDetail(el,id){", "var W21={lang:'sub'")
NEW_C = r"""function skDetail(el,id,mt){
  var isMv=mt==='animem';
  tFetch21((isMv?'/movie/':'/tv/')+id).catch(function(e){
    if(isMv)throw e;
    return tFetch21('/movie/'+id).then(function(m){m.__mv=1;return m});
  }).then(function(m){
    if(CV.APP.route.page!=='otaku-detail')return;
    var mv=isMv||m.__mv;
    var d={title:mv?(m.title||m.original_title):(m.name||m.original_name),cover:m.poster_path?('https://image.tmdb.org/t/p/w342'+m.poster_path):'',banner:m.backdrop_path?('https://image.tmdb.org/t/p/w780'+m.backdrop_path):'',desc:m.overview||'',year:(m.first_air_date||m.release_date||'').slice(0,4),episodes:mv?0:(m.number_of_episodes||0),score:Math.round((m.vote_average||0)*10),genres:(m.genres||[]).map(function(g){return g.name}),status:m.status||''};
    D21={id:id,type:'anime',mtype:mv?'movie':'tv',title:d.title,cover:d.cover,desc:d.desc,eps:mv?1:(m.number_of_episodes||0),src:'',matched:null,chs:[],tab:'chapters',seasons:mv?[]:((m.seasons||[]).filter(function(sn){return sn.episode_count>0})),sn:1};
    el.innerHTML=detailShell(d,'anime');
    renderTab();
  })
  .catch(function(e){el.innerHTML='<div class="otk-detail"><button class="mv-back" data-action="o21-back">\u2190 Back</button>'+emptyBox('TMDB error: '+e.message)+'</div>'});
}
"""

# D. renderWatch + playEp (seasons + SUB/DUB)
OLD_D = span("function renderWatch(el,params){", "var _hlsP21=null;", last=True)
NEW_D = r"""function renderWatch(el,params){
  var id=String(params.id||''),ep=String(params.ep||'1');
  if(!id){CV.Router.go('otaku');return}
  W21.ep=parseInt(ep,10)||1;
  W21.sn=parseInt(params.sn,10)||1;
  W21.k=String(params.k||'');
  W21.ctx={id:id,t:params.t?decodeURIComponent(params.t):'',c:params.c?decodeURIComponent(params.c):''};
  W21.list=[];
  var title=W21.ctx.t;
  el.innerHTML='<div class="otk-watch" style="grid-template-columns:1fr;max-width:1000px">'
    +'<div><button class="mv-back" data-action="o21-back">\u2190 Back</button>'
    +'<h2 class="mv-wtitle">'+esc(title||'Now Playing')+'</h2>'
    +'<div class="mv-wsub" id="v21WSub">S'+(W21.sn||1)+' \u00b7 Episode '+esc(ep)+'</div>'
    +'<div class="otk-player" id="v21Player" style="margin-bottom:12px"><div class="otk-player-overlay"><div class="spinner"></div><small style="color:var(--text-3)">Loading\u2026</small></div></div>'
    +'<div class="mv-srvrow">'
    +'<button class="mv-srv'+(W21.lang==='sub'?' on':'')+'" data-action="o21-lang" data-l="sub" title="Multi-language subtitles inside the player">SUB</button>'
    +'<button class="mv-srv'+(W21.lang==='dub'?' on':'')+'" data-action="o21-lang" data-l="dub" title="English dub via vidsrc.to">DUB</button>'
    +'<span style="border-left:1px solid var(--hairline);margin:0 2px;height:18px"></span>'
    +'<button class="mv-srv" data-action="o21-epnav" data-d="-1">\u2039 Prev</button>'
    +'<span id="v21EpN" style="font:700 12px var(--mono)">EP '+esc(ep)+'</span>'
    +'<button class="mv-srv" data-action="o21-epnav" data-d="1">Next \u203a</button>'
    +'<span style="border-left:1px solid var(--hairline);margin:0 2px;height:18px"></span>'
    +'<a class="mv-srv" style="text-decoration:none" id="v21Ext" target="_blank" rel="noopener">Open externally \u2197</a>'
    +'</div>'
    +'<div class="mv-note" style="margin-top:10px">SUB \u2192 Videasy (pick subtitle language in the player). DUB \u2192 English audio via vidsrc.to.</div>'
    +'</div></div>';
  playEp(el);
}
function v21TmdbKey(){return tKey21()}
function v21TmdbFind(a){
  var q=encodeURIComponent(a.t||''),k=tKey21();
  if(!q||!k)return Promise.reject(new Error('TMDB key not set'));
  var B='https://api.themoviedb.org/3/search/';
  function pick(r,isTv){
    var ja=(r.results||[]).filter(function(x){return x.original_language==='ja'});
    var list=ja.length?ja:(r.results||[]);
    if(!list.length)return null;
    return {id:list[0].id,type:isTv?'tv':'movie',name:isTv?(list[0].name||list[0].original_name):(list[0].title||list[0].original_title)};
  }
  return tFetch21('/search/tv?query='+q+'&include_adult=false').then(function(r1){var m=pick(r1,true);if(m)return m;
    return tFetch21('/search/movie?query='+q+'&include_adult=false').then(function(r2){return pick(r2,false)});
  });
}
function playEp(el){
  var box=document.getElementById('v21Player');
  var sub=document.getElementById('v21WSub');
  if(!box)return;
  var a=W21.ctx,m=null,ck=null;
  if(W21.k==='tmdb'||W21.k==='tmdbm'){m={id:a.id,type:W21.k==='tmdbm'?'movie':'tv',name:a.t}}
  else{ck='ot.vtmdb.'+a.id;try{var c=JSON.parse(ls('ot.vtmdb')||'{}');if(c[ck]&&Date.now()-(c[ck].t||0)<1209600000)m=c[ck]}catch(e){}}
  var go=function(m2){
    var url;
    if(m2.type==='tv'){
      url=W21.lang==='dub'
        ?('https://vidsrc.to/embed/tv/'+m2.id+'/'+(W21.sn||1)+'/'+(W21.ep||1)+'?ds_lang=eng')
        :('https://player.videasy.net/tv/'+m2.id+'/'+(W21.sn||1)+'/'+(W21.ep||1)+'?nextEpisode=true&autoplayNextEpisode=true&episodeSelector=true');
    }else{
      url=W21.lang==='dub'
        ?('https://vidsrc.to/embed/movie/'+m2.id+'?ds_lang=eng')
        :('https://player.videasy.net/movie/'+m2.id+'?nextEpisode=true&episodeSelector=true');
    }
    if(ck){try{var c2=JSON.parse(ls('ot.vtmdb')||'{}');c2[ck]={id:m2.id,type:m2.type,t:Date.now()};ls('ot.vtmdb',JSON.stringify(c2))}catch(e){}}
    if(sub)sub.textContent=(m2.type==='tv'?('S'+(W21.sn||1)+' \u00b7 '):'')+'Episode '+W21.ep+' \u00b7 '+(W21.lang==='dub'?'eng dub':'sub')+' \u00b7 '+(m2.name||a.t);
    box.innerHTML='<iframe src="'+url+'" style="position:absolute;inset:0;width:100%;height:100%;border:0" allow="autoplay; fullscreen; encrypted-media; picture-in-picture" allowfullscreen referrerpolicy="no-referrer"></iframe>';
    var ext=document.getElementById('v21Ext');if(ext)ext.href=url;
    saveCW(a.id,{id:a.id,title:a.t,cover:a.c,episode:String(W21.ep),progress:0,timestamp:Date.now()});
  };
  if(m){go(m);return}
  v21TmdbFind(a).then(function(m2){if(!m2)throw new Error('No TMDB match for this title');go(m2)})
  .catch(function(e){
    box.innerHTML='<div class="otk-player-overlay"><b>Couldn\u2019t load this episode</b><small>'+esc(e.message||'')+'</small><div style="display:flex;gap:8px;margin-top:8px"><button class="mv-srv" data-action="o21-epnav" data-d="0">Retry</button></div></div>';
  });
}
"""

# E. loadAnimeEpisodes (seasons)
OLD_E = span("function loadAnimeEpisodes(){", "/* settings page */")
NEW_E = r"""function loadAnimeEpisodes(){
  var box=document.getElementById('v21Eps');
  var lbl=document.getElementById('v21Match');
  if(!box)return;
  if(D21.mtype==='movie'){
    if(lbl)lbl.textContent='Anime film \u00b7 TMDB';
    box.innerHTML='<div class="v21-ep" data-action="o21-ep" data-id="'+esc(D21.id)+'" data-k="tmdbm" data-ep="1" data-sn="1" data-t="'+esc(D21.title)+'" data-c="'+esc(D21.cover)+'" data-num="1">'
      +'<span class="v21-ep-n">\u25b6</span>'
      +'<span class="v21-ep-t">Watch movie</span>'
      +'<span class="v21-ep-m">videasy</span></div>';
    return;
  }
  var sns=D21.seasons||[];
  var h='';
  if(sns.length>1){
    h+='<div class="v21-provrow" style="justify-content:flex-start;margin-bottom:8px">';
    sns.forEach(function(sn){h+='<button class="v21-prov'+((D21.sn||1)===sn.season_number?' on':'')+'" data-action="o21-sn" data-sn="'+sn.season_number+'" title="'+esc(sn.name||'')+'">'+esc(((sn.name||'').length<16)?(sn.name||('S'+sn.season_number)):('S'+sn.season_number))+'</button>';});
    h+='</div>';
  }
  h+='<div id="v21EpList"><div class="state-box" style="padding:24px"><div class="spinner"></div></div></div>';
  if(lbl)lbl.textContent=(sns.length>1?(sns.length+' seasons \u00b7 '):'')+'TMDB \u00b7 Videasy';
  box.innerHTML=h;
  var sn=D21.sn||1;
  tFetch21('/tv/'+D21.id+'/season/'+sn).then(function(r){
    if(CV.APP.route.page!=='otaku-detail')return;
    var eps=r.episodes||[];
    D21.eps=eps.length;
    var el2=document.getElementById('v21EpList');
    if(!el2)return;
    el2.innerHTML=eps.map(function(e){
      return '<div class="v21-ep" data-action="o21-ep" data-id="'+esc(D21.id)+'" data-k="tmdb" data-ep="'+e.episode_number+'" data-sn="'+sn+'" data-t="'+esc(D21.title)+'" data-c="'+esc(D21.cover)+'" data-num="'+e.episode_number+'">'
        +'<span class="v21-ep-n">EP '+e.episode_number+'</span>'
        +'<span class="v21-ep-t">'+esc(e.name||'')+(e.air_date?(' \u00b7 '+e.air_date):'')+'</span>'
        +'<span class="v21-ep-m">videasy</span></div>';
    }).join('')||emptyBox('No episodes listed on TMDB');
  }).catch(function(e){
    var el3=document.getElementById('v21EpList');
    if(el3)el3.innerHTML=emptyBox('TMDB season load failed: '+e.message);
  });
}
"""

# F. renderDetail (pass animem type through)
OLD_F = span("function renderDetail(el,params){", "function mdDetail(el,id){", last=True)
NEW_F = r"""function renderDetail(el,params){
  var id=String(params.id||''),type=params.type==='manga'?'manga':(params.type==='animem'?'animem':'anime');
  if(!id){CV.Router.go('otaku');return}
  el.innerHTML='<div class="otk-detail"><button class="mv-back" data-action="o21-back">\u2190 Back</button><div style="padding:24px 0"><div class="state-box"><div class="spinner"></div></div></div></div>';
  if(type==='manga')mdDetail(el,id);else skDetail(el,id,type);
}
"""

# G. characters + related tab branches (TMDB for anime)
OLD_G = span("}else if(t==='characters'){", "bindChSearch();")
NEW_G = r"""}else if(t==='characters'){
    el.innerHTML='<div class="state-box" style="padding:24px"><div class="spinner"></div></div>';
    var P=(D21.type==='manga')?alMangaChars(D21.title):tFetch21('/tv/'+D21.id+'/aggregate_credits').then(function(cr){
      return {chars:((cr&&cr.cast)||[]).slice(0,40).map(function(x){return {name:x.name,image:(x.profile_path?('https://image.tmdb.org/t/p/w185'+x.profile_path):'')}})};
    });
    P.then(function(d){
      if(CV.APP.route.page!=='otaku-detail')return;
      var box=document.getElementById('v21TabBody');
      if(box)box.innerHTML=charsGrid(d.chars||[]);
    }).catch(function(e){
      var box=document.getElementById('v21TabBody');
      if(box)box.innerHTML=emptyBox('Characters unavailable: '+e.message);
    });
  }else{
    el.innerHTML='<div class="state-box" style="padding:24px"><div class="spinner"></div></div>';
    var P2=(D21.type==='manga')?alInfo(D21.id):tFetch21('/tv/'+D21.id+'/recommendations').then(function(rc){
      return {rels:((rc&&rc.results)||[]).filter(tIsAnim).slice(0,12).map(tCard)};
    });
    P2.then(function(d){
      if(CV.APP.route.page!=='otaku-detail')return;
      var box=document.getElementById('v21TabBody');
      if(box)box.innerHTML=relsGrid(d.rels||[],'anime');
    }).catch(function(e){
      var box=document.getElementById('v21TabBody');
      if(box)box.innerHTML=emptyBox('Related titles unavailable: '+e.message);
    });
  }
"""

# H. o21-ep dispatcher (season pass) + o21-sn
OLD_H = span("else if(a==='o21-ep'){", "else if(a==='o21-lang'){")
NEW_H = r"""else if(a==='o21-ep'){
    var ep=t.getAttribute('data-ep');
    var id2=t.getAttribute('data-id');
    var k2=t.getAttribute('data-k')||'';
    var sn2=t.getAttribute('data-sn')||'1';
    CV.Router.go('otaku-watch?id='+encodeURIComponent(id2)+'&ep='+encodeURIComponent(ep)+'&sn='+encodeURIComponent(sn2)+'&k='+encodeURIComponent(k2)+'&t='+encodeURIComponent(t.getAttribute('data-t')||'')+'&c='+encodeURIComponent(t.getAttribute('data-c')||''));
    W21.ep=parseInt(ep,10)||1;W21.sn=parseInt(sn2,10)||1;
  }
  else if(a==='o21-sn'){
    D21.sn=parseInt(t.getAttribute('data-sn'),10)||1;
    var pgS=document.getElementById('page-otaku-detail');
    if(pgS)pgS.querySelectorAll('[data-action="o21-sn"]').forEach(function(b){b.classList.toggle('on',parseInt(b.getAttribute('data-sn'),10)===D21.sn)});
    loadAnimeEpisodes();
  }
"""

# 0. version + banner
assert "CV.VERSION='29.0.0';" in s
s = s.replace("CV.VERSION='29.0.0';", "CV.VERSION='30.0.0';")
old_banner = "console.log('[YRcine v29] anime playback via Videasy/TMDB; local episode lists');"
assert old_banner in s
s = s.replace(old_banner, "console.log('[YRcine v30] TMDB-native anime: browse/seasons/episodes/characters + sub-dub watch');")

# emit build statements (base64) AFTER the v29 replaces, BEFORE the final write
anchor = "open(DST, 'w').write(s)"
assert s.count(anchor) == 1
def blk(old, new, tag):
    bo = base64.b64encode(old.encode()).decode()
    bn = base64.b64encode(new.encode()).decode()
    return ("import base64 as _b64v30\n"
            "_O = _b64v30.b64decode('" + bo + "').decode()\n"
            "_N = _b64v30.b64decode('" + bn + "').decode()\n"
            "assert s.count(_O) == 1, '" + tag + " span not unique'\n"
            "s = s.replace(_O, _N)\n")
ins = (blk(OLD_A, NEW_A, 'home') + blk(OLD_B, NEW_B, 'search') + blk(OLD_C, NEW_C, 'detail')
       + blk(OLD_D, NEW_D, 'watch') + blk(OLD_E, NEW_E, 'eplist') + blk(OLD_F, NEW_F, 'renderdetail')
       + blk(OLD_G, NEW_G, 'tabs') + blk(OLD_H, NEW_H, 'dispatcher'))
s = s.replace(anchor, ins + '\n' + anchor)

out = '/scratch/work/v30-build.py'
open(out, 'w').write(s)
import py_compile
py_compile.compile(out, doraise=True)
print('v30-build.py written, python OK')
