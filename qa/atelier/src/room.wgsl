// LUNA ray renderer: BVH, exact affine primitives, GGX direct light, contact rays,
// rough single-bounce reflections, material height detail and linear accumulation.
struct Params {eye:vec4f,forward:vec4f,right:vec4f,up:vec4f,view:vec4f,state:vec4f,light:vec4f,env:vec4f,counts:vec4f};
struct Obj {pos:vec4f,row0:vec4f,row1:vec4f,row2:vec4f,color:vec4f,surf:vec4f,meta:vec4f,dim:vec4f};
struct Node {lo:vec4f,hi:vec4f};
struct Light {a:vec4f,b:vec4f};
struct Hit {t:f32,id:i32,n:vec3f};
@group(0) @binding(0) var<uniform> u:Params;
@group(0) @binding(1) var<storage,read> objects:array<Obj>;
@group(0) @binding(2) var lettering:texture_2d<f32>;
@group(0) @binding(3) var lettersSampler:sampler;
@group(0) @binding(4) var history:texture_2d<f32>;
@group(0) @binding(5) var<storage,read> nodes:array<Node>;
@group(0) @binding(6) var surfaces:texture_2d_array<f32>;
@group(0) @binding(7) var surfaceSampler:sampler;
@group(0) @binding(8) var<storage,read> lights:array<Light>;
var<private> rng:u32;
var<private> lod:f32;
const PI=3.14159265359;
@vertex fn vs(@builtin(vertex_index) i:u32)->@builtin(position) vec4f{var p=array<vec2f,3>(vec2f(-1,-1),vec2f(3,-1),vec2f(-1,3));return vec4f(p[i],0,1);}
fn hash11(x:f32)->f32{return fract(sin(x*127.137+71.319)*43758.5453);}
fn random()->f32{rng=1664525u*rng+1013904223u;var x=rng;x=(x^(x>>16u))*2246822519u;x=(x^(x>>13u))*3266489917u;x=x^(x>>16u);return f32(x)/4294967296.;}
fn random2()->vec2f{return vec2f(random(),random());}
fn localPoint(o:Obj,p:vec3f)->vec3f{let d=p-o.pos.xyz;return vec3f(dot(o.row0.xyz,d),dot(o.row1.xyz,d),dot(o.row2.xyz,d));}
fn localDir(o:Obj,d:vec3f)->vec3f{return vec3f(dot(o.row0.xyz,d),dot(o.row1.xyz,d),dot(o.row2.xyz,d));}
fn worldNormal(o:Obj,n:vec3f)->vec3f{return normalize(o.row0.xyz*n.x+o.row1.xyz*n.y+o.row2.xyz*n.z);}
fn aabb(ro:vec3f,rd:vec3f,lo:vec3f,hi:vec3f)->f32{let inv=1./select(vec3f(1e-9),rd,abs(rd)>vec3f(1e-9));let aa=(lo-ro)*inv;let bb=(hi-ro)*inv;let nn=min(aa,bb);let ff=max(aa,bb);let t=max(max(nn.x,nn.y),nn.z);let far=min(min(ff.x,ff.y),ff.z);return select(1e8,max(t,0.),far>=max(t,.0001));}
fn intersect(ro:vec3f,rd:vec3f,o:Obj)->vec4f{
let p=localPoint(o,ro);let d=localDir(o,rd);let kind=i32(o.pos.w);
if(kind==1){let a=dot(d,d);let b=dot(p,d);let h=b*b-a*(dot(p,p)-1.);if(h<0.){return vec4f(1e8,0,0,0);}let t=(-b-sqrt(h))/a;if(t<.0002){return vec4f(1e8,0,0,0);}return vec4f(t,worldNormal(o,p+d*t));}
if(kind==2){let a=dot(d.xz,d.xz);let b=dot(p.xz,d.xz);let h=b*b-a*(dot(p.xz,p.xz)-1.);var t=1e8;var n=vec3f(0,1,0);if(h>=0.&&a>1e-9){let q=(-b-sqrt(h))/a;if(q>.0002&&abs(p.y+q*d.y)<1.){t=q;n=vec3f(p.x+q*d.x,0,p.z+q*d.z);}}if(abs(d.y)>1e-9){let q=(select(-1.,1.,d.y<0.)-p.y)/d.y;let pp=p.xz+q*d.xz;if(q>.0002&&q<t&&dot(pp,pp)<1.){t=q;n=vec3f(0,select(-1.,1.,d.y<0.),0);}}return vec4f(t,worldNormal(o,n));}
let inv=1./select(vec3f(1e-9),d,abs(d)>vec3f(1e-9));let aa=(-1.-p)*inv;let bb=(1.-p)*inv;let nn=min(aa,bb);let ff=max(aa,bb);let tn=max(max(nn.x,nn.y),nn.z);let tf=min(min(ff.x,ff.y),ff.z);if(tf<max(tn,.0002)){return vec4f(1e8,0,0,0);}let t=select(tn,tf,tn<.0002);let q=p+d*t;var n=vec3f(0,0,sign(q.z));if(abs(q.x)>abs(q.z)&&abs(q.x)>abs(q.y)){n=vec3f(sign(q.x),0,0);}else if(abs(q.y)>abs(q.z)){n=vec3f(0,sign(q.y),0);}
// A bounded bevel normal catches the real lighting without distorting a face normal.
if(o.meta.w>0.&&o.dim.w>.5){let radii=min(vec3f(.30),vec3f(o.meta.w)/o.dim.xyz);let edge=max(abs(q)-vec3f(1)+radii,vec3f(0));if(length(edge)>1e-6){n=sign(q)*edge/max(radii,vec3f(.00001));}}
return vec4f(t,worldNormal(o,n));}
fn trace(ro:vec3f,rd:vec3f,limit:f32,anyHit:bool)->Hit{
var hit=Hit(limit,-1,vec3f(0));var stack:array<u32,48>;var count=1u;stack[0]=0u;
loop{if(count==0u){break;}count--;let ix=stack[count];let b=nodes[ix];if(aabb(ro,rd,b.lo.xyz,b.hi.xyz)>=hit.t){continue;}
if(b.hi.w>0.){let start=u32(b.lo.w);let end=start+u32(b.hi.w);for(var i=start;i<end;i++){let o=objects[i];if(o.meta.x==9.&&u.eye.y>3.24){continue;}let h=intersect(ro,rd,o);if(h.x<hit.t){hit=Hit(h.x,i32(i),h.yzw);if(anyHit){return hit;}}}}
else{if(count<46u){stack[count]=u32(b.lo.w);count++;stack[count]=u32(-b.hi.w-1.);count++;}}}
return hit;}
fn sky(rd:vec3f)->vec3f{
let night=smoothstep(.37,1.,u.view.z);let y=clamp(rd.y*.7+.46,0.,1.);var col=mix(mix(vec3f(.80,.77,.68),vec3f(.34,.52,.63),y),mix(vec3f(.065,.091,.13),vec3f(.013,.033,.073),y),night);
let az=atan2(rd.z,rd.x);let horizon=.007+sin(az*4.1)*.012+sin(az*11.5)*.004;
if(rd.y<horizon+.025){col=mix(vec3f(.28,.34,.32),vec3f(.026,.044,.065),night);}
for(var layer=0;layer<2;layer++){let k=floor(az*(29.+f32(layer)*7.));let h=.012+pow(hash11(k+f32(layer)*31.),2.)*.092+f32(layer)*.01;
if(rd.y<h){let variation=hash11(k*1.13+19.);col=mix(vec3f(.27,.32,.34),vec3f(.020,.037,.057),night)*(.66+variation*.33);
let grid=vec2f(az*(229.+f32(layer)*29.),rd.y*255.);let f=fract(grid);let lit=step(.73,hash11(floor(grid.x)+floor(grid.y)*57.+f32(layer)*231.));let pane=smoothstep(.18,.23,f.x)*(1.-smoothstep(.48,.55,f.x))*smoothstep(.28,.33,f.y)*(1.-smoothstep(.53,.6,f.y));col+=mix(vec3f(.04),vec3f(.62,.33,.11),night)*lit*pane*night;}}
return col;}
fn texUV(p:vec3f,n:vec3f,o:Obj)->vec2f{let q=localPoint(o,p)*o.dim.xyz;let nl=abs(localDir(o,n)*o.dim.xyz);var uv=q.xy*vec2f(1.3,.42);if(nl.x>nl.z&&nl.x>nl.y){uv=q.zy*vec2f(1.3,.42);}else if(nl.y>nl.z){uv=q.xz*vec2f(.70,.42);}if(o.meta.x==7.){let plank=floor(q.x/.19);let offset=hash11(plank+32.)*1.8;uv=vec2f(fract(q.x/.19)*.28,(q.z+offset)*.40);}else{uv.x+=hash11(o.meta.z*.79)*3.77;}if(o.surf.x==2.){uv=q.xz*.57;if(nl.z>nl.y){uv=q.xy*.6;}if(nl.x>nl.z&&nl.x>nl.y){uv=q.zy*.6;}}return uv*o.surf.w;}
fn texAt(p:vec3f,n:vec3f,o:Obj)->vec4f{return textureSampleLevel(surfaces,surfaceSampler,texUV(p,n,o),i32(o.surf.x),lod);}
fn baseColor(p:vec3f,n:vec3f,o:Obj)->vec3f{var c=o.color.xyz;if(o.surf.x>0.){let tex=texAt(p,n,o);c*=select(tex.rgb*1.38,pow(tex.rgb,vec3f(2.2)),o.surf.x==6.);}
if(o.meta.x==7.){let q=localPoint(o,p)*o.dim.xyz;let plank=floor(q.x/.19);let offset=hash11(plank+32.)*1.8;let a=fract(q.x/.19);let b=fract((q.z+offset)/1.8);let edge=smoothstep(0.,.009,min(a,1.-a))*smoothstep(0.,.0018,min(b,1.-b));c*=.80+.2*edge;c*=.9+hash11(plank+5.)*.15;}
return c;}
fn bumped(p:vec3f,n:vec3f,o:Obj)->vec3f{if(o.surf.x<.5||o.surf.x==6.){return n;}let uv=texUV(p,n,o);let layer=i32(o.surf.x);let delta=1./512.;let h=textureSampleLevel(surfaces,surfaceSampler,uv,layer,lod).a;let dx=textureSampleLevel(surfaces,surfaceSampler,uv+vec2f(delta,0),layer,lod).a-h;let dy=textureSampleLevel(surfaces,surfaceSampler,uv+vec2f(0,delta),layer,lod).a-h;var tangent=normalize(cross(select(vec3f(0,1,0),vec3f(0,0,1),abs(n.y)>.8),n));let bitangent=cross(n,tangent);let strength=select(.10,.30,o.surf.x==5.);return normalize(n-(tangent*dx+bitangent*dy)*strength);}
fn glyph(uv:vec2f)->f32{if(any(uv<vec2f(0))||any(uv>vec2f(1))){return 0.;}return textureSampleLevel(lettering,lettersSampler,uv,0.).a;}
fn inscription(p:vec3f,n:vec3f,o:Obj,base:vec3f)->vec3f{if(o.meta.x!=1.){return base;}let q=localPoint(o,p);if(q.y<.96){return base;}let localp=q*o.dim.xyz;let uv=vec2f((localp.x+.70)/2.1,(localp.z+.29)/1.05*.77);if(uv.y<0.||uv.y>.79){return base;}let state=select(u.state.x,u.state.y,uv.y>.52);let a=glyph(uv)*state;let edge=glyph(uv+vec2f(.00055,.0009))*state;return mix(base,base*.17,a*.91)+vec3f(.10,.089,.068)*max(0.,edge-a);}
fn hemisphere(n:vec3f)->vec3f{let r=random2();let phi=6.2831853*r.x;let rr=sqrt(r.y);let t=normalize(cross(select(vec3f(0,1,0),vec3f(1,0,0),abs(n.y)>.8),n));let b=cross(n,t);return normalize(t*(cos(phi)*rr)+b*(sin(phi)*rr)+n*sqrt(1.-r.y));}
fn direct(base:vec3f,n:vec3f,v:vec3f,l:vec3f,r:f32,metal:f32,radiance:vec3f)->vec3f{
let nl=max(dot(n,l),0.);if(nl<.0001){return vec3f(0);}let nv=max(dot(n,v),.01);let h=normalize(v+l);let nh=max(dot(n,h),0.);let vh=max(dot(v,h),0.);let a=max(.05,r*r);let aa=a*a;let d=aa/(PI*pow(nh*nh*(aa-1.)+1.,2.)+.00001);let k=pow(r+1.,2.)/8.;let geometry=nv/(nv*(1.-k)+k)*nl/(nl*(1.-k)+k);let f0=mix(vec3f(.04),base,metal);let f=f0+(1.-f0)*pow(1.-vh,5.);let spec=d*geometry*f/max(4.*nv*nl,.001);return (base*(1.-metal)*.9+min(spec,vec3f(6.)))*radiance*nl;}
fn shade(p:vec3f,geometricN:vec3f,rd:vec3f,id:i32)->vec3f{
let o=objects[id];let n=bumped(p,geometricN,o);let rough=o.color.w;let metal=o.surf.y;let day=u.view.z;let base=inscription(p,n,o,baseColor(p,n,o));
if(o.surf.z>.0){let factor=select(u.env.y,1.,o.meta.x==5.||o.surf.z>1.5);return u.light.xyz*(1.+u.light.w*2.)*factor;}
let ambient=mix(vec3f(.43,.47,.48),vec3f(.15,.18,.23),smoothstep(.2,1.,day));
let aoRay=hemisphere(geometricN);let aohit=trace(p+geometricN*.002,aoRay,.34,false);let ao=select(1.,mix(.25,1.,smoothstep(0.,.34,aohit.t)),aohit.id>=0);
var col=base*ambient*(.77+.23*max(n.y,0.))*ao*(1.-metal*.83);
// The broad physical aperture and a sun admitted through its actual rectangle.
let wr=random2();let wp=vec3f(-3.32,.76+wr.x*1.90,-2.15+wr.y*4.31);let wd=wp-p;let wl=normalize(wd);if(dot(n,wl)>.0){let vis=select(0.,1.,trace(p+geometricN*.002,wl,length(wd)-.015,true).id<0);let color=mix(vec3f(1.13,1.13,1.03),vec3f(.13,.23,.40),smoothstep(.15,1.,day));col+=direct(base,n,-rd,wl,rough,metal,color*vis*.93);}
let sj=(random2()-.5)*.018;let sl=normalize(vec3f(-1.,mix(.85,.24,day)+sj.x,mix(-.34,.25,day)+sj.y));let sunp=p+sl*((-3.36-p.x)/sl.x);if(sunp.y>.69&&sunp.y<2.75&&sunp.z> -2.28&&sunp.z<2.36&&day<.82&&dot(n,sl)>.0){let vis=select(0.,1.,trace(p+geometricN*.002,sl,16.,true).id<0);col+=direct(base,n,-rd,sl,rough,metal,vec3f(2.7,2.38,1.86)*pow(1.-day,2.)*vis);}
// Each light samples its transformed physical line. Moving the pendant moves the pool.
for(var j=0;j<u32(u.counts.x);j++){let light=lights[j];let lamp=mix(light.a.xyz,light.b.xyz,random())+vec3f(0,-.009,0);let d=lamp-p;let dist=length(d);let ld=d/dist;let on=select(1.,u.env.y,light.b.w>.5);let intensity=u.light.w*light.a.w*on*(.30+.70*day)/(1.+dist*dist*.59);if(dot(n,ld)>.0&&intensity>.003){let vis=select(0.,1.,trace(p+geometricN*.0016,ld,dist-.025,true).id<0);col+=direct(base,n,-rd,ld,rough,metal,u.light.xyz*vis*intensity);}}
// Rough single-bounce reflected radiance. No temporally re-used frame after an edit.
if(rough<.79||metal>.1){let reflected=reflect(rd,n);let rr=normalize(mix(reflected,hemisphere(n),rough*rough*.55));let h=trace(p+geometricN*.003,rr,24.,false);var c=sky(rr);if(h.id>=0){let b=objects[h.id];let pp=p+geometricN*.003+rr*h.t;c=baseColor(pp,h.n,b)*ambient*(.9+.3*max(h.n.y,0.));if(b.surf.z>.0){c=u.light.xyz*2.*u.light.w;}}
let f0=mix(vec3f(.035),base,metal);let f=f0+(1.-f0)*pow(1.-max(0.,dot(n,-rd)),5.);let amount=clamp(f*(1.-rough*.48),vec3f(0),vec3f(.92));col=col*(1.-amount*.3)+c*amount;}
if(o.meta.y==u.counts.y&&u.env.w>.5){col+=vec3f(.015,.026,.03);}
return max(col,vec3f(0));}
@fragment fn fs(@builtin(position) pixel:vec4f)->@location(0) vec4f{
rng=u32(pixel.x)*1973u+u32(pixel.y)*9277u+u32(u.state.w)*26699u+911u;
let jitter=random2()-.5;let uv=(pixel.xy+jitter)/u.view.xy*2.-1.;let rd=normalize(u.forward.xyz+u.right.xyz*uv.x*u.eye.w-u.up.xyz*uv.y*u.forward.w);
let hit=trace(u.eye.xyz,rd,80.,false);var col=sky(rd);lod=max(0.,log2(max(1.,hit.t*512./u.view.x*.42)));
if(hit.id>=0){let p=u.eye.xyz+rd*hit.t;col=shade(p,hit.n,rd,hit.id);}
col*=exp2(u.env.x);col=min(col,vec3f(18.));
let prev=textureLoad(history,vec2i(pixel.xy),0).rgb;col=mix(prev,col,1./(u.state.w+1.));return vec4f(col,1.);
}
