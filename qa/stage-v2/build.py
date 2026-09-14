#!/usr/bin/env python3
"""Build STAGE 2.0 from a pinned source. Only this development step fetches assets."""
import argparse,base64,hashlib,io,json,subprocess,time,urllib.request
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
BASE='c2235c89ffb654520201978ef7b8eafefcd3b22e'
p=argparse.ArgumentParser();p.add_argument('--offline',action='store_true');args=p.parse_args()
try: raw=subprocess.check_output(['git','show',BASE+':Luna-Stage.html'],cwd=ROOT,stderr=subprocess.DEVNULL)
except (subprocess.CalledProcessError,FileNotFoundError): raw=(ROOT/'Luna-Stage.html').read_bytes()
if hashlib.sha256(raw).hexdigest()!='17e052f77651eace4c663a23bd2aa39fecd9e6249df100d318e0142a0b0ca5f8': raise SystemExit('Unexpected baseline; restore the pinned source first.')
s=raw.decode('utf-8')
def replace(old,new):
 global s
 if old not in s: raise RuntimeError('Missing patch anchor: '+old[:100])
 s=s.replace(old,new,1)
assets=[
 ('oak','https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/oak_veneer_01/oak_veneer_01_diff_1k.jpg',(1024,1024)),
 ('normal','https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/oak_veneer_01/oak_veneer_01_nor_gl_1k.jpg',(1024,1024)),
 ('environment','https://dl.polyhaven.org/file/ph-assets/HDRIs/extra/Tonemapped%20JPG/venice_sunset.jpg',(2048,1024))]
embedded={};receipt=[]
for name,url,size in assets:
 cache=HERE/(name+'.jpg')
 if not args.offline:
  if not cache.exists():
   for attempt in range(3):
    try:
     req=urllib.request.Request(url,headers={'User-Agent':'Luna-Stage-build/2.0 (single-file CC0 asset embedding)'})
     with urllib.request.urlopen(req,timeout=90) as response: cache.write_bytes(response.read())
     break
    except Exception:
     if attempt==2: raise
     time.sleep(2+attempt*2)
  data=cache.read_bytes();im=Image.open(io.BytesIO(data)).convert('RGB').resize(size,Image.Resampling.LANCZOS)
  receipt.append({'name':name,'source':url,'source_sha256':hashlib.sha256(data).hexdigest(),'license':'CC0-1.0','size':list(size)})
 else:
  im=Image.new('RGB',size,(170,130,85) if name=='oak' else (128,128,255) if name=='normal' else (125,150,172))
  if name=='oak':
   d=ImageDraw.Draw(im)
   for x in range(0,1024,3): d.line((x,0,x+3,1024),fill=(135+x%27,99+x%23,58+x%19),width=1)
  receipt.append({'name':name,'development_placeholder':True,'size':list(size)})
 out=io.BytesIO();im.save(out,'WEBP',quality=88 if name!='normal' else 93,method=6)
 embedded[name]='data:image/webp;base64,'+base64.b64encode(out.getvalue()).decode()
 receipt[-1]['embedded_sha256']=hashlib.sha256(out.getvalue()).hexdigest()
a=s.index('const O=Luna.scene.objects;');b=s.index('Luna.scene.bounds=',a)
s=s[:a]+(HERE/'scene.js').read_text()+'\n'+s[b:]
a=s.index('const shader=`');b=s.index('const presentShader=',a)
s=s[:a]+'const shader=`\n'+(HERE/'room.wgsl').read_text()+'\n`;\n'+s[b:]
replace('</style>',(HERE/'style.css').read_text()+'\n</style>')
replace('LUNA STAGE 1.0','LUNA STAGE 2.0')
replace('material:o.material===1?1:0','material:Number.isInteger(o.material)?clamp(o.material,0,5):0')
replace('...o.col,o.shadow]','...o.col,o.shadow,...(o.extra||[0,0,0,.004])]')
replace('Luna.gpu.targetSamples=28','Luna.gpu.targetSamples=64')
replace('...b.r,0,...b.u,0,w,h','...b.r,(Luna.cam.playing||Luna.cam.shotPlaying||!!Luna.cam.transition)?1:0,...b.u,Math.hypot(...V.sub(Luna.cam.to,Luna.cam.eye)),w,h')
replace('moving?.77','moving?.72')
replace('Luna.cam.playing||!!Luna.cam.transition||performance.now()-settleAt<130','Luna.cam.playing||Luna.cam.shotPlaying||!!Luna.cam.transition||performance.now()-settleAt<130')
replace('let moving=false;if(Luna.cam.playing','let moving=Luna.cam.advanceShot?Luna.cam.advanceShot(dt,now):false;if(Luna.cam.playing')
replace('if(hit.object?.m===2)Luna.scene.cycle();else if(hit.object?.m===3)','if(hit.object?.swatch!==undefined)Luna.scene.selectMaterial(hit.object.swatch);else if(hit.object?.m===2||hit.object?.m===12)Luna.scene.cycle();else if(hit.object?.m===3)')
replace('for(let i=0;i<32;i++)Luna.gpu.render(w,h);','for(let i=0;i<48;i++){Luna.gpu.render(w,h);if(i%4===3)await device.queue.onSubmittedWorkDone();}')
replace('r*Math.sin(phi)*Math.cos(theta)]);Luna.hud.sync()', 'r*Math.sin(phi)*Math.cos(theta)]).map((v,k)=>clamp(v,[-3.03,.24,-1.75][k],[4.20,3.07,8][k]));Luna.hud.sync()')
asset_js='''
const embeddedAssets=__ASSETS__;
Luna.gpu.assetReceipt=__RECEIPT__;
Luna.gpu.loadAssets=async(device)=>{
 const decode=src=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(Error('Embedded material decode failed'));im.src=src});
 const images=await Promise.all([decode(embeddedAssets.oak),decode(embeddedAssets.normal),decode(embeddedAssets.environment)]);
 const upload=(ims,width,height)=>{const levels=1+Math.floor(Math.log2(Math.max(width,height)));const tex=device.createTexture({size:[width,height,ims.length],mipLevelCount:levels,format:'rgba8unorm',usage:GPUTextureUsage.TEXTURE_BINDING|GPUTextureUsage.COPY_DST|GPUTextureUsage.RENDER_ATTACHMENT});for(let layer=0;layer<ims.length;layer++){let w=width,h=height;for(let level=0;level<levels;level++){const c=document.createElement('canvas');c.width=w;c.height=h;const g=c.getContext('2d');g.imageSmoothingQuality='high';g.drawImage(ims[layer],0,0,w,h);device.queue.copyExternalImageToTexture({source:c},{texture:tex,mipLevel:level,origin:[0,0,layer]},[w,h]);w=Math.max(1,w>>1);h=Math.max(1,h>>1);}}return tex;};
 const material=upload(images.slice(0,2),1024,1024),env=upload([images[2]],2048,1024);
 const data=new Float32Array(Luna.scene.bvh.flatMap(n=>[...n.lo,n.first,...n.hi,n.end]));const bvh=device.createBuffer({size:data.byteLength,usage:GPUBufferUsage.STORAGE|GPUBufferUsage.COPY_DST});device.queue.writeBuffer(bvh,0,data);
 Luna.gpu.materialsLoaded=true;Luna.gpu.acceleration='stackless BVH';
 return [{binding:5,resource:{buffer:bvh}},{binding:6,resource:material.createView({dimension:'2d-array'})},{binding:7,resource:device.createSampler({magFilter:'linear',minFilter:'linear',mipmapFilter:'linear',addressModeU:'repeat',addressModeV:'repeat',maxAnisotropy:4})},{binding:8,resource:env.createView()}];
};
'''.replace('__ASSETS__',json.dumps(embedded,separators=(',',':'))).replace('__RECEIPT__',json.dumps(receipt,separators=(',',':')))
replace('const shader=`',asset_js+'\nconst shader=`')
replace("Luna.gpu.ready=true;Luna.gpu.backend='WebGPU'","staticEntries.push(...await Luna.gpu.loadAssets(device));Luna.gpu.ready=true;Luna.gpu.backend='WebGPU'")
replace('function tick(now){',(HERE/'cinema.js').read_text()+'\nfunction tick(now){')
replace('rgb*.99','rgb*1.06')
replace('color*(1.-.08*dot(uv,uv))','color*(1.-.045*dot(uv,uv))')
a=s.index('Luna.scene.pick=');b=s.index('\nLuna.scene.cycle=',a)
pick='''function hitPrimitive(ro,rd,o){const boxT=hitBox(ro,rd,o);if(!Number.isFinite(boxT))return Infinity;const p=V.sub(ro,o.c);if(o.type===1){const q=p.map((v,k)=>v/o.s[k]),d=rd.map((v,k)=>v/o.s[k]),a=V.dot(d,d),b=V.dot(q,d),h=b*b-a*(V.dot(q,q)-1);return h>=0&&(-b-Math.sqrt(h))/a>.0004?(-b-Math.sqrt(h))/a:Infinity}if(o.type===3){const ba=V.mul(o.extra.slice(0,3),2),pa=V.add(p,o.extra.slice(0,3)),r=o.extra[3],baba=V.dot(ba,ba),bard=V.dot(ba,rd),bapa=V.dot(ba,pa),rdoa=V.dot(rd,pa),a=baba-bard*bard,b=baba*rdoa-bapa*bard,c=baba*V.dot(pa,pa)-bapa*bapa-r*r*baba,h=b*b-a*c;let best=Infinity;if(h>=0&&Math.abs(a)>1e-10){const t=(-b-Math.sqrt(h))/a,y=bapa+t*bard;if(t>.0004&&y>0&&y<baba)best=t}for(const sign of [-1,1]){const oc=V.sub(p,V.mul(o.extra.slice(0,3),sign)),bb=V.dot(rd,oc),hh=bb*bb-V.dot(oc,oc)+r*r;if(hh>=0){const t=-bb-Math.sqrt(hh);if(t>.0004)best=Math.min(best,t)}}return best}return boxT}
Luna.scene.pick=(x,y)=>{const ro=Luna.cam.eye,rd=Luna.cam.ray(x,y);let t=Infinity,id=-1;O.forEach((o,i)=>{const d=hitPrimitive(ro,rd,o);if(d<t){t=d;id=i}});return {id,t,point:V.add(ro,V.mul(rd,t)),object:O[id]}};'''
s=s[:a]+pick+s[b:]
(ROOT/'Luna-Stage.html').write_text(s)
(ROOT/'qa/stage-v2/asset-receipt.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps({'version':'2.0','bytes':len(s.encode()),'sha256':hashlib.sha256(s.encode()).hexdigest(),'photo_assets':not args.offline,'base':BASE},indent=2))
