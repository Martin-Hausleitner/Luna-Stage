"""Reviewed patches after exact source-transfer verification. No runtime dependencies."""
import hashlib,json,re

def patch(name,old,new):
    p=SRC/name;s=p.read_text()
    if old not in s:raise ValueError('Patch anchor missing: '+name+' '+old[:60])
    p.write_text(s.replace(old,new))

for name,digest in {'raster.wgsl':'fa4bbc09b6e74153abc5d10fde448d91bb32f9d7f1d56a58045a0c0e367bb9ee','shadow.wgsl':'83ff9462c9c0b5db994a15f6d537c9c60e1aec9cd0edf36824cbddc91d8957e6','raster-engine.js':'237a7bed7623bf90fd5838903ca0b0ca065413e769497b801e2130ae872b2758'}.items():
    if hashlib.sha256((SRC/name).read_bytes()).hexdigest()!=digest:raise ValueError('Source transfer mismatch: '+name)
patch('state-camera.js','Luna.store.document=()=>({','Luna.store.document=()=>clone({')
patch('state-camera.js',"if(!s.styles||", "if(typeof s.strip!=='boolean'||!['auto','high'].includes(s.quality)||![0,1].includes(s.material))throw Error('Ungültige Darstellungseinstellungen.');\nif(!s.styles||")
patch('renderer.js','for(let i=0;i<n;i++){Luna.gpu.render(w,h);await Luna.gpu.pending;}const pitch=',
      'for(let i=0;i<n;i++){Luna.gpu.render(w,h);if(i<n-1)await Luna.gpu.pending;}const pitch=')
patch('renderer.js',"ag.fillText('31 %',90,686)","ag.fillText('31 %',90,630)")
patch('renderer.js',"ag.fillText('Marge · intern',90,734)","ag.fillText('Marge · intern',90,687)")
p=SRC/'raster.wgsl';s=p.read_text();s=re.sub(r'\blocal\b','position',s);s=re.sub(r'\bobject\b','oid',s);s=re.sub(r'\bactive\b','inscriptionEnabled',s)
s=s.replace('if(o.flags.x==9.', 'let jitter=vec2f(hash11(u.state.w+17.)-.5,hash11(u.state.w+71.)-.5);clip=vec4f(clip.xy+jitter*2./u.view.xy*clip.w,clip.zw);if(o.flags.x==9.',1)
p.write_text(s)
p=SRC/'renderer.js';s=p.read_text();a=s.index('Luna.gpu.render=(width,height)=>{');b=s.index('Luna.gpu.fallback=',a);s=s[:a]+s[b:]
s=s.replace('const shader=/*ROOM_SHADER*/,presentShader=/*PRESENT_SHADER*/;', 'const rasterShader='+json.dumps((SRC/'raster.wgsl').read_text())+',shadowShader='+json.dumps((SRC/'shadow.wgsl').read_text())+';\nconst presentShader=/*PRESENT_SHADER*/;')
s+='\n'+(SRC/'raster-engine.js').read_text();p.write_text(s)
p=QA/'verify.py';s=p.read_text()
s=s.replace('import functools, hashlib, http.server, json, threading, time, traceback','import functools, hashlib, http.server, json, threading, time, traceback, shutil, os')
s=re.sub(r'^    browser=p\.chromium\.launch\(.*\)$','    from gpu_probe import select_browser\n    browser=p.chromium.launch(**select_browser(p,QA,url.rsplit("/",1)[0]))',s,flags=re.M)
s=s.replace('Luna.gpu.ready || document.body','Luna.gpu.firstGPUMS || document.body')
s=s.replace('settle(960,540,1)','settle(1920,1080,12)').replace("'native_resolution':[960,540],'samples':1", "'native_resolution':[1920,1080],'samples':12")
s=s.replace('PREVIEW ONLY; ONE SAMPLE','NATIVE PREVIEW; VISUAL REVIEW PENDING')
p.write_text(s)
