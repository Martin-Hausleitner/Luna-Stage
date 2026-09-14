"""Reproducible native Chromium WebGPU checks. QA dependency only: Python Playwright.
Run: python3 qa/verify.py [--url https://Martin-Hausleitner.github.io/Luna-Stage/] [--live]
The browser application itself has no dependencies. Never accept fallback as GPU PASS.
"""
import argparse, functools, hashlib, json, threading, time
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

ap=argparse.ArgumentParser();ap.add_argument('--url');ap.add_argument('--live',action='store_true');ap.add_argument('--full',action='store_true');args=ap.parse_args()
root=Path(__file__).resolve().parent.parent;out=root/'qa';out.mkdir(exist_ok=True);server=None
if not args.url:
    server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(SimpleHTTPRequestHandler,directory=str(root)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    url=f'http://127.0.0.1:{server.server_port}/Luna-Stage.html'
else:url=args.url
report={'url':url,'viewport':[1920,1080],'checks':{},'page_errors':[],'console_errors':[],'screenshots':[]}
with sync_playwright() as p:
    chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    kw={'executable_path':chrome} if Path(chrome).exists() else {}
    b=p.chromium.launch(headless=True,args=['--enable-unsafe-webgpu'],**kw)
    ctx=b.new_context(viewport={'width':1920,'height':1080},device_scale_factor=1,accept_downloads=True)
    page=ctx.new_page();page.on('pageerror',lambda e:report['page_errors'].append(str(e)))
    page.on('console',lambda m:report['console_errors'].append(m.text) if m.type=='error' else None)
    external=[];page.on('request',lambda r:external.append(r.url) if not r.url.startswith(url.split('?')[0]) and not r.url.startswith('data:') else None)
    response=page.goto(url+'?chapter=3&paused=1');report['http_status']=response.status
    page.wait_for_function('window.Luna && (Luna.gpu.ready || document.body.classList.contains("fallback"))',timeout=120000)
    page.wait_for_timeout(1000)
    report['gpu']=page.evaluate('({backend:Luna.gpu.backend,ready:Luna.gpu.ready,adapter:Luna.gpu.adapter,errors:Luna.gpu.errors,frames:Luna.gpu.frames,firstImageMS:Luna.gpu.firstImageMS,firstPaintMS:Luna.gpu.firstPaintMS,firstGPUMS:Luna.gpu.firstGPUMS})')
    report['checks']['real_webgpu']=report['gpu']['ready'];report['checks']['first_image_under_1s']=report['gpu']['firstImageMS']<1000
    print(json.dumps(report['gpu'],ensure_ascii=False),flush=True)
    def shot(i,name,ceo=False):
        page.evaluate('(i)=>Luna.cam.goto(i,false)',i)
        if ceo:page.evaluate('Luna.scene.ceo=true;Luna.hud.sync();Luna.gpu.invalidate()')
        page.wait_for_timeout(600)
        page.evaluate('Luna.gpu.render(1920,1080)')
        page.wait_for_timeout(450)
        path=out/(('live-' if args.live else '')+name+'.png');page.screenshot(path=str(path))
        report['screenshots'].append({'name':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()});print('SHOT',path.name,flush=True)
    if report['gpu']['ready']:
        names=['01-arrival','02-grain-morning','03-evening','04-lacquer','05-price-on-worktop','06-wide-still']
        for i,name in enumerate(names):
            if not args.live or i in [2,4]:shot(i,name)
        if not args.live:shot(4,'07-ceo-margin',True)
        if args.full:
            page.evaluate('Luna.cam.goto(2,false);Luna.scene.ceo=false;Luna.hud.sync()')
            before=page.evaluate('Luna.scene.material');page.keyboard.press('m')
            report['checks']['material_key']=page.evaluate('Luna.scene.material')!=before
            before=page.evaluate('Luna.scene.price');page.keyboard.press('p')
            report['checks']['price_key']=page.evaluate('Luna.scene.price')!=before
            page.keyboard.press('c');report['checks']['ceo_key']=page.evaluate('Luna.scene.ceo')
            page.keyboard.press('c');report['checks']['ceo_off']=not page.evaluate('Luna.scene.ceo')
            page.keyboard.press('f');page.wait_for_timeout(400)
            report['checks']['fullscreen']=page.evaluate('!!document.fullscreenElement')
            if report['checks']['fullscreen']:page.keyboard.press('f')
            page.evaluate('Luna.cam.goto(4,false)');page.wait_for_timeout(500)
            point=page.evaluate('Luna.cam.project([.60,.959,.65])')
            old=page.evaluate('Luna.scene.price');page.mouse.click(point['x'],point['y']);report['checks']['worktop_hit']=page.evaluate('Luna.scene.price')!=old
            point=page.evaluate('Luna.cam.project([.05,.55,.926])');old=page.evaluate('Luna.scene.material');page.mouse.click(point['x'],point['y']);report['checks']['door_hit']=page.evaluate('Luna.scene.material')!=old
            page.locator('#sun').evaluate('(e)=>{e.value=6;e.dispatchEvent(new Event("input",{bubbles:true}))}');report['checks']['sun_slider']=abs(page.evaluate('Luna.scene.sun')-.06)<.001
            old=page.evaluate('Luna.cam.eye.slice()');page.mouse.move(1600,600);page.mouse.down();page.mouse.move(1500,630,steps=10);page.mouse.up();report['checks']['free_orbit']=page.evaluate('Luna.cam.eye')!=old
            page.keyboard.press('Escape');report['checks']['skip_to_still']=page.evaluate('Luna.cam.chapter===5&&!Luna.cam.playing')
            with page.expect_download(timeout=120000) as d:page.keyboard.press('s')
            d.value.save_as(str(out/'STAGE-Berger-Abend.png'));report['checks']['snapshot']=page.evaluate('Luna.gpu.lastSnapshot')
            report['checks']['store_key']=page.evaluate('JSON.parse(localStorage.getItem("luna.stage.v1")).version===1')
            page.reload();page.wait_for_function('window.Luna && (Luna.gpu.ready || document.body.classList.contains("fallback"))',timeout=120000)
            report['checks']['ceo_default_off']=not page.evaluate('Luna.scene.ceo')
            report['checks']['room_contract']=page.evaluate('Luna.scene.bounds()')
            fb=ctx.new_page();fb.goto(url+'?backend=canvas2d&chapter=5&paused=1');fb.wait_for_function('document.body.classList.contains("fallback")');fb.screenshot(path=str(out/'08-canvas2d-fallback.png'))
            report['checks']['canvas_fallback']=fb.evaluate('Luna.gpu.backend==="Canvas2D" && document.querySelectorAll("#filmstrip canvas").length===6 && document.querySelector("#still").width>0')
            fb.close()
    else:page.screenshot(path=str(out/'diagnostic.png'))
    report['network_requests']=external;report['browser']=b.version;report['gpu_errors_end']=page.evaluate('Luna.gpu.errors');b.close()
if server:server.shutdown()
(out/('live-report.json' if args.live else 'local-report.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
if not report['checks']['real_webgpu']:raise SystemExit(2)
