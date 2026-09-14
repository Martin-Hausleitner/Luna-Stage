"""Small reviewed patches applied after exact source-transfer verification."""
import re

def patch(name, old, new):
    p=SRC/name
    s=p.read_text()
    if old not in s:
        raise ValueError('Patch anchor missing: '+name+' '+old[:60])
    p.write_text(s.replace(old,new))

p=SRC/'room.wgsl'
p.write_text(re.sub(r'\bmeta\b','flags',p.read_text()))
# History must own its vectors and surface records, not alias the edited scene.
patch('state-camera.js','Luna.store.document=()=>({','Luna.store.document=()=>clone({')
# Canvas currentTexture must be copied in the same event-loop turn as rendering it.
patch('renderer.js','for(let i=0;i<n;i++){Luna.gpu.render(w,h);await Luna.gpu.pending;}const pitch=',
      'for(let i=0;i<n;i++){Luna.gpu.render(w,h);if(i<n-1)await Luna.gpu.pending;}const pitch=')
