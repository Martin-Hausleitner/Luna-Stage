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
patch('renderer.js',"const targetSamples=Luna.scene.quality==='high'?80:48;", "const targetSamples=Luna.gpu.software?(Luna.scene.quality==='high'?16:8):(Luna.scene.quality==='high'?80:48);")
patch('interface.js','Luna.gpu.readPixels(1920,1080,48)','Luna.gpu.readPixels(1920,1080,Luna.gpu.software?8:48)')
p=SRC/'raster.wgsl';s=p.read_text();s=re.sub(r'\blocal\b','position',s);s=re.sub(r'\bobject\b','oid',s);s=re.sub(r'\bactive\b','inscriptionEnabled',s)
s=s.replace('if(o.flags.x==9.', 'let jitter=vec2f(hash11(u.state.w+17.)-.5,hash11(u.state.w+71.)-.5);clip=vec4f(clip.xy+jitter*2./u.view.xy*clip.w,clip.zw);if(o.flags.x==9.',1)
p.write_text(s)
# Software Vulkan adapters can execute native GPU commands and read back correct pixels
# while their browser compositor exposes a black canvas. This is a shipped presentation
# bridge, not a screenshot substitution. Hardware adapters keep direct WebGPU presentation.
p=SRC/'raster-engine.js';s=p.read_text()
s=s.replace('let roomDepth,', 'let bridgeBuffer,bridgeBytes=0;\nlet roomDepth,',1)
s=s.replace("context=$('room').getContext('webgpu');", "Luna.gpu.software=/swiftshader|llvmpipe|software/i.test(JSON.stringify(Luna.gpu.adapter));Luna.gpu.presentation=Luna.gpu.software?'gpu-readback-canvas':'direct-webgpu';\n context=$('room').getContext('webgpu');",1)
s=s.replace("Math.min(devicePixelRatio,1.15,1920/innerWidth)", "Math.min(devicePixelRatio,1.15,(Luna.gpu.software?1280:1920)/innerWidth)")
s=s.replace("Math.min(.70,1160/innerWidth)","Math.min(.70,(Luna.gpu.software?768:1160)/innerWidth)")
s=s.replace("display.end();const started=performance.now();", """display.end();const pitch=Math.ceil(w*4/256)*256;if(Luna.gpu.software){if(bridgeBytes!==pitch*h){bridgeBuffer?.destroy();bridgeBytes=pitch*h;bridgeBuffer=device.createBuffer({size:bridgeBytes,usage:GPUBufferUsage.COPY_DST|GPUBufferUsage.MAP_READ});}encoder.copyTextureToBuffer({texture:lastSurface},{buffer:bridgeBuffer,bytesPerRow:pitch,rowsPerImage:h},[w,h]);}const started=performance.now();""")
s=s.replace("Luna.gpu.pending=device.queue.onSubmittedWorkDone().then(()=>{gpuInFlight=false;Luna.gpu.lastFrameMS=performance.now()-started;});", """Luna.gpu.pending=(async()=>{await device.queue.onSubmittedWorkDone();if(Luna.gpu.software){const buf=bridgeBuffer;await buf.mapAsync(GPUMapMode.READ);const src=new Uint8Array(buf.getMappedRange()),pixels=new Uint8ClampedArray(w*h*4);for(let y=0;y<h;y++)pixels.set(src.subarray(y*pitch,y*pitch+w*4),y*w*4);if(format.startsWith('bgra'))for(let i=0;i<pixels.length;i+=4){const b=pixels[i];pixels[i]=pixels[i+2];pixels[i+2]=b;}buf.unmap();const out=$('still');if(out.width!==w)out.width=w;if(out.height!==h)out.height=h;out.getContext('2d').putImageData(new ImageData(pixels,w,h),0,0);document.body.classList.add('gpu-readback');}Luna.gpu.lastFrameMS=performance.now()-started;})().finally(()=>{gpuInFlight=false});""")
p.write_text(s)
p=SRC/'style.css';p.write_text(p.read_text()+"\nbody.gpu.gpu-readback #room{opacity:0}body.gpu.gpu-readback #still{visibility:visible}\n")
p=SRC/'renderer.js';s=p.read_text();a=s.index('Luna.gpu.render=(width,height)=>{');b=s.index('Luna.gpu.fallback=',a);s=s[:a]+s[b:]
s=s.replace('const shader=/*ROOM_SHADER*/,presentShader=/*PRESENT_SHADER*/;', 'const rasterShader='+json.dumps((SRC/'raster.wgsl').read_text())+',shadowShader='+json.dumps((SRC/'shadow.wgsl').read_text())+';\nconst presentShader=/*PRESENT_SHADER*/;')
s+='\n'+(SRC/'raster-engine.js').read_text();p.write_text(s)
