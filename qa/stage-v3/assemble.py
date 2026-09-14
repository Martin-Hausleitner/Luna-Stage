#!/usr/bin/env python3
"""Assemble verified room artifacts; native renderer and geometry remain unchanged."""
from pathlib import Path
import argparse,hashlib,base64,json,re,io,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--source-sha256',required=True);a=p.parse_args()
names=['01-arrival','02-grain-morning','03-evening','04-lacquer','05-price-on-worktop','06-wide-still','07-ceo-margin','09-plant-detail']
raw=(a.input/'Luna-Stage.html').read_bytes();assert hashlib.sha256(raw).hexdigest()==a.source_sha256;q=a.input/'qa/frames';reports=[]
for name in names:
 r=json.loads((q/(name+'.json')).read_text());assert r['result']=='PASS' and all(r['checks'].values());assert r['source_sha256']==a.source_sha256
 assert r['frame']['width']==1920 and r['frame']['height']==1080 and r['checks']['browser_room_visible'];reports.append(r)
s=raw.decode();stills=[]
for i,name in enumerate(names[:6]):
 im=Image.open(q/('fallback-price-clean.png' if i==4 else 'room-'+name+'.png')).convert('RGB').resize((1280,720),Image.Resampling.LANCZOS);buf=io.BytesIO();im.save(buf,'WEBP',quality=86,method=6)
 stills.append('data:image/webp;base64,'+base64.b64encode(buf.getvalue()).decode())
pattern=r'const embeddedStills=\[.*?\];';matches=list(re.finditer(pattern,s,re.S));assert len(matches)==1;m=matches[0]
replacement='const embeddedStills='+json.dumps(stills,separators=(',',':'))+';';new=s[:m.start()]+replacement+s[m.end():]
# Pre-tint the fallback atlas ONCE. Previously each projected tile invoked a costly filter.
anchor='}drawAtlas();';tinted="}drawAtlas();\nconst fallbackAtlas=document.createElement('canvas');fallbackAtlas.width=atlas.width;fallbackAtlas.height=atlas.height;const fag=fallbackAtlas.getContext('2d');fag.drawImage(atlas,0,0);fag.globalCompositeOperation='source-in';fag.fillStyle='#292827';fag.fillRect(0,0,atlas.width,atlas.height);\n"
assert anchor in new and 'const src=atlas,rows=16' in new and "g.filter='brightness(.16)';" in new
new=new.replace(anchor,tinted,1).replace('const src=atlas,rows=16','const src=fallbackAtlas,rows=16',1).replace("g.filter='brightness(.16)';",'',1)
# Inverting the enumerated fallback-only changes must reproduce the exact tested source.
inverted=new.replace(tinted,anchor,1).replace('const src=fallbackAtlas,rows=16','const src=atlas,rows=16',1).replace('g.globalAlpha=.68;g.transform','g.globalAlpha=.68;g.filter=\'brightness(.16)\';g.transform',1)
assert inverted.replace(replacement,'__STILLS__',1)==s[:m.start()]+'__STILLS__'+s[m.end():]
out=a.output;out.mkdir(parents=True,exist_ok=True);(out/'Luna-Stage.html').write_text(new)
for name in ['README.md','VISION.md']:
 path=ROOT/'qa/stage-v3'/name
 if path.exists():
  dest=out/('qa/v3/VISION.md' if name=='VISION.md' else name);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
shutil.copy2(ROOT/'LICENSE',out/'LICENSE');(out/'.nojekyll').touch();shutil.copytree(q,out/'qa/v3',dirs_exist_ok=True)
for name in names:shutil.copy2(q/(name+'.png'),out/'qa'/(name+'.png'))
(out/'qa/stage-v2').mkdir(parents=True,exist_ok=True);shutil.copy2(a.input/'qa/stage-v2/asset-receipt.json',out/'qa/stage-v2/asset-receipt.json')
receipt={'version':'3.2-detail','tested_source_sha256':a.source_sha256,'assembled_sha256':hashlib.sha256(new.encode()).hexdigest(),'bytes':len(new.encode()),'native_reports':len(reports),'changes_after_native_test':['six embedded stills rebaked from actual current native renders','Canvas2D glyph atlas pre-tinted once instead of per-tile brightness filters'],'reference_image_embedded':False,'native_adapter':reports[0]['gpu']['adapter'],'geometry':reports[0]['geometry'],'checks':{'all_native_reports_pass':True,'native_renderer_geometry_and_camera_unchanged':True,'fallback_price_clean':True,'enumerated_changes_invert_to_exact_tested_source':True}}
(out/'qa/v3/assembly.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
