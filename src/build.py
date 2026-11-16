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
<style>[hidden]{display:none!important}:root{padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}</style>
<script src="peerjs.min.js"></script>
</head><body>
'''
tail='''
<script>if('serviceWorker' in navigator)addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}));</script>
</body></html>'''
open('../index.html','w').write(head+src+tail)
ver=time.strftime('%Y%m%d%H%M%S')
sw=open('sw.template.js').read().replace('__VER__',ver)
open('../sw.js','w').write(sw)
print('built', ver)
