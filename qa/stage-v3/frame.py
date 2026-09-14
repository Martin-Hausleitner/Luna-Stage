from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageStat,ImageChops
import http.server,threading,functools,json,time,base64,traceback,io,sys,hashlib
root=Path(__file__).resolve().parents[2];cfg=json.loads((root/'qa/stage-v3/FRAMES.json').read_text());ch=int(sys.argv[1]);out=root/'qa/frames';out.mkdir(parents=True,exist_ok=True)
names=['01-arrival','02-grain-morning','03-evening','04-lacquer','05-price-on-worktop','06-wide-still','07-ceo-margin','09-plant-detail'];name=names[ch]
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)));threading.Thread(target=srv.serve_forever,daemon=True).start()
r={'name':name,'source_sha256':hashlib.sha256((root/'Luna-Stage.html').read_bytes()).hexdigest(),'checks':{},'errors':[]};t=time.monotonic()
def record(k,v):
 r[k]=v;r['elapsed_seconds']=round(time.monotonic()-t,2);(out/(name+'.json')).write_text(json.dumps(r,indent=2));print(k,v,flush=True)
def image(data,filename):
 raw=base64.b64decode(data.split(',')[1]);im=Image.open(io.BytesIO(raw));assert min(ImageStat.Stat(im.convert('RGB')).stddev)>5
 (out/filename).write_bytes(raw);return im.convert('RGB')
try:
 with sync_playwright() as p:
  b=p.chromium.launch(headless=True,args=['--enable-unsafe-webgpu']);page=b.new_page(viewport={'width':320,'height':180},device_scale_factor=1,accept_downloads=True)
  page.on('pageerror',lambda e:r['errors'].append(str(e)));page.on('console',lambda m:print(m.type,m.text,flush=True) if m.type=='error' else None)
  record('browser',b.version);page.goto(f'http://127.0.0.1:{srv.server_port}/Luna-Stage.html?chapter=3&paused=1')
  page.wait_for_function('window.Luna && (Luna.gpu.ready || document.body.classList.contains("fallback"))',timeout=120000)
  page.evaluate('Luna.gpu.snapshotBusy=true');page.wait_for_function('Luna.gpu.firstGPUMS || !Luna.gpu.ready',timeout=120000)
  record('gpu',page.evaluate('({backend:Luna.gpu.backend,ready:Luna.gpu.ready,errors:Luna.gpu.errors,adapter:Luna.gpu.adapter,version:Luna.gpu.version})'));assert r['gpu']['ready']
  page.set_viewport_size({'width':1920,'height':1080});page.evaluate('(ch)=>{Luna.cam.goto(ch<6?ch:ch===6?4:2,false);if(ch===6)Luna.scene.ceo=true;if(ch===7){Luna.cam.eye=[-.23,1.72,2.90];Luna.cam.to=[-2.52,1.34,.56];Luna.cam.fov=39}Luna.hud.draw()}',ch)
  record('geometry',page.evaluate('({objects:Luna.scene.objects.length,oliveLeaves:Luna.scene.detailStats.oliveLeaves,films:Luna.cam.films.length})'))
  samples=cfg.get('samples',4);frame=image(page.evaluate('(n)=>Luna.gpu.captureFrame(n,1920,1080)',samples),'room-'+name+'.png')
  page.screenshot(path=str(out/(name+'.png')));record('frame',{'width':frame.width,'height':frame.height,'samples':samples,'sha256':hashlib.sha256((out/(name+'.png')).read_bytes()).hexdigest()})
  assert frame.size==(1920,1080);r['checks']['native_full_resolution']=True
  if ch==2:
   page.evaluate('Luna.cam.goto(2,false)');on=image(page.evaluate('Luna.gpu.captureFrame(1,320,180)'),'controls-light-on.png');page.keyboard.press('l');assert not page.evaluate('Luna.scene.lights');off=image(page.evaluate('Luna.gpu.captureFrame(1,320,180)'),'controls-light-off.png')
   assert sum(ImageStat.Stat(ImageChops.difference(on,off)).mean)>2;r['checks']['lights_change_pixels']=True;page.keyboard.press('l');page.keyboard.press('m');assert page.evaluate('Luna.scene.material')==2;r['checks']['materials']=True
   page.keyboard.press('p');assert page.evaluate('Luna.scene.price');page.keyboard.press('c');assert page.evaluate('Luna.scene.ceo');r['checks']['price_ceo']=True
   page.keyboard.press('v');assert page.locator('#library').evaluate('(e)=>e.open');total=0
   for i in range(10):page.locator('#film-group-'+str(i)).click();total+=page.locator('.film-card').count()
   assert total==50;page.locator('#close-library').click();r['checks']['50_library_entries']=True
   for i in range(50):
    page.evaluate('(i)=>Luna.cam.playShot(i,false)',i);image(page.evaluate('Luna.gpu.captureFrame(1,128,72)'),f'film-{i+1:02}.png')
   r['checks']['50_clips_executed']=True;page.evaluate('Luna.cam.goto(2,false)');eye=page.evaluate('Luna.cam.eye');page.mouse.move(1030,500);page.mouse.down();page.mouse.move(1160,530,steps=5);page.mouse.up();assert eye!=page.evaluate('Luna.cam.eye');r['checks']['orbit']=True
   eye=page.evaluate('Luna.cam.eye');page.mouse.wheel(0,-120);page.wait_for_timeout(300);assert eye!=page.evaluate('Luna.cam.eye');r['checks']['zoom']=True;page.keyboard.press('Escape');assert page.evaluate('Luna.cam.chapter')==5;r['checks']['skip']=True
   page.keyboard.press('f');page.wait_for_timeout(300);assert page.evaluate('!!document.fullscreenElement');page.keyboard.press('f');r['checks']['fullscreen']=True
  assert not r['errors'];assert not page.evaluate('Luna.gpu.errors');r['checks']['zero_gpu_js_errors']=True
  record('result','PASS');b.close()
except Exception:record('exception',traceback.format_exc());record('result','FAIL');raise
finally:srv.shutdown()
