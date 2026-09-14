"""Reviewed compatibility and correctness patches after verified source transfer."""
import re

def patch(name, old, new):
    p=SRC/name
    s=p.read_text()
    if old not in s:
        raise ValueError('Patch anchor missing: '+name+' '+old[:60])
    p.write_text(s.replace(old,new))

p=SRC/'room.wgsl'
p.write_text(re.sub(r'\bmeta\b','flags',p.read_text()))
patch('room.wgsl','for(var j=0;j<u32(u.counts.x);j++)','for(var j=0u;j<u32(u.counts.x);j++)')
patch('state-camera.js','Luna.store.document=()=>({','Luna.store.document=()=>clone({')
patch('renderer.js','for(let i=0;i<n;i++){Luna.gpu.render(w,h);await Luna.gpu.pending;}const pitch=',
      'for(let i=0;i<n;i++){Luna.gpu.render(w,h);if(i<n-1)await Luna.gpu.pending;}const pitch=')
patch('renderer.js','Luna.gpu.init=async()=>{','Luna.gpu.init=async()=>{await new Promise(resolve=>requestAnimationFrame(()=>setTimeout(resolve,0)));')
patch('geometry-gpu.js','n.right=build(list.slice(mid))}return index}',
      'n.right=build(list.slice(mid))}n.escape=nodes.length;return index}')
patch('geometry-gpu.js','...n.lo,n.count?n.start:n.left,...n.hi,n.count||(-n.right-1)',
      '...n.lo,n.count?n.start:n.escape,...n.hi,n.count')
p=SRC/'room.wgsl';s=p.read_text()
a=s.index('fn trace(');b=s.index('fn sky(',a)
s=s[:a]+'''fn trace(ro:vec3f,rd:vec3f,limit:f32,anyHit:bool)->Hit{
var hit=Hit(limit,-1,vec3f(0));var ix=0u;
for(var step=0u;step<u32(u.counts.w);step++){
if(ix>=u32(u.counts.w)){break;}let node=nodes[ix];
if(aabb(ro,rd,node.lo.xyz,node.hi.xyz)>=hit.t){
if(node.hi.w>0.){ix++;}else{ix=u32(node.lo.w);}continue;}
if(node.hi.w>0.){let start=u32(node.lo.w);let end=start+u32(node.hi.w);
for(var i=start;i<end;i++){let o=objects[i];if(o.flags.x==9.&&u.eye.y>3.24){continue;}
let h=intersect(ro,rd,o);if(h.x<hit.t){hit=Hit(h.x,i32(i),h.yzw);if(anyHit){return hit;}}}}
ix++;}
return hit;}
''' + s[b:];p.write_text(s)
p=QA/'verify.py';s=p.read_text()
s=s.replace('import functools, hashlib, http.server, json, threading, time, traceback','import functools, hashlib, http.server, json, threading, time, traceback, shutil, os')
s=s.replace("with sync_playwright() as p:","os.environ['DEBUG']='pw:browser'\nwith sync_playwright() as p:")
s=s.replace("p.chromium.launch(headless=True,args=", "p.chromium.launch(headless=True,executable_path=shutil.which('google-chrome') or None,args=")
s=s.replace("'--use-angle=swiftshader','--enable-features=Vulkan','--disable-vulkan-surface'", "'--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'")
s=s.replace("'--disable-dev-shm-usage']", "'--disable-dev-shm-usage','--disable-gpu-watchdog']")
s=s.replace("Luna.gpu.ready || document.body", "Luna.gpu.firstGPUMS || document.body")
p.write_text(s)
