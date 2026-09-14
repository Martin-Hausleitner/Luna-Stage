"""Final visual and interaction corrections, applied to source and embedded shader."""
import json,re

def replace(name,old,new):
    p=SRC/name;s=p.read_text()
    if old not in s:raise ValueError('Finishing anchor missing: '+name+' '+old[:50])
    p.write_text(s.replace(old,new))

replace('interface.js','g.yaw=v*Math.PI/180;constrain(g);','const center=groupCenter(g);g.yaw=v*Math.PI/180;for(let i=0;i<3;i++)setCenter(g,i,center[i]);constrain(g);')
replace('input-boot.js','g.yaw=((g.yaw+Math.PI/12+Math.PI)%TAU)-Math.PI;constrain(g)','const center=groupCenter(g);g.yaw=((g.yaw+Math.PI/12+Math.PI)%TAU)-Math.PI;for(let i=0;i<3;i++)setCenter(g,i,center[i]);constrain(g)')
p=SRC/'raster.wgsl';s=p.read_text()
s=s.replace('c*=select(tex.rgb*1.38,pow(tex.rgb,vec3f(2.2)),o.surf.x==6.);','let timber=clamp(vec3f(.72)+(tex.rgb-vec3f(.72))*7.,vec3f(.24),vec3f(.99));let colour=select(tex.rgb,timber,o.surf.x==1.);c*=select(colour*1.38,pow(tex.rgb,vec3f(2.2)),o.surf.x==6.);')
s=s.replace('vec3f(.16,.19,.25)','vec3f(.23,.225,.215)')
s=s.replace('229.+f32(layer)*29.','96.+f32(layer)*13.').replace('rd.y*255.','rd.y*112.').replace('step(.73,hash11','step(.88,hash11')
s=s.replace('return col;}\nfn texUV', 'col=mix(col,mix(vec3f(.19,.23,.24),vec3f(.012,.022,.035),night),smoothstep(.10,.28,-rd.y));return col;}\nfn texUV',1)
p.write_text(s)
# Keep the audited shader source and the runtime's inline shader identical.
p=SRC/'renderer.js';lines=p.read_text().splitlines(keepends=True)
for i,line in enumerate(lines):
    if line.startswith('const rasterShader='):
        lines[i]='const rasterShader='+json.dumps((SRC/'raster.wgsl').read_text())+',shadowShader='+json.dumps((SRC/'shadow.wgsl').read_text())+';\n'
        break
else:raise ValueError('Inline raster shader header missing')
p.write_text(''.join(lines))
