"""Development-only graphics preflight. Checks a completed canvas render and readback."""
import json, os, shutil, subprocess, time
from pathlib import Path

TEST='''async()=>{
if(!navigator.gpu)return {ok:false,error:'WebGPU missing'};
const adapter=await navigator.gpu.requestAdapter();if(!adapter)return {ok:false,error:'Adapter missing'};
const device=await adapter.requestDevice();let lost=null;device.lost.then(i=>lost=i.message);
try{
const canvas=document.querySelector('canvas');canvas.width=1920;canvas.height=1080;
const context=canvas.getContext('webgpu'),format=navigator.gpu.getPreferredCanvasFormat();
context.configure({device,format,alphaMode:'opaque',usage:GPUTextureUsage.RENDER_ATTACHMENT|GPUTextureUsage.COPY_SRC});
const texture=context.getCurrentTexture(),encoder=device.createCommandEncoder();
const pass=encoder.beginRenderPass({colorAttachments:[{view:texture.createView(),loadOp:'clear',storeOp:'store',clearValue:{r:.2,g:.4,b:.6,a:1}}]});pass.end();
const buf=device.createBuffer({size:256,usage:GPUBufferUsage.COPY_DST|GPUBufferUsage.MAP_READ});
encoder.copyTextureToBuffer({texture},{buffer:buf,bytesPerRow:256},[1,1]);device.queue.submit([encoder.finish()]);
await Promise.race([buf.mapAsync(GPUMapMode.READ),new Promise((_,r)=>setTimeout(()=>r(Error('Render timeout')),6000))]);
const pixel=Array.from(new Uint8Array(buf.getMappedRange()).slice(0,4));buf.unmap();buf.destroy();
return {ok:!lost&&pixel[3]===255&&pixel.slice(0,3).reduce((a,b)=>a+b,0)>200,pixel,format,adapter:{vendor:adapter.info.vendor,architecture:adapter.info.architecture},lost};
}catch(e){return {ok:false,error:e.message,lost};}finally{device.destroy();}
}'''

def select_browser(playwright,qa,origin):
    probe=qa.parents[1]/'gpu-probe.html';probe.write_text('<!doctype html><title>GPU presentation probe</title><canvas></canvas>')
    executable=shutil.which('google-chrome')
    common=['--no-sandbox','--enable-unsafe-webgpu','--disable-dev-shm-usage','--disable-gpu-watchdog']
    variants=[
        ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'],
        ['--use-gl=angle','--use-angle=vulkan','--use-vulkan=swiftshader','--enable-features=Vulkan','--disable-vulkan-surface'],
        ['--use-gl=angle','--use-angle=swiftshader','--use-vulkan=swiftshader','--enable-features=Vulkan','--disable-vulkan-surface'],
        [],
        ['--use-gl=angle','--use-angle=vulkan','--use-vulkan=swiftshader','--enable-features=Vulkan']
    ]
    results=[]
    for headless in [True,False]:
        if not headless:
            if not shutil.which('Xvfb'):continue
            subprocess.Popen(['Xvfb',':99','-screen','0','1920x1080x24','-nolisten','tcp'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            os.environ['DISPLAY']=':99';time.sleep(.8)
        for extra in variants:
            config={'headless':headless,'args':common+extra}
            if executable:config['executable_path']=executable
            browser=None
            try:
                browser=playwright.chromium.launch(**config)
                page=browser.new_page(viewport={'width':1920,'height':1080})
                page.goto(origin+'/gpu-probe.html',wait_until='domcontentloaded',timeout=20000)
                result=page.evaluate(TEST);result['config']=config
                print('CANVAS PROBE',json.dumps(result),flush=True);results.append(result)
                if result.get('ok'):
                    (qa/'gpu-probe.json').write_text(json.dumps(results,indent=2));return config
            except Exception as e:
                results.append({'ok':False,'config':config,'error':str(e)})
            finally:
                if browser:browser.close()
    (qa/'gpu-probe.json').write_text(json.dumps(results,indent=2))
    raise RuntimeError('No tested browser configuration completed a native WebGPU canvas render; see gpu-probe.json')
