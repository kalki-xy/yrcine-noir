#!/usr/bin/env python3
# v28: movie section upgrade — replace 3 dead embed providers with 7 live ones
# (verified via Astralchemist/tmdb-embed-providers + vidsrc.cc official API docs)
import base64
src = '/workspace/notes/v27-build.py'
s = open(src).read()

OLD = """var SRVS=[
  {id:'vidsrc-to',label:'Vidsrc',desc:'Vidsrc.to embed'},
  {id:'vidsrc-xyz',label:'Vidsrc XYZ',desc:'vidsrc.xyz embed'},
  {id:'embed-su',label:'EmbedSU',desc:'embed.su embed'}
];
function embedUrl(srv,w){
  if(srv==='vidsrc-to')return w.type==='tv'?('https://vidsrc.to/embed/tv/'+w.id+'/'+w.season+'/'+w.episode):('https://vidsrc.to/embed/movie/'+w.id);
  if(srv==='vidsrc-xyz')return w.type==='tv'?('https://vidsrc.xyz/embed/tv?tmdb='+w.id+'&season='+w.season+'&episode='+w.episode):('https://vidsrc.xyz/embed/movie?tmdb='+w.id);
  return w.type==='tv'?('https://embed.su/embed/tv/'+w.id+'/'+w.season+'/'+w.episode):('https://embed.su/embed/movie/'+w.id);
}"""

NEW = """var SRVS=[
  {id:'videasy',label:'Videasy',desc:'Videasy player, up to 4K'},
  {id:'vidfast',label:'VidFast',desc:'vidfast.pro, autoplay'},
  {id:'vidlink',label:'VidLink',desc:'vidlink.pro'},
  {id:'vidsrc-pm',label:'vidsrc.pm',desc:'multi-language subtitles'},
  {id:'vidsrc-cc',label:'vidsrc.cc',desc:'v2 embed'},
  {id:'2embed',label:'2Embed',desc:'2embed.skin'},
  {id:'vidsrc-to',label:'Vidsrc',desc:'vidsrc.to embed'}
];
function embedUrl(srv,w){
  var t=w.type==='tv';
  if(srv==='videasy')return t?('https://player.videasy.net/tv/'+w.id+'/'+w.season+'/'+w.episode):('https://player.videasy.net/movie/'+w.id);
  if(srv==='vidfast')return t?('https://vidfast.pro/tv/'+w.id+'/'+w.season+'/'+w.episode+'?autoPlay=true'):('https://vidfast.pro/movie/'+w.id+'?autoPlay=true');
  if(srv==='vidlink')return t?('https://vidlink.pro/tv/'+w.id+'/'+w.season+'/'+w.episode):('https://vidlink.pro/movie/'+w.id);
  if(srv==='vidsrc-pm')return t?('https://vidsrc.pm/embed/tv/'+w.id+'/'+w.season+'/'+w.episode):('https://vidsrc.pm/embed/movie/'+w.id);
  if(srv==='vidsrc-cc')return t?('https://vidsrc.cc/v2/embed/tv/'+w.id+'/'+w.season+'/'+w.episode):('https://vidsrc.cc/v2/embed/movie/'+w.id);
  if(srv==='2embed')return t?('https://www.2embed.skin/embedtv/'+w.id+'&s='+w.season+'&e='+w.episode):('https://www.2embed.skin/embed/'+w.id);
  return t?('https://vidsrc.to/embed/tv/'+w.id+'/'+w.season+'/'+w.episode):('https://vidsrc.to/embed/movie/'+w.id);
}"""

# 0. version + banner
assert "CV.VERSION='27.0.0';" in s
s = s.replace("CV.VERSION='27.0.0';", "CV.VERSION='28.0.0';")
old_banner = "console.log('[YRcine v27] AniList<->MAL auto-failover + Mangapill CDN image fix');"
assert old_banner in s
s = s.replace(old_banner, "console.log('[YRcine v28] movies: 7 live embed sources (videasy/vidfast/vidlink/vidsrc.pm/vidsrc.cc/2embed/vidsrc.to)');")

# 1. movie sources swap — the SRVS block lives in the v20 SOURCE html, so the build
#    script needs an output-replace statement. Emit it with base64 to avoid quoting layers.
i = s.find('import re as _re26')
assert i > 0, 'escape-fix anchor missing'
b_old = base64.b64encode(OLD.encode()).decode()
b_new = base64.b64encode(NEW.encode()).decode()
ins = (
    'import base64 as _b64v28\n'
    "OLD_MOVIE = _b64v28.b64decode('" + b_old + "').decode()\n"
    "NEW_MOVIE = _b64v28.b64decode('" + b_new + "').decode()\n"
    "assert s.count(OLD_MOVIE) == 1, 'movie SRVS block not found in source'\n"
    's = s.replace(OLD_MOVIE, NEW_MOVIE)\n'
)
s = s[:i] + ins + s[i:]

out = '/scratch/work/v28-build.py'
open(out, 'w').write(s)
import py_compile
py_compile.compile(out, doraise=True)
print('v28-build.py written, python OK')
for feat in ['videasy', 'vidfast', 'vidlink.pro', 'vidsrc.pm', 'vidsrc.cc/v2', '2embed.skin', "CV.VERSION='28.0.0'"]:
    print(('OK  ' if feat in s else 'MISS '), feat)
assert 'embed.su' not in NEW and 'vidsrc.xyz' not in NEW
print('patcher done')
