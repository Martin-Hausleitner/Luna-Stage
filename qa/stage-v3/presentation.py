"""Present actual WebGPU pixels on software adapters with incomplete canvas compositing."""
from pathlib import Path
root=Path(__file__).resolve().parents[2];p=root/'Luna-Stage.html';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a[:90]
 s=s.replace(a,b,1)
rep('</style>', 'body.softgpu #still{visibility:visible}body.softgpu #room{opacity:0!important;pointer-events:none}</style>')
rep('let framePending=false;', 'let softSurface=null,softSize="";let framePending=false;')
rep('Luna.gpu.adapter={vendor:',"Luna.gpu.software=/swiftshader|llvmpipe|software/i.test([adapter.info?.vendor,adapter.info?.architecture,adapter.info?.description].join(' '));Luna.gpu.presentation=Luna.gpu.software?'WebGPU pixels / software-adapter readback':'WebGPU canvas';Luna.gpu.adapter={vendor:")
rep("document.body.classList.add('gpu');", "document.body.classList.toggle('softgpu',Luna.gpu.software);document.body.classList.add('gpu');")
rep('lastSurface=context.getCurrentTexture();', '''if(Luna.gpu.software){if(softSize!==w+'x'+h){if(softSurface)softSurface.destroy();softSurface=device.createTexture({size:[w,h],format,usage:GPUTextureUsage.RENDER_ATTACHMENT|GPUTextureUsage.COPY_SRC});softSize=w+'x'+h;}lastSurface=softSurface;}else lastSurface=context.getCurrentTexture();''')
a='display.end();device.queue.submit([enc.finish()]);framePending=true;device.queue.onSubmittedWorkDone().then(()=>{framePending=false});sampleCount++;'
b=r'''display.end();
let screenBuffer=null,pitch=0;
if(Luna.gpu.software){pitch=Math.ceil(w*4/256)*256;screenBuffer=device.createBuffer({size:pitch*h,usage:GPUBufferUsage.COPY_DST|GPUBufferUsage.MAP_READ});enc.copyTextureToBuffer({texture:lastSurface},{buffer:screenBuffer,bytesPerRow:pitch,rowsPerImage:h},[w,h]);}
device.queue.submit([enc.finish()]);framePending=true;
Luna.gpu.presentationPending=(async()=>{
 try{
  if(screenBuffer){await screenBuffer.mapAsync(GPUMapMode.READ);const src=new Uint8Array(screenBuffer.getMappedRange()),rgba=new Uint8ClampedArray(w*h*4);for(let y=0;y<h;y++)rgba.set(src.subarray(y*pitch,y*pitch+w*4),y*w*4);if(format.startsWith('bgra'))for(let i=0;i<rgba.length;i+=4){const a=rgba[i];rgba[i]=rgba[i+2];rgba[i+2]=a;}screenBuffer.unmap();screenBuffer.destroy();const screen=$('still');if(screen.width!==w)screen.width=w;if(screen.height!==h)screen.height=h;screen.getContext('2d').putImageData(new ImageData(rgba,w,h),0,0);}
  else await device.queue.onSubmittedWorkDone();
 }finally{framePending=false;}
})();sampleCount++;'''
rep(a,b)
rep('Luna.gpu.wait=async()=>{if(device)await device.queue.onSubmittedWorkDone()}', 'Luna.gpu.wait=async()=>{if(device)await device.queue.onSubmittedWorkDone();if(Luna.gpu.presentationPending)await Luna.gpu.presentationPending}')
rep('Luna.gpu.firstGPUMS=performance.now();', 'if(Luna.gpu.presentationPending)await Luna.gpu.presentationPending;Luna.gpu.firstGPUMS=performance.now();')
rep('const ratio=Math.min(moving?.72:Math.min(devicePixelRatio,1.25),(moving?1440:1920)/innerWidth);', 'const ratio=Luna.gpu.software?Math.min(moving?.48:1,(moving?640:960)/innerWidth):Math.min(moving?.72:Math.min(devicePixelRatio,1.25),(moving?1440:1920)/innerWidth);')
a='function tick(now){raf=0;let dt=lastFrame?Math.min((now-lastFrame)/1000,1.0):0;lastFrame=now;if(document.hidden)return;if(Luna.gpu.snapshotBusy||framePending){raf=requestAnimationFrame(tick);return}'
b='function tick(now){raf=0;if(document.hidden)return;if(Luna.gpu.snapshotBusy||framePending){raf=requestAnimationFrame(tick);return}let dt=lastFrame?Math.max(0,(now-lastFrame)/1000):0;lastFrame=now;'
rep(a,b)
rep('Luna.cam.toggle=()=>{if(Luna.cam.time','Luna.cam.toggle=()=>{lastFrame=performance.now();if(Luna.cam.time')
rep('Luna.cam.playShot=(id,play=true)=>{','Luna.cam.playShot=(id,play=true)=>{lastFrame=performance.now();')
rep('Luna.cam.toggle=()=>{if(Luna.cam.activeShot','Luna.cam.toggle=()=>{lastFrame=performance.now();if(Luna.cam.activeShot')
rep('Luna.gpu.snapshotBusy=false;Luna.hud.sync();Luna.gpu.invalidate()', 'Luna.gpu.snapshotBusy=false;lastFrame=performance.now();Luna.hud.sync();Luna.gpu.invalidate()')
p.write_text(s);print('Native pixel presentation and camera clock fixed')
