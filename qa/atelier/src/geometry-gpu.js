/* Affine analytic primitives + a CPU-built BVH. Non-uniform group scale is exact, including tilted chair legs. */
let device,context,pipeline,presentPipeline,uniform,objectBuffer,nodeBuffer,lightBuffer,format,staticEntries=[],histories=[],groupsGPU=[],presentGroups=[],historySize='',stateKey='',sampleCount=0,lastSurface,atlasTexture,materialTexture,materialSampler,uploadRevision=-1;
let sortedObjects=[],bvhNodes=[],lightData=[],raf=0,lastFrame=0,dirty=true,settleAt=0,busy=false,gpuInFlight=false;
function local(o,p,dir=false){const d=dir?p:V.sub(p,o.c);return o.rows.map(r=>V.dot(r,d))}
function boxNear(ro,rd,lo,hi){let tn=-Infinity,tf=Infinity;for(let i=0;i<3;i++){if(Math.abs(rd[i])<1e-9){if(ro[i]<lo[i]||ro[i]>hi[i])return Infinity;continue}let a=(lo[i]-ro[i])/rd[i],b=(hi[i]-ro[i])/rd[i];tn=Math.max(tn,Math.min(a,b));tf=Math.min(tf,Math.max(a,b))}return tf>=Math.max(tn,.0001)?Math.max(0,tn):Infinity}
function intersectCPU(ro,rd,o){const p=local(o,ro),d=local(o,rd,true);if(o.type===0){let tn=-Infinity,tf=Infinity;for(let i=0;i<3;i++){if(Math.abs(d[i])<1e-9){if(Math.abs(p[i])>1)return Infinity;continue}const a=(-1-p[i])/d[i],b=(1-p[i])/d[i];tn=Math.max(tn,Math.min(a,b));tf=Math.min(tf,Math.max(a,b))}return tf>=Math.max(tn,.0001)?(tn>.0001?tn:tf):Infinity}
if(o.type===1){const a=V.dot(d,d),b=V.dot(p,d),h=b*b-a*(V.dot(p,p)-1);if(h<0)return Infinity;const t=(-b-Math.sqrt(h))/a;return t>.0001?t:Infinity}
const a=d[0]*d[0]+d[2]*d[2],b=p[0]*d[0]+p[2]*d[2],h=b*b-a*(p[0]*p[0]+p[2]*p[2]-1);let t=Infinity;if(h>=0&&a>1e-10){const x=(-b-Math.sqrt(h))/a;if(x>.0001&&Math.abs(p[1]+d[1]*x)<1)t=x}if(Math.abs(d[1])>1e-9){const x=((d[1]<0?1:-1)-p[1])/d[1],xx=p[0]+d[0]*x,zz=p[2]+d[2]*x;if(x>.0001&&xx*xx+zz*zz<=1)t=Math.min(t,x)}return t}
Luna.scene.pick=(x,y)=>{const ro=Luna.cam.eye,rd=Luna.cam.ray(x,y);let t=Infinity,object=null;for(const o of Luna.scene.objects){if(o.flag===9&&ro[1]>3.24)continue;const hit=intersectCPU(ro,rd,o);if(hit<t){t=hit;object=o}}return {object,id:object?.id??-1,group:object?groups[object.gi]:null,t,point:Number.isFinite(t)?V.add(ro,V.mul(rd,t)):null}};
Luna.scene.rebuild=()=>{
const objects=[];lightData=[];
for(let gi=0;gi<groups.length;gi++){const g=groups[gi];if(g.hidden)continue;const yaw=Q.axis([0,1,0],g.yaw);
for(const p of g.parts){const c=V.add(V.add(g.pivot,g.offset),Q.rotate(yaw,p.c.map((v,i)=>v*g.scale[i])));const basis=[0,1,2].map(j=>Q.rotate(yaw,Q.rotate(p.q,[j===0?p.s[0]:0,j===1?p.s[1]:0,j===2?p.s[2]:0]).map((v,i)=>v*g.scale[i])));const det=V.dot(basis[0],V.cross(basis[1],basis[2]));if(Math.abs(det)<1e-12)continue;const rows=[V.cross(basis[1],basis[2]),V.cross(basis[2],basis[0]),V.cross(basis[0],basis[1])].map(r=>V.mul(r,1/det));const ext=[0,1,2].map(k=>basis.reduce((s,v)=>s+Math.abs(v[k]),0));const m=Luna.scene.surface(g,p.slot,p);if(p.flag===6&&g.kind==='light')m.emission=2;const color=hexRGB(m.color).map(v=>Math.pow(v,2.2));const o={c,rows,ext,lo:V.sub(c,ext),hi:V.add(c,ext),type:p.type,dim:p.s,gi,id:p.id,slot:p.slot,flag:p.flag,bevel:p.bevel,shadow:p.shadow,color,m,source:p};objects.push(o);
if(p.flag===6){const a=V.sub(c,basis[0]),b=V.add(c,basis[0]);lightData.push({a,b,power:g.kind==='light'?2.55:.78,strip:g.kind!=='light'});}
}}
Luna.scene.objects=objects;const nodes=[],ordered=[];
function build(list){const index=nodes.length;const lo=[0,1,2].map(k=>Math.min(...list.map(o=>o.lo[k]))),hi=[0,1,2].map(k=>Math.max(...list.map(o=>o.hi[k])));const n={lo,hi,left:0,right:0,start:0,count:0};nodes.push(n);if(list.length<=4){n.start=ordered.length;n.count=list.length;ordered.push(...list)}else{const span=V.sub(hi,lo);let axis=span.indexOf(Math.max(...span));list.sort((a,b)=>a.c[axis]-b.c[axis]);const mid=Math.floor(list.length/2);n.left=build(list.slice(0,mid));n.right=build(list.slice(mid))}return index}
if(objects.length)build([...objects]);sortedObjects=ordered;bvhNodes=nodes;Luna.scene.revision++;Luna.gpu.revision=Luna.scene.revision;Luna.gpu.invalidate();
};
function uploadScene(){if(uploadRevision===Luna.scene.revision)return;const data=new Float32Array(sortedObjects.flatMap(o=>[...o.c,o.type,...o.rows[0],o.ext[0],...o.rows[1],o.ext[1],...o.rows[2],o.ext[2],...o.color,o.m.rough,o.m.tex,o.m.metal,o.m.emission||0,o.m.scale||1,o.flag,o.gi,o.id,o.bevel,...o.dim,o.shadow]));const nodes=new Float32Array(bvhNodes.flatMap(n=>[...n.lo,n.count?n.start:n.left,...n.hi,n.count||(-n.right-1)]));const lights=new Float32Array(lightData.flatMap(l=>[...l.a,l.power,...l.b,l.strip?1:0]));
for(const [buf,arr] of [[objectBuffer,data],[nodeBuffer,nodes],[lightBuffer,lights]])device.queue.writeBuffer(buf,0,arr);Luna.gpu.objectCount=sortedObjects.length;Luna.gpu.nodeCount=bvhNodes.length;Luna.gpu.lightCount=lightData.length;uploadRevision=Luna.scene.revision;
}
// Surface maps are authored locally. No network or texture-provider dependency at runtime.
const textureCanvases=[];
function makeTextures(){
const N=512;
for(let layer=0;layer<7;layer++){const c=document.createElement('canvas');c.width=c.height=N;const g=c.getContext('2d'),im=g.createImageData(N,N),d=im.data;
for(let y=0;y<N;y++)for(let x=0;x<N;x++){const u=x/N,v=y/N;let h=.5,t=.72;
if(layer===1||layer===4){const warp=Math.sin(v*TAU+Math.sin(v*TAU*2)*.25)*.022+Math.sin(v*TAU*3+u*TAU)*.009;let p=u+warp;const knot=Math.sqrt((p-.56)**2+((v-.48)*.16)**2);const growth=Math.sin(knot*TAU*85+Math.sin(v*TAU*2)*1.4);const lines=Math.sin((p+Math.sin(v*TAU)*.003)*TAU*227),micro=Math.sin(u*TAU*511+Math.sin(v*TAU*8)*2);h=.5+growth*.12+lines*.04+micro*.025;t=.69+growth*.057-Math.max(0,growth-.75)*.15+lines*.018+micro*.006+Math.sin(u*TAU*4+v*TAU)*.035;if(layer===4){t+=Math.sin(knot*TAU*33)*.06;h+=Math.sin(knot*TAU*33)*.1}}
else if(layer===2){const warp=Math.sin(u*TAU*2+Math.sin(v*TAU)*.7)*.13+Math.sin(u*TAU*5+v*TAU*2)*.025;const veins=Math.sin((v+warp)*TAU*16);const fine=Math.sin((v+warp)*TAU*61+Math.sin(u*TAU*11)*.3);t=.73+veins*.054+fine*.022+Math.sin(u*TAU*7+v*TAU*19)*.012;h=.5+veins*.10+fine*.047;}
else if(layer===3){const n=Math.sin(x*19.193+y*71.939)*43758.3;const f=n-Math.floor(n);t=.73+(f-.5)*.034+Math.sin(u*TAU*3+v*TAU*5)*.010;h=.5+(f-.5)*.08}
else if(layer===5){const a=Math.sin(x*TAU/5),b=Math.sin(y*TAU/5);h=.5+a*b*.18;t=.73+a*b*.08+Math.sin(x*6.3+y*8.7)*.015}
const i=(y*N+x)*4;d[i]=d[i+1]=d[i+2]=Math.round(clamp(t)*255);d[i+3]=Math.round(clamp(h)*255)}g.putImageData(im,0,0);textureCanvases.push(c)}
}
function uploadTextureLayer(c,layer){const tmp=document.createElement('canvas'),g=tmp.getContext('2d');for(let mip=0;mip<10;mip++){const n=512>>mip;tmp.width=tmp.height=n;g.drawImage(c,0,0,n,n);device.queue.copyExternalImageToTexture({source:tmp},{texture:materialTexture,mipLevel:mip,origin:[0,0,layer]},[n,n])}}
Luna.gpu.loadCustom=async()=>{if(!device||!materialTexture)return;try{if(!Luna.scene.customImage){uploadTextureLayer(textureCanvases[6],6);return}const image=new Image();image.src=Luna.scene.customImage;await image.decode();uploadTextureLayer(image,6);Luna.scene.revision++;Luna.gpu.invalidate()}catch{Luna.hud.hint('Die eigene Textur konnte nicht gelesen werden. Die Materialfarbe bleibt erhalten.')}};
