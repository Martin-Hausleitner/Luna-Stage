from pathlib import Path
from playwright.sync_api import sync_playwright
import http.server,threading,functools,json,time,base64,traceback,platform
root=Path(__file__).resolve().parents[2];out=root/'qa/probe';out.mkdir(parents=True,exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)));threading.Thread(target=srv.serve_forever,daemon=True).start()
r={'platform':platform.platform()};t=time.monotonic()
def log(k,v):
 r[k]=v;r['elapsed_seconds']=round(time.monotonic()-t,2);(out/'report.json').write_text(json.dumps(r,indent=2));print(k,v,flush=True)
try:
 with sync_playwright() as p:
  args=['--no-sandbox','--enable-unsafe-webgpu','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--use-webgpu-adapter=swiftshader','--enable-features=Vulkan','--use-vulkan=swiftshader','--disable-vulkan-surface','--disable-gpu-watchdog','--disable-dev-shm-usage']
  if platform.system()=='Darwin':args=['--enable-unsafe-webgpu']
  b=p.chromium.launch(headless=True,args=args);page=b.new_page(viewport={'width':320,'height':180});page.on('console',lambda m:print(m.type,m.text,flush=True))
  log('browser',b.version);page.goto(f'http://127.0.0.1:{srv.server_port}/Luna-Stage.html?chapter=3&paused=1');log('loaded',True)
  page.wait_for_function('window.Luna && (Luna.gpu.ready || document.body.classList.contains("fallback"))',timeout=120000)
  log('gpu',page.evaluate('({backend:Luna.gpu.backend,ready:Luna.gpu.ready,errors:Luna.gpu.errors,adapter:Luna.gpu.adapter})'))
  page.evaluate('Luna.gpu.snapshotBusy=true');log('paused',True)
  page.wait_for_function('Luna.gpu.firstGPUMS || !Luna.gpu.ready',timeout=120000)
  log('firstGPUMS',page.evaluate('Luna.gpu.firstGPUMS'));assert page.evaluate('Luna.gpu.ready')
  data=page.evaluate('Luna.gpu.captureFrame(1,320,180)');(out/'room.png').write_bytes(base64.b64decode(data.split(',')[1]));log('captured',True)
  page.screenshot(path=str(out/'browser.png'));log('result','PASS');b.close()
except Exception:log('failure',traceback.format_exc());raise
finally:srv.shutdown()
