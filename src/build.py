# Baut die GitHub-Pages-Version aus index.html (eine Quelldatei fuer beide Versionen).
import shutil, os, time
src=open('game.html').read()
head='''<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#ffcf1f">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Need For Pete">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-180.png">
<link rel="icon" href="icon-192.png">
<script>if(/[?&]modus=rennen(&|$)/.test(location.search)&&!window.NFP_RENNEN)location.replace('rennen.html'+location.search+location.hash);</script>
<style>[hidden]{display:none!important}:root{padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}</style>
<script src="peerjs.min.js"></script>
</head><body>
'''
tail='''
<script>if('serviceWorker' in navigator){let had=!!navigator.serviceWorker.controller,rl=false;
addEventListener('load',()=>navigator.serviceWorker.register('sw.js',{updateViaCache:'none'}).then(r=>{const up=()=>r.update().catch(()=>{});setInterval(up,120000);document.addEventListener('visibilitychange',()=>{if(!document.hidden)up();});}).catch(()=>{}));
navigator.serviceWorker.addEventListener('controllerchange',()=>{if(!had){had=true;return;}if(rl)return;rl=true;const go=()=>{const m=document.getElementById('menu');if(!m||!m.hidden)location.reload();else setTimeout(go,3000);};go();});}</script>
</body></html>'''
open('../index.html','w').write(head+src+tail)
# Blue-Chip-Pausen-Rennen: eigener Link, gleicher Spielcode, aber kein Speichern, kein Menü, kein Service-Worker-Update-Neuladen
rhead=head.replace('<script src="peerjs.min.js"></script>','<title>Blue Chip Pausen-Rennen</title><script>window.NFP_RENNEN=1;</script>')
rhead=rhead[:rhead.index("<script>if(/[?&]modus=rennen")]+rhead[rhead.index("<style>[hidden]"):]
assert rhead!=head
open('../rennen.html','w').write(rhead+src+'\n</body></html>')
ver=time.strftime('%Y%m%d%H%M%S')
sw=open('sw.template.js').read().replace('__VER__',ver)
open('../sw.js','w').write(sw)
print('built', ver)
