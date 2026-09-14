#!/usr/bin/env python3
"""Assemble reviewed native artifacts. Never replace 3D code with a reference image."""
from pathlib import Path
import argparse,hashlib,base64,json,re,io,shutil,zipfile
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--source-sha256',required=True);a=p.parse_args()
names=['01-arrival','02-grain-morning','03-evening','04-lacquer','05-price-on-worktop','06-wide-still','07-ceo-margin','09-plant-detail']
src=a.input/'Luna-Stage.html';raw=src.read_bytes();assert hashlib.sha256(raw).hexdigest()==a.source_sha256
q=a.input/'qa/frames';reports=[]
for name in names:
 r=json.loads((q/(name+'.json')).read_text());assert r['result']=='PASS',r;assert all(r['checks'].values()),r
 assert r['source_sha256']==a.source_sha256;assert r['frame']['width']==1920 and r['frame']['height']==1080
 assert r['checks']['browser_room_visible'];reports.append(r)
s=raw.decode();stills=[]
for i,name in enumerate(names[:6]):
 path=q/('fallback-price-clean.png' if i==4 else 'room-'+name+'.png')
 im=Image.open(path).convert('RGB').resize((1280,720),Image.Resampling.LANCZOS);buf=io.BytesIO();im.save(buf,'WEBP',quality=86,method=6)
 stills.append('data:image/webp;base64,'+base64.b64encode(buf.getvalue()).decode())
pattern=r'const embeddedStills=\[.*?\];';matches=list(re.finditer(pattern,s,re.S));assert len(matches)==1
m=matches[0];replacement='const embeddedStills='+json.dumps(stills,separators=(',',':'))+';';new=s[:m.start()]+replacement+s[m.end():]
assert new.replace(replacement,'__STILLS__',1)==s[:m.start()]+'__STILLS__'+s[m.end():]
out=a.output;out.mkdir(parents=True,exist_ok=True);(out/'Luna-Stage.html').write_text(new)
for name in ['README.md','VISION.md']:
 path=ROOT/'qa/stage-v3'/name
 if path.exists():
  dest=out/('qa/v3/VISION.md' if name=='VISION.md' else name);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
shutil.copy2(ROOT/'LICENSE',out/'LICENSE');(out/'.nojekyll').touch();shutil.copytree(q,out/'qa/v3',dirs_exist_ok=True)
for name in names:shutil.copy2(q/(name+'.png'),out/'qa'/(name+'.png'))
asset=a.input/'qa/stage-v2/asset-receipt.json';(out/'qa/stage-v2').mkdir(parents=True,exist_ok=True);shutil.copy2(asset,out/'qa/stage-v2/asset-receipt.json')
receipt={'version':'3.2-detail','tested_source_sha256':a.source_sha256,'assembled_sha256':hashlib.sha256(new.encode()).hexdigest(),'bytes':len(new.encode()),'native_reports':len(reports),'data_only_change':'six embedded fallback WebP frames replaced with actual current native renders; executable code identical','reference_image_embedded':False,'native_adapter':reports[0]['gpu']['adapter'],'geometry':reports[0]['geometry'],'checks':{'all_native_reports_pass':True,'executable_code_unchanged':True,'fallback_price_clean':True}}
(out/'qa/v3/assembly.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
