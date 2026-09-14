"""Bake six honest fallback stills from this application's actual native WebGPU room.
Development-only. Source contains the resulting inline WebP images, no runtime assets.
Run only when the scene changes. Pillow and Playwright are QA/build tools, not app dependencies.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import functools,threading,json,re,hashlib
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent.parent;path=root/'Luna-Stage.html';source=path.read_text()
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(SimpleHTTPRequestHandler,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start()
frames=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args=['--enable-unsafe-webgpu'])
 page=b.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1);page.goto(f'http://127.0.0.1:{server.server_port}/Luna-Stage.html?paused=1');page.wait_for_function('Luna.gpu.ready',timeout=120000)
 for i in range(6):
  image=page.evaluate('''async i=>{Luna.gpu.snapshotBusy=true;Luna.cam.goto(i,false);Luna.scene.price=false;Luna.scene.ceo=false;const data=await Luna.gpu.readPixels(1280,720);const canvas=document.createElement('canvas');canvas.width=1280;canvas.height=720;canvas.getContext('2d').putImageData(data,0,0);Luna.gpu.snapshotBusy=false;return canvas.toDataURL('image/webp',.72)}''',i)
  assert image.startswith('data:image/webp;base64,');frames.append(image);print('baked',i+1,len(image),flush=True)
 b.close()
server.shutdown()
block='/* BAKED-STILLS-BEGIN */\nconst embeddedStills='+json.dumps(frames,separators=(',',':'))+';\nconst stillImages=embeddedStills.map((src,i)=>{const image=new Image();image.onload=()=>{Luna.gpu.drawStill($("filmstrip").children[i].querySelector("canvas"),i,true);if(!Luna.gpu.ready){Luna.gpu.drawStill($("still"));Luna.hud.draw();Luna.gpu.bakedStillMS=performance.now()}};image.src=src;return image;});\n/* BAKED-STILLS-END */\n'
if '/* BAKED-STILLS-BEGIN */' in source:source=re.sub(r'/\* BAKED-STILLS-BEGIN \*/.*?/\* BAKED-STILLS-END \*/\n',lambda _:block,source,flags=re.S)
else:
 source=source.replace('let woodPattern=null;',block+'let woodPattern=null;')
 needle='const g=canvas.getContext(\'2d\'),w=canvas.width,h=canvas.height,old='
 replacement='const frame=stillImages[chapter];if(frame?.complete&&frame.naturalWidth){const g=canvas.getContext(\'2d\'),w=canvas.width,h=canvas.height;g.drawImage(frame,0,0,w,h);return}const g=canvas.getContext(\'2d\'),w=canvas.width,h=canvas.height,old='
 assert needle in source;source=source.replace(needle,replacement)
 source=source.replace('Luna.scene.cycle=()=>{Luna.cam.playing=false;',"Luna.scene.cycle=()=>{if(!Luna.gpu.ready){Luna.cam.goto(Luna.scene.material?2:3,false);return}Luna.cam.playing=false;")
 source=source.replace('g.save();g.globalAlpha=.67;g.transform','g.save();g.globalAlpha=.68;g.filter=\'brightness(.16)\';g.transform')
 source=source.replace('#brand{font-size:10px;','#brand{font-size:12px;')
path.write_text(source)
print('runtime_bytes',path.stat().st_size,'sha256',hashlib.sha256(path.read_bytes()).hexdigest(),flush=True)
