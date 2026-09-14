#!/usr/bin/env python3
"""Execute the actual native WebGPU room and record pixel/interaction evidence."""
from pathlib import Path
import base64,hashlib,http.server,threading,json,time,io,re,functools,traceback,os
from PIL import Image,ImageStat,ImageChops
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/v3';OUT.mkdir(exist_ok=True,parents=True)
cfg=json.loads((ROOT/'qa/stage-v3/RUN.json').read_text());final=cfg.get('mode')=='final'
w,h=(1920,1080) if final else (960,540);samples=cfg.get('samples',32 if final else 6)
report={'viewport':[w,h],'mode':cfg['mode'],'checks':{},'screenshots':[],'errors':[]}
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=srv.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{srv.server_port}/Luna-Stage.html'
def save(data,name):
 raw=base64.b64decode(data.split(',',1)[1]);(OUT/name).write_bytes(raw)
 assert min(ImageStat.Stat(Image.open(io.BytesIO(raw)).convert('RGB')).stddev)>5,name
 return raw
os.environ['DEBUG']='pw:browser'
try:
 with sync_playwright() as pw:
  flags=cfg.get('browser_args',['--no-sandbox','--enable-unsafe-webgpu','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--use-webgpu-adapter=swiftshader','--enable-features=Vulkan','--use-vulkan=swiftshader','--disable-vulkan-surface','--disable-gpu-watchdog','--disable-dev-shm-usage'])
  b=pw.chromium.launch(headless=True,args=flags)
  p=b.new_page(viewport={'width':w,'height':h},device_scale_factor=1,accept_downloads=True)
  p.on('pageerror',lambda e:report['errors'].append(str(e)))
  p.on('console',lambda m:print('CONSOLE',m.type,m.text,flush=True) if m.type in ['warning','error'] else None)
  p.goto(url+'?chapter=3&paused=1',wait_until='load')
  p.wait_for_function('window.Luna && (Luna.gpu.firstGPUMS || document.body.classList.contains("fallback"))',timeout=180000)
  report['gpu']=p.evaluate('({ready:Luna.gpu.ready,backend:Luna.gpu.backend,adapter:Luna.gpu.adapter,errors:Luna.gpu.errors,version:Luna.gpu.version,firstGPUMS:Luna.gpu.firstGPUMS})')
  print(json.dumps(report['gpu']),flush=True);assert report['gpu']['ready'] and report['gpu']['backend']=='WebGPU'
  p.evaluate('Luna.gpu.snapshotBusy=true');report['checks']['native_webgpu']=True
  report['geometry']=p.evaluate('({objects:Luna.scene.objects.length,details:Luna.scene.detailStats,films:Luna.cam.films.length})')
  assert report['geometry']['details']['oliveLeaves']==756 and report['geometry']['films']==50
  report['checks']['geometry_and_50_films']=True
  def capture(name,n=samples,W=w,H=h):
   t=time.monotonic();raw=save(p.evaluate('(a)=>Luna.gpu.captureFrame(...a)',[n,W,H]),name)
   print('RENDER',name,round(time.monotonic()-t,2),flush=True);return raw
  names=['01-arrival','02-grain-morning','03-evening','04-lacquer','05-price-on-worktop','06-wide-still'];frames={}
  for i in (range(6) if final else [2,4]):
   p.evaluate('(i)=>{Luna.cam.goto(i,false);Luna.hud.draw()}',i);frames[i]=capture('room-'+names[i]+'.png')
   p.screenshot(path=str(OUT/(names[i]+'.png')));report['screenshots'].append({'name':names[i]+'.png','sha256':hashlib.sha256((OUT/(names[i]+'.png')).read_bytes()).hexdigest()})
  p.evaluate('Luna.cam.goto(2,false);Luna.cam.eye=[-.23,1.72,2.90];Luna.cam.to=[-2.52,1.34,.56];Luna.cam.fov=39;Luna.hud.draw()');capture('plant-detail.png')
  p.evaluate('Luna.cam.goto(2,false)');on=capture('lights-on.png',2,640,360);p.keyboard.press('l');assert not p.evaluate('Luna.scene.lights');off=capture('lights-off.png',2,640,360)
  diff=ImageStat.Stat(ImageChops.difference(Image.open(io.BytesIO(on)).convert('RGB'),Image.open(io.BytesIO(off)).convert('RGB'))).mean
  assert sum(diff)>2;report['checks']['lights_change_actual_pixels']=True;report['light_pixel_difference']=diff
  p.keyboard.press('l');p.keyboard.press('m');assert p.evaluate('Luna.scene.material')==2;capture('walnut.png',2,640,360);report['checks']['material']=True
  p.keyboard.press('p');assert p.evaluate('Luna.scene.price');p.keyboard.press('c');assert p.evaluate('Luna.scene.ceo');report['checks']['price_and_ceo']=True
  if final:
   p.evaluate('Luna.cam.goto(4,false);Luna.scene.ceo=true;Luna.hud.draw()');capture('room-07-ceo-margin.png');p.screenshot(path=str(OUT/'07-ceo-margin.png'))
  p.keyboard.press('v');assert p.locator('#library').evaluate('(e)=>e.open');count=0
  for i in range(10):p.locator('#film-group-'+str(i)).click();count+=p.locator('.film-card').count()
  assert count==50;p.locator('#close-library').click();report['checks']['film_library']=True
  for i in range(50):
   p.evaluate('(i)=>Luna.cam.playShot(i,false)',i)
   if final:capture(f'film-{i+1:02}.png',1,320,180)
  report['checks']['all_50_applied']=True
  p.evaluate('Luna.cam.goto(2,false)');old=p.evaluate('Luna.cam.eye');p.mouse.move(w*.55,h*.5);p.mouse.down();p.mouse.move(w*.63,h*.52,steps=6);p.mouse.up();assert old!=p.evaluate('Luna.cam.eye');report['checks']['orbit']=True
  old=p.evaluate('Luna.cam.eye');p.mouse.wheel(0,-150);p.wait_for_timeout(300);assert old!=p.evaluate('Luna.cam.eye');report['checks']['zoom']=True
  p.keyboard.press('Escape');assert p.evaluate('Luna.cam.chapter')==5;report['checks']['skip']=True
  p.keyboard.press('f');p.wait_for_timeout(300);assert p.evaluate('!!document.fullscreenElement');p.keyboard.press('f');report['checks']['fullscreen']=True
  report['gpu_errors_end']=p.evaluate('Luna.gpu.errors');assert not report['gpu_errors_end'];assert not report['errors']
  if final:
   stills=[]
   for i in range(6):
    im=Image.open(io.BytesIO(frames[i])).convert('RGB').resize((1280,720),Image.Resampling.LANCZOS);out=io.BytesIO();im.save(out,'WEBP',quality=86,method=6);stills.append('data:image/webp;base64,'+base64.b64encode(out.getvalue()).decode())
   src=(ROOT/'Luna-Stage.html').read_text();src=re.sub(r'const embeddedStills=\[.*?\];','const embeddedStills='+json.dumps(stills,separators=(',',':'))+';',src,count=1,flags=re.S);(ROOT/'Luna-Stage.html').write_text(src)
   fb=b.new_page(viewport={'width':w,'height':h});fb.goto(url+'?backend=canvas2d&chapter=3&paused=1');fb.wait_for_function('document.body.classList.contains("fallback")');fb.wait_for_timeout(800);fb.screenshot(path=str(OUT/'08-fallback.png'))
   assert fb.evaluate('Luna.gpu.backend')=='Canvas2D';assert min(ImageStat.Stat(Image.open(OUT/'08-fallback.png').convert('RGB')).stddev)>5;report['checks']['rebaked_fallback']=True;fb.close()
  report['browser']=b.version;report['source_sha256']=hashlib.sha256((ROOT/'Luna-Stage.html').read_bytes()).hexdigest();report['result']='PASS';b.close()
except Exception:
 report['result']='FAIL';report['exception']=traceback.format_exc();print(report['exception'],flush=True)
finally:
 srv.shutdown();(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
if report['result']!='PASS':raise SystemExit(1)
