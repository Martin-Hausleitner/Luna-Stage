"""Native WebGPU acceptance: real inputs, actual encoded downloads, no fake rendering."""
from pathlib import Path
import base64, functools, hashlib, http.server, io, json, os, re, shutil, threading, time, traceback
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops, ImageStat, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'qa/atelier';OUT=QA/'screenshots';OUT.mkdir(exist_ok=True)
report={'checks':{},'errors':[],'console':[],'screenshots':[],'visual_review':'PENDING','started_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/Luna-Stage.html'

def check(name,value):
    report['checks'][name]=bool(value); print('CHECK',name,bool(value),flush=True)
    if not value: raise AssertionError(name)

def capture(page,name,samples=32,raw=False):
    vp=page.viewport_size;w,h=vp['width'],vp['height'];start=time.monotonic()
    page.evaluate('async d=>{Luna.cam.stop();busy=true;await Luna.gpu.pending;stateKey="";sampleCount=0;await Luna.gpu.settle(d.w,d.h,d.n);busy=true;Luna.hud.draw()}',{'w':w,'h':h,'n':samples})
    path=OUT/name
    if raw:page.locator('#room').screenshot(path=str(path),timeout=120000)
    else:
        page.screenshot(path=str(path),timeout=120000)
        if name[:2] in ['01','02','03','04','05','06']:
            page.locator('#room').screenshot(path=str(OUT/('raw-'+name)),timeout=120000)
    image=Image.open(path);record={'name':name,'size':list(image.size),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'render_seconds':round(time.monotonic()-start,3),'stddev':ImageStat.Stat(image.convert('RGB')).stddev}
    report['screenshots'].append(record);print('SHOT',json.dumps(record),flush=True)
    page.evaluate('busy=false;Luna.gpu.invalidate()');return path

def wait_gpu(page):
    page.wait_for_function("window.Luna && (Luna.gpu.firstGPUMS || document.body.classList.contains('fallback'))",timeout=240000)
    check('native_webgpu_'+str(len(report['checks'])),page.evaluate("Luna.gpu.ready && Luna.gpu.backend==='WebGPU' && Luna.gpu.firstGPUMS>0"))

with sync_playwright() as p:
    from gpu_probe import select_browser
    browser=p.chromium.launch(**select_browser(p,QA,url.rsplit('/',1)[0]))
    report['browser']=browser.version
    page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1,accept_downloads=True)
    page.set_default_timeout(240000)
    page.on('pageerror',lambda e:report['errors'].append(str(e)))
    page.on('console',lambda e:report['console'].append(e.text) if e.type=='error' else None)
    network=[];page.on('request',lambda req:network.append(req.url) if req.url.startswith(('http://','https://')) and not req.url.startswith(url) else None)
    try:
        check('http_200',page.goto(url+'?chapter=3&paused=1&fresh=1',wait_until='domcontentloaded').status==200)
        wait_gpu(page);report['gpu']=page.evaluate('Luna.qa.getState()')
        check('two_cc0_source_textures',page.evaluate('Luna.gpu.sourceTextures.length===2'))
        check('ceo_default_off',page.evaluate('!Luna.scene.ceo'))
        pristine=page.evaluate('Luna.store.document()')
        check('first_image_under_second',page.evaluate('Luna.gpu.firstImageMS<1000'))
        stills=[]
        names=['01-arrival.png','02-grain-morning.png','03-evening.png','04-lacquer.png','05-price-on-worktop.png','06-wide-still.png']
        for i,name in enumerate(names):
            page.evaluate('i=>Luna.cam.goto(i,false)',i)
            capture(page,name,32)
            raw=OUT/('raw-'+name)
            image=Image.open(raw).convert('RGB');image.thumbnail((1280,720));buf=io.BytesIO();image.save(buf,'WEBP',quality=74,method=6)
            stills.append('data:image/webp;base64,'+base64.b64encode(buf.getvalue()).decode())
        morning=Image.open(OUT/names[1]);evening=Image.open(OUT/names[2])
        check('morning_evening_distinct',sum(ImageStat.Stat(ImageChops.difference(morning,evening)).mean)>15)
        page.evaluate('Luna.cam.goto(4,false)');page.keyboard.press('c');check('ceo_toggle_on',page.evaluate('Luna.scene.ceo'));capture(page,'07-ceo-margin.png',32)
        page.keyboard.press('c');check('ceo_toggle_off',page.evaluate('!Luna.scene.ceo'))
        page.keyboard.press('f');check('fullscreen_on',page.evaluate('!!document.fullscreenElement'));page.keyboard.press('f')
        page.evaluate('Luna.cam.goto(2,false)');page.keyboard.press('e');check('editor_opens',page.locator('#editor').is_visible())
        for name in ['nord','olive','nocturne','terra','atelier']:
            page.locator('[data-theme="'+name+'"]').click();check('theme_'+name,page.evaluate('name=>Luna.scene.theme===name',name))
        page.evaluate('Luna.cam.view("wide")');capture(page,'08-live-atelier.png',32)
        point=page.evaluate('Luna.cam.project([.05,.948,.65])');before=page.evaluate('Luna.qa.center("island")')
        page.mouse.move(point['x'],point['y']);page.mouse.down();page.mouse.move(point['x']-100,point['y']+12,steps=12);page.mouse.up()
        check('pointer_selects_island',page.evaluate('Luna.editor.selected==="island"'))
        after=page.evaluate('Luna.qa.center("island")');check('pointer_drag_moves_geometry',abs(after[0]-before[0])+abs(after[2]-before[2])>.05)
        page.locator('#undo').click();check('undo_drag',sum(abs(a-b) for a,b in zip(page.evaluate('Luna.qa.center("island")'),before))<.002)
        page.locator('#redo').click();check('redo_drag',sum(abs(a-b) for a,b in zip(page.evaluate('Luna.qa.center("island")'),after))<.002)
        page.locator('#pos-x').fill('450');page.locator('#pos-x').press('Tab');check('millimetre_position',abs(page.evaluate('Luna.qa.center("island")[0]')-.45)<.002)
        page.locator('#size-x').fill('3100');page.locator('#size-x').press('Tab');check('width_changes_geometry',page.evaluate('Math.abs(Luna.scene.group("island").bounds.size[0]*Luna.scene.group("island").scale[0]-3.1)<.002'))
        page.locator('#rotation').evaluate('(e)=>{e.value=15;e.dispatchEvent(new Event("input",{bubbles:true}));e.dispatchEvent(new Event("change",{bubbles:true}))}')
        check('rotation_changes_geometry',page.evaluate('Math.abs(Luna.scene.group("island").yaw-Math.PI/12)<.001'))
        page.locator('#surface-select').select_option('front');page.locator('[data-material="walnut"]').click();check('per_object_material',page.evaluate('Luna.scene.group("island").overrides.front.id==="walnut"'))
        page.locator('#surface-color').evaluate('(e)=>{e.value="#715a49";e.dispatchEvent(new Event("input",{bubbles:true}));e.dispatchEvent(new Event("change",{bubbles:true}))}')
        check('surface_colour',page.evaluate('Luna.scene.group("island").overrides.front.color==="#715a49"'))
        capture(page,'09-object-editing.png',32)
        fixture=QA/'test-texture.png';image=Image.new('RGB',(128,128),'#dbc49c');draw=ImageDraw.Draw(image)
        for x in range(0,128,16):draw.rectangle((x,0,x+3,127),fill='#624735')
        image.save(fixture);page.locator('#texture-file').set_input_files(str(fixture));page.wait_for_function('Luna.scene.group("island").overrides.front.id==="custom" && !!Luna.scene.customImage')
        check('custom_texture_import',page.evaluate('Luna.scene.customName==="test-texture.png"'))
        count=page.evaluate('Luna.scene.groups.filter(g=>!g.hidden).length');page.locator('#duplicate-object').click();check('duplicate',page.evaluate('Luna.scene.groups.filter(g=>!g.hidden).length')==count+1)
        page.locator('#delete-object').click();check('delete',page.evaluate('Luna.scene.groups.filter(g=>!g.hidden).length')==count)
        page.locator('#undo').click();check('undo_delete',page.evaluate('Luna.scene.groups.filter(g=>!g.hidden).length')==count+1);page.locator('#redo').click()
        page.locator('#tab-light').click()
        for name,value,expr in [('kelvin','3400','Luna.scene.kelvin===3400'),('light-power','130','Luna.scene.power===1.3'),('daylight','91','Luna.scene.sun===.91')]:
            page.locator('#'+name).evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}));e.dispatchEvent(new Event("change",{bubbles:true}))}',value);check('light_'+name,page.evaluate(expr))
        capture(page,'10-light-editing.png',32)
        page.locator('#tab-room').click()
        with page.expect_download(timeout=240000) as got:page.locator('#project-save').click()
        export=QA/'project-export.json';got.value.save_as(str(export));saved=json.loads(export.read_text());check('project_download',saved['schema']=='luna.stage.project' and bool(saved['customImage']))
        before_bad=page.evaluate('comparable(Luna.store.document())');bad=QA/'invalid-project.json';bad.write_text('{"schema":"wrong"}');page.locator('#project-file').set_input_files(str(bad));page.wait_for_timeout(200);check('invalid_import_is_atomic',page.evaluate('comparable(Luna.store.document())')==before_bad)
        page.locator('[data-theme="nord"]').click();page.locator('#project-file').set_input_files(str(export));page.wait_for_function('!!Luna.scene.customImage');check('project_roundtrip',page.evaluate('Luna.scene.theme')==saved['scene']['theme'])
        page.evaluate('Luna.store.write();Luna.scene.ceo=true')
        page.goto(url+'?paused=1',wait_until='domcontentloaded');wait_gpu(page);check('local_reload_retains_layout',abs(page.evaluate('Luna.qa.center("island")[0]')-.45)<.002);check('ceo_never_restored',page.evaluate('!Luna.scene.ceo'));check('reload_retains_imported_texture',page.evaluate('!!Luna.scene.customImage'))
        before_photo=page.evaluate('comparable(Luna.store.document())')
        with page.expect_download(timeout=240000) as got:page.keyboard.press('s')
        photo=QA/'STAGE-Berger-Abend.png';got.value.save_as(str(photo));im=Image.open(photo)
        check('snapshot_exact_1920_1080',im.size==(1920,1080));check('snapshot_contains_actual_room',min(ImageStat.Stat(im.convert('RGB')).stddev)>12);check('snapshot_preserves_document',before_photo==page.evaluate('comparable(Luna.store.document())'))
        page.evaluate('d=>{Luna.store.apply(d);Luna.scene.customImage=null;Luna.gpu.loadCustom();Luna.cam.time=0;Luna.cam.chapter=0;Luna.cam.playing=false;Luna.cam.toggle()}',pristine)
        start=time.monotonic();seen=set()
        while time.monotonic()-start<58:
            state=page.evaluate('({playing:Luna.cam.playing,chapter:Luna.cam.chapter,time:Luna.cam.time})');seen.add(state['chapter'])
            if not state['playing']:break
            page.wait_for_timeout(350)
        seconds=time.monotonic()-start;report['film_wall_seconds']=seconds;check('film_40_to_55_seconds',40<=seconds<=55);check('six_chapters_executed',len(seen)==6);check('film_lands_in_stille',state['chapter']==5 and not state['playing'])
        check('no_external_runtime_requests',not network);report['network']=network
        html=(ROOT/'Luna-Stage.html').read_text();report['prebake_source_sha256']=hashlib.sha256(html.encode()).hexdigest();html=re.sub(r'const embeddedStills=\[.*?\];','const embeddedStills='+json.dumps(stills,separators=(',',':'))+';',html,count=1,flags=re.S);(ROOT/'Luna-Stage.html').write_text(html)
        report['source_sha256']=hashlib.sha256(html.encode()).hexdigest();report['bytes']=len(html.encode());report['baked_fallback_frames']=6
        page.goto(url+'?backend=canvas2d&chapter=3&paused=1&fresh=1',wait_until='load');page.wait_for_function('Luna.gpu.backend==="Canvas2D" && document.body.classList.contains("fallback")');page.screenshot(path=str(OUT/'11-new-scene-fallback.png'))
        check('truthful_fallback_filmstrip',page.locator('#filmstrip').is_visible() and len(stills)==6)
        page.goto(url+'?chapter=3&paused=1&fresh=1',wait_until='domcontentloaded');wait_gpu(page);check('final_baked_source_native_gpu',page.evaluate('Luna.gpu.errors.length===0'))
        page.set_viewport_size({'width':390,'height':844});page.keyboard.press('e');capture(page,'12-mobile-editor.png',16)
        check('mobile_editor_inside_viewport',page.evaluate('(()=>{const r=document.getElementById("editor").getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight})()'))
        check('no_overflow',page.evaluate('document.documentElement.scrollWidth===innerWidth && document.documentElement.scrollHeight===innerHeight'))
        check('no_page_errors',not report['errors']);check('no_gpu_errors',page.evaluate('Luna.gpu.errors.length===0'))
        report['result']='PASS'
    except Exception as error:
        report['result']='FAIL';report['exception']=str(error);report['traceback']=traceback.format_exc()
        try:report['gpu_at_failure']=page.evaluate('window.Luna && Luna.qa.getState()');page.screenshot(path=str(OUT/'failure.png'),timeout=30000)
        except Exception:pass
        print(traceback.format_exc(),flush=True)
    finally:
        (QA/'acceptance-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True);browser.close();server.shutdown()
if report.get('result')!='PASS':raise SystemExit(1)
