"""Rebuild the standalone runtime offline from final reviewed sources and embedded assets."""
from pathlib import Path
import base64,hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'qa/atelier';SRC=QA/'src'
receipts=json.loads((QA/'assets.json').read_text())
assets={}
for layer,name in [(1,'Wood094'),(2,'Travertine003')]:
    data=(QA/(name+'.webp')).read_bytes()
    receipt=next(r for r in receipts if r['asset']==name)
    if hashlib.sha256(data).hexdigest()!=receipt['packed_sha256']:raise ValueError('Asset checksum failed: '+name)
    assets[str(layer)]={'name':name,'data':'data:image/webp;base64,'+base64.b64encode(data).decode()}
stills=json.loads((QA/'embedded-stills.json').read_text())
code='\n'.join((SRC/n).read_text() for n in ['scene.js','state-camera.js','geometry-gpu.js','renderer.js','interface.js','input-boot.js'])
code=code.replace('/*PRESENT_SHADER*/',json.dumps((SRC/'present.wgsl').read_text())).replace('/*STILLS*/',json.dumps(stills,separators=(',',':'))).replace('/*MATERIAL_ASSETS*/',json.dumps(assets,separators=(',',':')))
html=(SRC/'shell.html').read_text().replace('/*CSS*/',(SRC/'style.css').read_text()).replace('/*CODE*/',code)
encoded=html.encode();actual=hashlib.sha256(encoded).hexdigest()
record=QA/'release-integrity.json'
if record.exists():
    expected=json.loads(record.read_text())['runtime_sha256']
    if actual!=expected:raise ValueError('Rebuild differs from reviewed runtime: '+actual+' != '+expected)
(ROOT/'Luna-Stage.html').write_bytes(encoded)
print(json.dumps({'runtime_sha256':actual,'bytes':len(encoded),'offline_rebuild':'PASS'},indent=2))
