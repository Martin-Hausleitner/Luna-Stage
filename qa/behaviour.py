"""Real browser film timing, persistence, resilience and PNG pixel checks."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import functools,threading,json,time,hashlib
from playwright.sync_api import sync_playwright
from PIL import Image,ImageStat
root=Path(__file__).resolve().parent.parent
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(SimpleHTTPRequestHandler,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/Luna-Stage.html'
report={'checks':{},'measurements':{},'errors':[],'source_sha256':hashlib.sha256((root/'Luna-Stage.html').read_bytes()).hexdigest()}
checks=report['checks']
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args=['--enable-unsafe-webgpu'])
 ctx=b.new_context(viewport={'width':1920,'height':1080},device_scale_factor=1)
 page=ctx.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)))
 page.goto(url);page.wait_for_function('window.Luna && Luna.gpu.ready',timeout=120000)
 checks['autoplay_on_fresh_visit']=page.evaluate('Luna.cam.playing')
 page.evaluate('window.observations=[];window.filmStarted=performance.now()-Luna.cam.time*1000;window.observer=setInterval(()=>observations.push({t:Luna.cam.time,chapter:Luna.cam.chapter,material:Luna.scene.material,price:Luna.scene.price,ceo:Luna.scene.ceo}),120)')
 page.wait_for_function('Luna.cam.time>=48&&!Luna.cam.playing',timeout=65000)
 elapsed=page.evaluate('(performance.now()-filmStarted)/1000');data=page.evaluate('observations');page.evaluate('clearInterval(observer)')
 report['measurements']['film_wall_seconds']=elapsed;report['film_observations']=data
 checks['film_40_to_55_seconds']=40<=elapsed<=55
 checks['six_chapters_executed']=sorted(set(o['chapter'] for o in data))==list(range(6))
 surfaces=[o['material'] for o in data if o['chapter']==3]
 checks['oak_lacquer_oak_sequence']=0 in surfaces and 1 in surfaces and surfaces.index(1)>0 and surfaces[-1]==0
 checks['price_in_chapter_five']=any(o['price'] for o in data if o['chapter']==4)
 checks['ceo_off_entire_film']=all(not o['ceo'] for o in data)
 checks['stille_landing']=page.evaluate('Luna.cam.chapter===5 && document.body.classList.contains("stille")')
 page.evaluate('Luna.cam.goto(2,false);Luna.scene.material=1;Luna.scene.sun=.17;Luna.scene.price=true;Luna.scene.ceo=true;Luna.store.write()')
 page.reload();page.wait_for_function('window.Luna&&Luna.gpu.ready',timeout=120000)
 checks['restored_preferences']=page.evaluate('Luna.scene.material===1&&Luna.scene.sun===.17&&Luna.scene.price&&Luna.cam.chapter===2&&!Luna.cam.playing')
 checks['ceo_not_restored']=page.evaluate('!Luna.scene.ceo&&!JSON.parse(localStorage.getItem("luna.stage.v1")).ceo')
 checks['no_scrollbars']=page.evaluate('document.documentElement.scrollWidth<=innerWidth&&document.documentElement.scrollHeight<=innerHeight')
 ctx.close()
 reduced=b.new_context(viewport={'width':1920,'height':1080},reduced_motion='reduce');r=reduced.new_page();r.goto(url);r.wait_for_function('window.Luna&&Luna.gpu.ready',timeout=120000);checks['reduced_motion_no_autoplay']=r.evaluate('!Luna.cam.playing');reduced.close()
 denied=b.new_context();d=denied.new_page();d.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new DOMException('Storage unavailable','SecurityError')}})");d.goto(url+'?paused=1');d.wait_for_function('window.Luna&&Luna.gpu.ready',timeout=120000);d.keyboard.press('m');checks['storage_denial_safe']=d.evaluate('Luna.scene.material===1&&Luna.store.write()===false');denied.close()
 unavailable=b.new_context();d=unavailable.new_page();d.add_init_script("Object.defineProperty(navigator,'gpu',{value:undefined})");d.goto(url+'?paused=1');d.wait_for_function('document.body.classList.contains("fallback")');checks['actual_unavailable_gpu_fallback']=d.evaluate('Luna.gpu.backend==="Canvas2D"&&document.querySelectorAll("#filmstrip canvas").length===6');unavailable.close()
 b.close()
image=Image.open(root/'qa'/'STAGE-Berger-Abend.png').convert('RGB');stats=ImageStat.Stat(image.crop((0,0,1920,950)))
checks['snapshot_exact_resolution']=image.size==(1920,1080)
checks['snapshot_contains_room_pixels']=min(stats.stddev)>20 and min(stats.mean)>10
report['measurements']['snapshot_channel_stddev']=stats.stddev
report['measurements']['snapshot_bytes']=(root/'qa'/'STAGE-Berger-Abend.png').stat().st_size
report['all_pass']=all(checks.values()) and not report['errors']
(root/'qa'/'behaviour-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps({k:v for k,v in report.items() if k!='film_observations'},indent=2),flush=True)
server.shutdown()
if not report['all_pass']:raise SystemExit(1)
