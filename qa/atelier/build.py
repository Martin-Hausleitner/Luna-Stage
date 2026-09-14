"""Development-only one-file packer. Runtime never fetches assets."""
from pathlib import Path
import base64, hashlib, io, json, re, runpy, urllib.request, zipfile
from PIL import Image, ImageStat
ROOT = Path(__file__).resolve().parents[2]
QA = ROOT / 'qa/atelier'
SRC = QA / 'src'
EXPECTED = {
'state-camera.js':'32d5c6ec4259bfa38bfc4e9ec1baf16b41249ddf81eafa1cb3ebe3ad7246719a',
'style.css':'228da2c4cc9d64974d25220450aaf355f8e94a8c11b2eb5b0c98fc08379bf712',
'shell.html':'c671e5743515562a9e065fc234e6ae6eb01bc59369454e5fbab5907b6a3b5280',
'interface.js':'c6c52107a3614723d1cd917eee911af02c59d2170600d9bd4fa2eda06f423d2e',
'present.wgsl':'f2ba1bb5392ed1f4473b25e2f95713d3c862784d0a786aa501a371e962494373',
'geometry-gpu.js':'a8d1e469983edd69348c6b4b952ad10b1256ef5cb6683725c78deada8da19e9d',
'input-boot.js':'c02acd6578202d33094aabaa241130bfd527f46b5859a1e98dae35658851ba0c',
'scene.js':'0085837e225e5c84f3a8358de287ad226e6ad209ef95aa205e71ff8446a9f228',
'room.wgsl':'88d4b5c4ef1ad8ca0318fa2be688a7ffde8fb23e17eb1417703a7f71b8417264',
'renderer.js':'a80458cdf041b2b44edf55574f94be9a7bb119eee3a9de15c957c6f90d723ee3'}
for name, digest in EXPECTED.items():
    actual = hashlib.sha256((SRC/name).read_bytes()).hexdigest()
    print('SOURCE', name, actual, flush=True)
    if actual != digest:
        raise ValueError('Transferred source differs: '+name)
base=(ROOT/'Luna-Stage.html').read_text()
stills=re.search(r'const embeddedStills=(\[.*?\]);',base,re.S).group(1)
if (QA/'fixes.py').exists():
    runpy.run_path(str(QA/'fixes.py'),init_globals={'SRC':SRC,'ROOT':ROOT,'QA':QA})
assets={}
receipts=[]
for layer, name in [(1,'Wood094'),(2,'Travertine003')]:
    url='https://ambientcg.com/get?file='+name+'_1K-JPG.zip'
    receipt={'asset':name,'source':'https://ambientcg.com/view?id='+name,'license':'CC0-1.0','status':'unavailable'}
    try:
        request=urllib.request.Request(url,headers={'User-Agent':'LunaStage/2.0 asset packer'})
        with urllib.request.urlopen(request,timeout=40) as response:
            data=response.read(32*1024*1024)
        archive=zipfile.ZipFile(io.BytesIO(data))
        colors=[n for n in archive.namelist() if n.lower().endswith('_color.jpg')]
        heights=[n for n in archive.namelist() if '_displacement.' in n.lower()]
        if not colors:raise ValueError('No color map in source archive')
        color=Image.open(io.BytesIO(archive.read(colors[0]))).convert('RGB').resize((512,512),Image.Resampling.LANCZOS)
        # Preserve the source grain/veins; normalize the mean so live tint remains useful.
        channels=[]
        for channel, mean in zip(color.split(),ImageStat.Stat(color).mean):
            lut=[min(255,max(0,round(184+(v-mean)*.72))) for v in range(256)]
            channels.append(channel.point(lut))
        height=Image.open(io.BytesIO(archive.read(heights[0]))).convert('L').resize((512,512),Image.Resampling.LANCZOS) if heights else color.convert('L')
        height=height.point([round(112+v*.125) for v in range(256)])
        rgba=Image.merge('RGBA',(*channels,height))
        out=io.BytesIO();rgba.save(out,'WEBP',quality=86,method=6)
        packed=out.getvalue()
        assets[str(layer)]={'name':name,'data':'data:image/webp;base64,'+base64.b64encode(packed).decode()}
        (QA/(name+'.webp')).write_bytes(packed)
        receipt.update(status='embedded',zip_sha256=hashlib.sha256(data).hexdigest(),packed_sha256=hashlib.sha256(packed).hexdigest(),packed_bytes=len(packed),color_file=colors[0],height_file=heights[0] if heights else None)
    except Exception as error:
        receipt['error']=str(error)
        print('ASSET WARNING',name,str(error),flush=True)
    receipts.append(receipt)
(QA/'assets.json').write_text(json.dumps(receipts,indent=2))
code='\n'.join((SRC/n).read_text() for n in ['scene.js','state-camera.js','geometry-gpu.js','renderer.js','interface.js','input-boot.js'])
code=code.replace('/*ROOM_SHADER*/',json.dumps((SRC/'room.wgsl').read_text())).replace('/*PRESENT_SHADER*/',json.dumps((SRC/'present.wgsl').read_text())).replace('/*STILLS*/',stills).replace('/*MATERIAL_ASSETS*/',json.dumps(assets,separators=(',',':')))
html=(SRC/'shell.html').read_text().replace('/*CSS*/',(SRC/'style.css').read_text()).replace('/*CODE*/',code)
(ROOT/'Luna-Stage.html').write_text(html)
(QA/'check.js').write_text(code)
metadata={'sha256':hashlib.sha256(html.encode()).hexdigest(),'bytes':len(html.encode()),'assets':receipts,'sources':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SRC.iterdir() if p.is_file()}}
(QA/'build.json').write_text(json.dumps(metadata,indent=2))
print(json.dumps(metadata,indent=2),flush=True)
