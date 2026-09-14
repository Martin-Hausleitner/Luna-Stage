"""Polish native geometry, accelerate traversal, and capture stable GPU pixels."""
from pathlib import Path
root=Path(__file__).resolve().parents[2];p=root/'Luna-Stage.html';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a[:100]
 s=s.replace(a,b,1)
a=s.index('// Hand-thrown ceramics.');b=s.index('// Every leaf',a)
s=s[:a]+'''// A folded linen cloth next to the sink.
rounded([-1.62,.991,-2.10],[.11,.012,.08],.008,10,[.48,.52,.48]);
'''+s[b:]
a=s.index('function buildBVH(');b=s.index('buildBVH([...O]);',a)
s=s[:a]+r'''function buildBVH(items){
 const idx=nodes.length,lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];
 for(const o of items)for(let k=0;k<3;k++){lo[k]=Math.min(lo[k],o.c[k]-o.s[k]-.0001);hi[k]=Math.max(hi[k],o.c[k]+o.s[k]+.0001)}
 const n={lo,hi,first:-1,end:0};nodes.push(n);
 if(items.length===1){n.first=ordered.length;ordered.push(items[0]);}
 else{
  const area=(a,b)=>{let x=Math.max(0,b[0]-a[0]),y=Math.max(0,b[1]-a[1]),z=Math.max(0,b[2]-a[2]);return x*y+x*z+y*z};
  let score=Infinity,left=null,right=null;
  for(let axis=0;axis<3;axis++){
   const sorted=[...items].sort((a,b)=>a.c[axis]-b.c[axis]);const prefix=[];let l=[Infinity,Infinity,Infinity],h=[-Infinity,-Infinity,-Infinity];
   for(let i=0;i<sorted.length;i++){let o=sorted[i];for(let k=0;k<3;k++){l[k]=Math.min(l[k],o.c[k]-o.s[k]);h[k]=Math.max(h[k],o.c[k]+o.s[k])}prefix.push(area(l,h)*(i+1))}
   l=[Infinity,Infinity,Infinity];h=[-Infinity,-Infinity,-Infinity];
   for(let i=sorted.length-1;i>0;i--){let o=sorted[i];for(let k=0;k<3;k++){l[k]=Math.min(l[k],o.c[k]-o.s[k]);h[k]=Math.max(h[k],o.c[k]+o.s[k])}let c=prefix[i-1]+area(l,h)*(sorted.length-i);if(c<score){score=c;left=sorted.slice(0,i);right=sorted.slice(i)}}
  }
  buildBVH(left);buildBVH(right);
 }
 n.end=nodes.length;return idx;
}
'''+s[b:]
rep("fn rand(k:f32)->vec2f{if(u.right.w>.5){return vec2f(.5);}return vec2f(hash(seed+vec3f(k,17,31)),hash(seed+vec3f(41,k,73)));}","fn rand(k:f32)->vec2f{if(u.right.w>.5){return vec2f(.5);}let frame=u.state.w+1.;return fract(vec2f(frame*.754877666+k*.61803399,frame*.569840296+k*.41421356));}")
rep("for(var guard=0u;guard<16384u;guard++)", "for(var guard=0u;guard<arrayLength(&tree);guard++)")
a=s.index('Luna.gpu.captureFrame=');b=s.index('function tick(now)',a)
s=s[:a]+r'''
Luna.gpu.captureFrame=async(samples=16,w=1920,h=1080)=>{
 const old=Luna.gpu.snapshotBusy;Luna.gpu.snapshotBusy=true;
 try{
  await Luna.gpu.wait();for(let i=0;i<samples;i++){Luna.gpu.render(w,h);await Luna.gpu.wait();}
  const image=device.createTexture({size:[w,h],format,usage:GPUTextureUsage.RENDER_ATTACHMENT|GPUTextureUsage.COPY_SRC});
  const pitch=Math.ceil(w*4/256)*256,buf=device.createBuffer({size:pitch*h,usage:GPUBufferUsage.COPY_DST|GPUBufferUsage.MAP_READ});
  const enc=device.createCommandEncoder(),pass=enc.beginRenderPass({colorAttachments:[{view:image.createView(),loadOp:'clear',storeOp:'store'}]});
  pass.setPipeline(presentPipeline);pass.setBindGroup(0,presentGroups[sampleCount%2]);pass.draw(3);pass.end();
  enc.copyTextureToBuffer({texture:image},{buffer:buf,bytesPerRow:pitch,rowsPerImage:h},[w,h]);device.queue.submit([enc.finish()]);await buf.mapAsync(GPUMapMode.READ);
  const raw=new Uint8Array(buf.getMappedRange()),rgba=new Uint8ClampedArray(w*h*4);for(let y=0;y<h;y++)rgba.set(raw.subarray(y*pitch,y*pitch+w*4),y*w*4);
  if(format.startsWith('bgra'))for(let i=0;i<rgba.length;i+=4){const t=rgba[i];rgba[i]=rgba[i+2];rgba[i+2]=t}
  buf.unmap();buf.destroy();image.destroy();const c=document.createElement('canvas');c.width=w;c.height=h;c.getContext('2d').putImageData(new ImageData(rgba,w,h),0,0);return c.toDataURL('image/png');
 }finally{Luna.gpu.snapshotBusy=old}
};
'''+s[b:]
rep("Luna.gpu.version='3.0-detail'", "Luna.gpu.version='3.1-detail'")
p.write_text(s)
print('Polished runtime',len(s.encode()))
