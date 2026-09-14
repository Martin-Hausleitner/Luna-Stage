from pathlib import Path
root=Path(__file__).resolve().parents[2];p=root/'Luna-Stage.html';s=p.read_text()
anchor='function tick(now)'
patch='''Luna.gpu.readPixels=async(w=1920,h=1080)=>{const img=new Image();img.src=await Luna.gpu.captureFrame(16,w,h);await img.decode();const c=document.createElement('canvas');c.width=w;c.height=h;const g=c.getContext('2d');g.drawImage(img,0,0);return g.getImageData(0,0,w,h)};
'''
assert anchor in s;s=s.replace(anchor,patch+anchor,1);p.write_text(s)
