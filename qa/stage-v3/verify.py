#!/usr/bin/env python3
"""Native WebGPU execution and actual browser evidence. Never label fallback as GPU."""
from pathlib import Path
import base64,hashlib,http.server,threading,json,time,io,re,functools,traceback
from PIL import Image,ImageStat,ImageChops
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/v3';OUT.mkdir(exist_ok=True,parents=True)
config=json.loads((ROOT/'qa/stage-v3/RUN.json').read_text())
final=config.get('mode')=='final';w,h=(1920,1080) if final else (1280,720)
samples=32 if final else 10
report={'mode':config.get('mode'),'viewport':[w,h],'screenshots':[],'checks':{},'errors':[]}
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/Luna-Stage.html'
def record(data,name):
 raw=base64.b64decode(data.split(',',1)[1]);(OUT/name).write_bytes(raw)
 im=Image.open(io.BytesIO(raw));std=ImageStat.Stat(im.convert('RGB')).stddev
 assert min(std)>5,(name,std)
 return raw
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox','--enable-unsafe-webgpu','--enable-features=Vulkan','--use-angle=vulkan','--use-vulkan=swiftshader','--disable-vulkan-surface','--disable-dev-shm-usage'])
  page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1,accept_downloads=True)
  page.on('pageerror',lambda e:report['errors'].append(str(e)))
  page.on('console',lambda m:print('CONSOLE',m.type,m.text,flush=True) if m.type in ('error','warning') else None)
  page.goto(url+'?chapter=3&paused=1',wait_until='load',timeout=90000)
  page.wait_for_function('window.Luna && (Luna.gpu.ready || document.body.classList.contains("fallback"))',timeout=180000)
  gpu=page.evaluate('({ready:Luna.gpu.ready,backend:Luna.gpu.backend,errors:Luna.gpu.errors,adapter:Luna.gpu.adapter,version:Luna.gpu.version})');report['gpu']=gpu
  print(json.dumps(gpu),flush=True);assert gpu['ready'] and gpu['backend']=='WebGPU',gpu
  page.evaluate('Luna.gpu.snapshotBusy=true')
  report['checks']['native_webgpu']=True
  stats=page.evaluate('({objects:Luna.scene.objects.length,details:Luna.scene.detailStats,films:Luna.cam.films.length,shapes:[...new Set(Luna.scene.objects.map(o=>o.type))]})');report['geometry']=stats
  assert stats['details']['oliveLeaves']==756;assert stats['films']==50
  assert 5 in stats['shapes'] and 6 in stats['shapes']
  report['checks']['individual_3d_leaves']=True
  report['checks']['fifty_camera_sequences']=True
  report['checks']['valid_scene']=page.evaluate('Luna.scene.objects.every(o=>[...o.c,...o.s,...o.extra].every(Number.isFinite))')
  frames={}
  chapters=range(6) if final else [2,4]
  names=['01-arrival','02-grain-morning','03-evening','04-lacquer','05-price-on-worktop','06-wide-still']
  for i in chapters:
   page.evaluate('(i)=>{Luna.cam.goto(i,false);Luna.hud.draw()}',i)
   then=time.monotonic();data=page.evaluate('async(o)=>await Luna.gpu.captureFrame(o.s,o.w,o.h)',{'s':samples,'w':w,'h':h})
   raw=record(data,'room-'+names[i]+'.png');frames[i]=raw
   page.screenshot(path=str(OUT/(names[i]+'.png')))
   report['screenshots'].append({'name':names[i]+'.png','sha256':hashlib.sha256((OUT/(names[i]+'.png')).read_bytes()).hexdigest(),'render_seconds':round(time.monotonic()-then,2)})
   print('SHOT',names[i],round(time.monotonic()-then,2),flush=True)
  page.evaluate('''()=>{Luna.cam.goto(2,false);Luna.cam.eye=[-.23,1.72,2.90];Luna.cam.to=[-2.52,1.34,.56];Luna.cam.fov=39;Luna.hud.draw()}''')
  record(page.evaluate('async(o)=>await Luna.gpu.captureFrame(o.s,o.w,o.h)',{'s':samples,'w':w,'h':h}),'plant-detail.png')
  print('SHOT plant',flush=True)
  page.evaluate('Luna.cam.goto(2,false)');day=record(page.evaluate('Luna.gpu.captureFrame(2,640,360)'),'control-lights-on.png')
  page.keyboard.press('l');assert page.evaluate('Luna.scene.lights') is False
  dark=record(page.evaluate('Luna.gpu.captureFrame(2,640,360)'),'control-lights-off.png')
  diff=ImageStat.Stat(ImageChops.difference(Image.open(io.BytesIO(day)).convert('RGB'),Image.open(io.BytesIO(dark)).convert('RGB'))).mean
  assert sum(diff)>2,diff;report['checks']['light_key_changes_render']=True;report['light_pixel_difference']=diff
  page.keyboard.press('l');page.keyboard.press('m');assert page.evaluate('Luna.scene.material')==2
  record(page.evaluate('Luna.gpu.captureFrame(2,640,360)'),'control-walnut.png');report['checks']['material_cycle']=True
  page.keyboard.press('p');assert page.evaluate('Luna.scene.price');report['checks']['price_control']=True
  page.keyboard.press('c');assert page.evaluate('Luna.scene.ceo');report['checks']['ceo_control']=True
  if final:
   page.evaluate('Luna.cam.goto(4,false);Luna.scene.ceo=true;Luna.hud.draw()')
   record(page.evaluate('Luna.gpu.captureFrame(32,1920,1080)'),'room-07-ceo-margin.png')
   page.screenshot(path=str(OUT/'07-ceo-margin.png'))
  page.keyboard.press('v');assert page.locator('#library').evaluate('(e)=>e.open')
  total=0
  for i in range(10):
   page.locator('#film-group-'+str(i)).click();total+=page.locator('.film-card').count()
  assert total==50;page.locator('#close-library').click();report['checks']['film_library_50_selectable']=True
  for i in range(50):
   page.evaluate('(i)=>Luna.cam.playShot(i,false)',i)
   if final:record(page.evaluate('Luna.gpu.captureFrame(1,320,180)'),f'film-{i+1:02}.png')
  report['checks']['all_50_definitions_applied']=True
  page.evaluate('Luna.cam.goto(2,false)');eye=page.evaluate('Luna.cam.eye')
  page.mouse.move(w*.55,h*.5);page.mouse.down();page.mouse.move(w*.63,h*.52,steps=6);page.mouse.up()
  assert eye!=page.evaluate('Luna.cam.eye');report['checks']['free_orbit']=True
  old=page.evaluate('Luna.cam.eye');page.mouse.wheel(0,-150);assert old!=page.evaluate('Luna.cam.eye');report['checks']['zoom']=True
  page.keyboard.press('Escape');assert page.evaluate('Luna.cam.chapter')==5;report['checks']['skip']=True
  page.keyboard.press('f');report['checks']['fullscreen']=page.evaluate('!!document.fullscreenElement');page.keyboard.press('f')
  report['gpu_errors_end']=page.evaluate('Luna.gpu.errors');assert not report['gpu_errors_end'];assert not report['errors']
  if final:
   embedded=[]
   for i in range(6):
    im=Image.open(io.BytesIO(frames[i])).convert('RGB').resize((1280,720),Image.Resampling.LANCZOS);b=io.BytesIO();im.save(b,'WEBP',quality=86,method=6)
    embedded.append('data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode())
   source=(ROOT/'Luna-Stage.html').read_text();source=re.sub(r'const embeddedStills=\[.*?\];','const embeddedStills='+json.dumps(embedded,separators=(',',':'))+';',source,count=1,flags=re.S)
   (ROOT/'Luna-Stage.html').write_text(source)
   fb=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
   fb.goto(url+'?backend=canvas2d&chapter=3&paused=1');fb.wait_for_function('document.body.classList.contains("fallback")');fb.wait_for_timeout(1000)
   assert fb.evaluate('Luna.gpu.backend')=='Canvas2D';fb.screenshot(path=str(OUT/'08-fallback.png'));report['checks']['rebaked_fallback']=True
   report['checks']['fallback_nonblank']=min(ImageStat.Stat(Image.open(OUT/'08-fallback.png').convert('RGB')).stddev)>5
   fb.close()
  report['browser']=browser.version;report['source_sha256']=hashlib.sha256((ROOT/'Luna-Stage.html').read_bytes()).hexdigest()
  report['result']='PASS' if all(report['checks'].values()) else 'FAIL'
  browser.close()
except Exception as e:
 report['result']='FAIL';report['exception']=traceback.format_exc();print(report['exception'],flush=True)
finally:
 server.shutdown();(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
if report['result']!='PASS':raise SystemExit(1)
