"""Live Pages verification against the approved runtime; actual screenshots, no overlays."""
from pathlib import Path
import functools,hashlib,http.server,json,threading,time,traceback
from playwright.sync_api import sync_playwright
from PIL import Image,ImageStat
ROOT=Path(__file__).resolve().parents[2];QA=ROOT/'qa/atelier';OUT=ROOT/'live-output';OUT.mkdir(exist_ok=True)
request=json.loads((QA/'live-request.json').read_text());expected=request['runtime_sha256'];url='https://martin-hausleitner.github.io/Luna-Stage/'
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
report={'url':url,'runtime_sha256':expected,'checks':{},'errors':[],'console_errors':[],'screenshots':[],'request':request}
def check(name,value):
    report['checks'][name]=bool(value);print(name,bool(value),flush=True)
    if not value:raise AssertionError(name)
def shot(page,name):
    page.evaluate('async()=>{Luna.cam.stop();busy=true;await Luna.gpu.pending;stateKey="";sampleCount=0;await Luna.gpu.settle(1920,1080,4);busy=true;Luna.hud.draw()}')
    path=OUT/name;page.screenshot(path=str(path),timeout=120000);image=Image.open(path);std=ImageStat.Stat(image.convert('RGB')).stddev
    check(name+'_actual_room_pixels',min(std)>12 and image.size==(1920,1080))
    report['screenshots'].append({'name':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size':list(image.size),'stddev':std})
    page.evaluate('busy=false;Luna.gpu.invalidate()')
with sync_playwright() as p:
    from gpu_probe import select_browser
    browser=p.chromium.launch(**select_browser(p,QA,f'http://127.0.0.1:{server.server_port}'))
    report['browser']=browser.version;page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
    page.set_default_timeout(120000);page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('console',lambda m:report['console_errors'].append(m.text) if m.type=='error' else None)
    try:
        for attempt in range(20):
            response=page.goto(url+'?chapter=3&paused=1&fresh=1',wait_until='domcontentloaded');body=response.body()
            if response.status==200 and hashlib.sha256(body).hexdigest()==expected:break
            page.wait_for_timeout(3000)
        check('http_200',response.status==200);check('approved_runtime_identical',hashlib.sha256(body).hexdigest()==expected)
        page.wait_for_function("window.Luna && (Luna.gpu.firstGPUMS || document.body.classList.contains('fallback'))",timeout=120000)
        check('real_webgpu',page.evaluate('Luna.gpu.ready && Luna.gpu.backend==="WebGPU"'))
        report['gpu']=page.evaluate('({...Luna.qa.getState(),presentation:Luna.gpu.presentation,software:Luna.gpu.software})')
        shot(page,'live-03-evening.png');page.evaluate('Luna.cam.goto(4,false)');shot(page,'live-05-price-on-worktop.png')
        page.keyboard.press('e');check('live_editor_opens',page.locator('#editor').is_visible());page.locator('[data-theme="olive"]').click();check('live_theme_changes',page.evaluate('Luna.scene.theme==="olive" && Luna.scene.styles.front==="sage"'))
        page.evaluate('Luna.cam.view("wide")');shot(page,'live-08-editor.png');page.keyboard.press('e');page.keyboard.press('f');check('live_fullscreen',page.evaluate('!!document.fullscreenElement'));page.keyboard.press('f')
        check('no_js_errors',not report['errors']);check('no_gpu_errors',page.evaluate('Luna.gpu.errors.length===0'));report['result']='PASS'
    except Exception as e:
        report['result']='FAIL';report['exception']=str(e);report['traceback']=traceback.format_exc();print(traceback.format_exc(),flush=True)
        try:page.screenshot(path=str(OUT/'live-failure.png'))
        except Exception:pass
    finally:
        report['verified_at_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());(OUT/'live-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True);browser.close();server.shutdown()
if report.get('result')!='PASS':raise SystemExit(1)
