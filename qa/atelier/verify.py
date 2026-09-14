"""Compare actual GPU readback with native canvas screenshot; bounded to a few frames."""
from pathlib import Path
import base64,functools,http.server,json,threading,traceback
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];QA=ROOT/'qa/atelier';OUT=QA/'screenshots';OUT.mkdir(exist_ok=True)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/Luna-Stage.html'
report={}
with sync_playwright() as p:
    from gpu_probe import select_browser
    browser=p.chromium.launch(**select_browser(p,QA,url.rsplit('/',1)[0]))
    page=browser.new_page(viewport={'width':1920,'height':1080})
    page.on('console',lambda m:print('CONSOLE',m.type,m.text,flush=True))
    page.on('pageerror',lambda e:print('ERROR',e,flush=True))
    try:
        page.goto(url+'?chapter=3&paused=1&fresh=1',wait_until='domcontentloaded');page.wait_for_function("window.Luna && (Luna.gpu.firstGPUMS || document.body.classList.contains('fallback'))",timeout=60000)
        report['state']=page.evaluate('Luna.qa.getState()');print('STATE',json.dumps(report['state']),flush=True)
        report['numbers']=page.evaluate('({basis:Luna.cam.basis(),eye:Luna.cam.eye,to:Luna.cam.to,first:Luna.scene.objects[0],kelvin:kelvinRGB(Luna.scene.kelvin),lightData})')
        result=page.evaluate('''async()=>{busy=true;await Luna.gpu.pending;Luna.cam.stop();const image=await Luna.gpu.readPixels(640,360,1);busy=true;const c=document.createElement('canvas');c.width=640;c.height=360;c.getContext('2d').putImageData(image,0,0);return {png:c.toDataURL('image/png').split(',')[1],pixels:Array.from(image.data.slice((180*640+320)*4,(180*640+320)*4+4))}}''')
        (OUT/'gpu-readback.png').write_bytes(base64.b64decode(result.pop('png')));report['readback']=result;print('READBACK',result,flush=True)
        page.screenshot(path=str(OUT/'native-canvas.png'))
        page.evaluate('''async()=>{const code='@vertex fn vs(@builtin(vertex_index) i:u32)->@builtin(position) vec4f{var p=array<vec2f,3>(vec2f(-1,-1),vec2f(3,-1),vec2f(-1,3));return vec4f(p[i],0,1);}@fragment fn fs()->@location(0) vec4f{return vec4f(.2,.4,.6,1);}';const m=device.createShaderModule({code});const pp=await device.createRenderPipelineAsync({layout:'auto',vertex:{module:m,entryPoint:'vs'},fragment:{module:m,entryPoint:'fs',targets:[{format}]}});const encoder=device.createCommandEncoder();const pass=encoder.beginRenderPass({colorAttachments:[{view:context.getCurrentTexture().createView(),loadOp:'clear',storeOp:'store'}]});pass.setPipeline(pp);pass.draw(3);pass.end();device.queue.submit([encoder.finish()]);await device.queue.onSubmittedWorkDone();}''')
        page.screenshot(path=str(OUT/'flat-compositor.png'));report['result']='DIAGNOSTIC COMPLETE'
    except Exception as e:report['error']=str(e);report['traceback']=traceback.format_exc();print(traceback.format_exc(),flush=True)
    finally:(QA/'diagnostic.json').write_text(json.dumps(report,indent=2));browser.close();server.shutdown()
if report.get('error'):raise SystemExit(1)
