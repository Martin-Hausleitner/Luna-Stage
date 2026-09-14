"""Real browser/WGSL verification. Never accepts a still as a GPU PASS."""
from pathlib import Path
import functools, hashlib, http.server, json, threading, time, traceback
from playwright.sync_api import sync_playwright
from PIL import Image, ImageStat
ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'qa/atelier'
OUT=QA/'screenshots';OUT.mkdir(exist_ok=True)
report={'checks':{},'errors':[],'console':[],'screenshots':[],'source_sha256':hashlib.sha256((ROOT/'Luna-Stage.html').read_bytes()).hexdigest(),'visual_review':'PENDING'}
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/Luna-Stage.html'
def check(name,value):
    report['checks'][name]=bool(value)
    print('CHECK',name,bool(value),flush=True)
    if not value:raise AssertionError(name)
def shot(page,name,n=24):
    start=time.monotonic()
    page.evaluate('async n=>{Luna.cam.stop();await Luna.gpu.settle(1920,1080,n);busy=true;Luna.hud.draw()}',n)
    page.screenshot(path=str(OUT/name),timeout=120000)
    image=Image.open(OUT/name)
    record={'name':name,'size':list(image.size),'sha256':hashlib.sha256((OUT/name).read_bytes()).hexdigest(),'seconds':round(time.monotonic()-start,3),'stddev':ImageStat.Stat(image.convert('RGB')).stddev}
    report['screenshots'].append(record)
    print('SHOT',json.dumps(record),flush=True)
    page.evaluate('busy=false;Luna.gpu.invalidate()')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--no-sandbox','--enable-unsafe-webgpu','--use-angle=swiftshader','--enable-features=Vulkan','--disable-vulkan-surface','--disable-dev-shm-usage'])
    report['browser']=browser.version
    page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1,accept_downloads=True)
    page.set_default_timeout(120000)
    page.on('pageerror',lambda e:report['errors'].append(str(e)))
    page.on('console',lambda e:report['console'].append(e.text) if e.type=='error' else None)
    try:
        response=page.goto(url+'?chapter=3&paused=1&fresh=1',wait_until='domcontentloaded')
        check('http_200',response.status==200)
        page.wait_for_function("window.Luna && (Luna.gpu.ready || document.body.classList.contains('fallback'))",timeout=240000)
        report['gpu']=page.evaluate('Luna.qa.getState()')
        print('GPU',json.dumps(report['gpu']),flush=True)
        check('native_webgpu',page.evaluate('Luna.gpu.ready && Luna.gpu.backend==="WebGPU"'))
        check('embedded_external_textures',page.evaluate('Luna.gpu.sourceTextures.length===2'))
        check('ceo_default_off',page.evaluate('!Luna.scene.ceo'))
        shot(page,'03-evening.png',24)
        page.evaluate('Luna.cam.goto(1,false)');shot(page,'02-morning.png',24)
        page.evaluate('Luna.cam.goto(4,false)');shot(page,'05-price.png',24)
        page.keyboard.press('e')
        check('editor_toggle',page.evaluate('Luna.editor.open'))
        page.locator('[data-theme="olive"]').click()
        check('live_theme',page.evaluate('Luna.scene.theme==="olive" && Luna.scene.styles.front==="sage"'))
        page.evaluate('Luna.cam.view("wide")');shot(page,'08-atelier-olive.png',24)
        page.evaluate('Luna.editor.select("island","front")')
        before=page.evaluate('Luna.qa.center("island")')
        page.locator('#pos-x').fill('450');page.locator('#pos-x').press('Tab')
        check('numeric_move',abs(page.evaluate('Luna.qa.center("island")[0]')-.45)<.002)
        page.locator('#undo').click()
        check('undo_move',abs(page.evaluate('Luna.qa.center("island")[0]')-before[0])<.002)
        page.locator('#redo').click()
        check('redo_move',abs(page.evaluate('Luna.qa.center("island")[0]')-.45)<.002)
        page.locator('[data-material="walnut"]').click()
        check('per_object_surface',page.evaluate('Luna.scene.group("island").overrides.front.id==="walnut"'))
        check('valid_project_document',page.evaluate('!!Luna.store.validate(Luna.store.document())'))
        page.locator('#tab-room').click()
        with page.expect_download() as got:page.locator('#project-save').click()
        downloaded=QA/'project-export.json';got.value.save_as(str(downloaded))
        check('real_project_download',json.loads(downloaded.read_text())['schema']=='luna.stage.project')
        check('no_page_errors',not report['errors'])
        check('no_gpu_errors',page.evaluate('Luna.gpu.errors.length===0'))
        report['result']='PASS';report['visual_review']='PENDING HUMAN VISION CHECK'
    except Exception as error:
        report['result']='FAIL';report['exception']=str(error);report['traceback']=traceback.format_exc()
        try:
            report['gpu_at_failure']=page.evaluate('window.Luna && Luna.qa.getState()')
            page.screenshot(path=str(OUT/'failure.png'),timeout=30000)
        except Exception:pass
        print(traceback.format_exc(),flush=True)
    finally:
        (QA/'report.json').write_text(json.dumps(report,indent=2))
        print(json.dumps(report,indent=2),flush=True)
        browser.close();server.shutdown()
if report.get('result')!='PASS':raise SystemExit(1)
