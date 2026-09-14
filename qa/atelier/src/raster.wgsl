// Native WebGPU real-time PBR. Geometry is rasterized; two depth maps supply contact shadows.
struct Params {eye:vec4f,forward:vec4f,right:vec4f,up:vec4f,view:vec4f,state:vec4f,light:vec4f,env:vec4f,counts:vec4f};
struct Obj {pos:vec4f,row0:vec4f,row1:vec4f,row2:vec4f,color:vec4f,surf:vec4f,flags:vec4f,dim:vec4f};
struct Light {a:vec4f,b:vec4f};
struct Shadow {origin:vec4f,right:vec4f,up:vec4f,forward:vec4f};
struct Shadows {maps:array<Shadow,2>};
@group(0) @binding(0) var<uniform> u:Params;
@group(0) @binding(1) var<storage,read> objects:array<Obj>;
@group(0) @binding(2) var lettering:texture_2d<f32>;
@group(0) @binding(3) var lettersSampler:sampler;
@group(0) @binding(4) var history:texture_2d<f32>;
@group(0) @binding(6) var surfaces:texture_2d_array<f32>;
@group(0) @binding(7) var surfaceSampler:sampler;
@group(0) @binding(8) var<storage,read> lights:array<Light>;
@group(0) @binding(9) var shadowMaps:texture_depth_2d_array;
@group(0) @binding(10) var shadowSampler:sampler_comparison;
@group(0) @binding(11) var<uniform> shadows:Shadows;
struct Vertex { @location(0) local:vec3f, @location(1) normal:vec3f, @location(2) object:u32 };
struct Fragment { @builtin(position) clip:vec4f, @location(0) world:vec3f, @location(1) normal:vec3f, @location(2) @interpolate(flat) object:u32 };
fn worldPoint(o:Obj,q:vec3f)->vec3f{let a=o.row0.xyz;let b=o.row1.xyz;let c=o.row2.xyz;let inv=1./dot(a,cross(b,c));return o.pos.xyz+(cross(b,c)*q.x+cross(c,a)*q.y+cross(a,b)*q.z)*inv;}
fn worldNormal(o:Obj,n:vec3f)->vec3f{return normalize(o.row0.xyz*n.x+o.row1.xyz*n.y+o.row2.xyz*n.z);}
fn localPoint(o:Obj,p:vec3f)->vec3f{let d=p-o.pos.xyz;return vec3f(dot(o.row0.xyz,d),dot(o.row1.xyz,d),dot(o.row2.xyz,d));}
fn localDir(o:Obj,d:vec3f)->vec3f{return vec3f(dot(o.row0.xyz,d),dot(o.row1.xyz,d),dot(o.row2.xyz,d));}
@vertex fn vs(v:Vertex)->Fragment{let o=objects[v.object];let p=worldPoint(o,v.local);let d=p-u.eye.xyz;let z=dot(d,u.forward.xyz);var clip=vec4f(dot(d,u.right.xyz)/u.eye.w,dot(d,u.up.xyz)/u.forward.w,z*1.0005-.04002,z);if(o.flags.x==9.&&u.eye.y>3.24){clip=vec4f(0,0,2,1);}return Fragment(clip,p,worldNormal(o,v.normal),v.object);}
fn hash11(x:f32)->f32{return fract(sin(x*127.137+71.319)*43758.5453);}
fn sky(rd:vec3f)->vec3f{
let night=smoothstep(.37,1.,u.view.z);let y=clamp(rd.y*.7+.46,0.,1.);var col=mix(mix(vec3f(.80,.77,.68),vec3f(.34,.52,.63),y),mix(vec3f(.065,.091,.13),vec3f(.013,.033,.073),y),night);
let az=atan2(rd.z,rd.x);let horizon=.007+sin(az*4.1)*.012+sin(az*11.5)*.004;
if(rd.y<horizon+.025){col=mix(vec3f(.28,.34,.32),vec3f(.026,.044,.065),night);}
for(var layer=0;layer<2;layer++){let k=floor(az*(29.+f32(layer)*7.));let h=.012+pow(hash11(k+f32(layer)*31.),2.)*.092+f32(layer)*.01;
if(rd.y<h){let variation=hash11(k*1.13+19.);col=mix(vec3f(.27,.32,.34),vec3f(.020,.037,.057),night)*(.66+variation*.33);
let grid=vec2f(az*(229.+f32(layer)*29.),rd.y*255.);let f=fract(grid);let lit=step(.73,hash11(floor(grid.x)+floor(grid.y)*57.+f32(layer)*231.));let pane=smoothstep(.18,.23,f.x)*(1.-smoothstep(.48,.55,f.x))*smoothstep(.28,.33,f.y)*(1.-smoothstep(.53,.6,f.y));col+=mix(vec3f(.04),vec3f(.62,.33,.11),night)*lit*pane*night;}}
return col;}
fn texUV(p:vec3f,n:vec3f,o:Obj)->vec2f{let q=localPoint(o,p)*o.dim.xyz;let nl=abs(localDir(o,n)*o.dim.xyz);var uv=q.xy*vec2f(1.3,.42);if(nl.x>nl.z&&nl.x>nl.y){uv=q.zy*vec2f(1.3,.42);}else if(nl.y>nl.z){uv=q.xz*vec2f(.70,.42);}if(o.flags.x==7.){let plank=floor(q.x/.19);let offset=hash11(plank+32.)*1.8;uv=vec2f(fract(q.x/.19)*.28,(q.z+offset)*.40);}else{uv.x+=hash11(o.flags.z*.79)*3.77;}if(o.surf.x==2.){uv=q.xz*.57;if(nl.z>nl.y){uv=q.xy*.6;}if(nl.x>nl.z&&nl.x>nl.y){uv=q.zy*.6;}}if(o.surf.x==1.){uv=uv.yx;}return uv*o.surf.w;}
fn baseColor(p:vec3f,n:vec3f,o:Obj,uv:vec2f,lod:f32)->vec3f{var c=o.color.xyz;if(o.surf.x>0.){let tex=textureSampleLevel(surfaces,surfaceSampler,uv,i32(o.surf.x),lod);c*=select(tex.rgb*1.38,pow(tex.rgb,vec3f(2.2)),o.surf.x==6.);}
if(o.flags.x==7.){let q=localPoint(o,p)*o.dim.xyz;let plank=floor(q.x/.19);let offset=hash11(plank+32.)*1.8;let a=fract(q.x/.19);let b=fract((q.z+offset)/1.8);let edge=smoothstep(0.,.009,min(a,1.-a))*smoothstep(0.,.0018,min(b,1.-b));c*=.80+.2*edge;c*=.9+hash11(plank+5.)*.15;}
return c;}
fn bump(n:vec3f,o:Obj,uv:vec2f,lod:f32)->vec3f{if(o.surf.x<.5||o.surf.x==6.){return n;}let layer=i32(o.surf.x);let delta=1./512.;let h=textureSampleLevel(surfaces,surfaceSampler,uv,layer,lod).a;let dx=textureSampleLevel(surfaces,surfaceSampler,uv+vec2f(delta,0),layer,lod).a-h;let dy=textureSampleLevel(surfaces,surfaceSampler,uv+vec2f(0,delta),layer,lod).a-h;let tangent=normalize(cross(select(vec3f(0,1,0),vec3f(0,0,1),abs(n.y)>.8),n));let bitangent=cross(n,tangent);return normalize(n-(tangent*dx+bitangent*dy)*.38);}
fn glyph(uv:vec2f)->f32{if(any(uv<vec2f(0))||any(uv>vec2f(1))){return 0.;}return textureSampleLevel(lettering,lettersSampler,uv,0.).a;}
fn inscription(p:vec3f,o:Obj,base:vec3f)->vec3f{if(o.flags.x!=1.){return base;}let q=localPoint(o,p);if(q.y<.96){return base;}let p2=q*o.dim.xyz;let uv=vec2f((p2.x+.70)/2.1,(p2.z+.29)/1.05*.77);if(uv.y<0.||uv.y>.79){return base;}let active=select(u.state.x,u.state.y,uv.y>.52);let a=glyph(uv)*active;let edge=glyph(uv+vec2f(.00055,.0009))*active;return mix(base,base*.17,a*.91)+vec3f(.10,.089,.068)*max(0.,edge-a);}
fn visibility(p:vec3f,n:vec3f,layer:i32,soft:f32)->f32{let s=shadows.maps[layer];let d=p+n*.0018-s.origin.xyz;let uv=vec2f(dot(d,s.right.xyz)/s.origin.w*.5+.5,.5-dot(d,s.up.xyz)/s.right.w*.5);let z=dot(d,s.forward.xyz)/s.up.w;if(any(uv<vec2f(0))||any(uv>vec2f(1))||z<0.||z>1.){return 1.;}let texel=soft/vec2f(textureDimensions(shadowMaps));let a=u.state.w*2.399963;let j=vec2f(cos(a),sin(a))*.65;var v=0.;for(var i=0;i<4;i++){let theta=f32(i)*1.5707963+a;let offset=(vec2f(cos(theta),sin(theta))+j)*texel;v+=textureSampleCompareLevel(shadowMaps,shadowSampler,uv+offset,layer,z-.0007);}return v*.25;}
fn direct(base:vec3f,n:vec3f,v:vec3f,l:vec3f,r:f32,metal:f32,radiance:vec3f)->vec3f{
let nl=max(dot(n,l),0.);let nv=max(dot(n,v),.01);let h=normalize(v+l);let nh=max(dot(n,h),0.);let vh=max(dot(v,h),0.);let a=max(.06,r*r);let aa=a*a;let d=aa/(3.14159265*pow(nh*nh*(aa-1.)+1.,2.)+.00001);let k=pow(r+1.,2.)/8.;let geo=nv/(nv*(1.-k)+k)*nl/(nl*(1.-k)+k);let f0=mix(vec3f(.04),base,metal);let f=f0+(1.-f0)*pow(1.-vh,5.);let spec=d*geo*f/max(4.*nv*nl,.001);return (base*(1.-metal)*.9+min(spec,vec3f(4.)))*radiance*nl;}
@fragment fn fs(v:Fragment,@builtin(front_facing) front:bool)->@location(0) vec4f{
let o=objects[v.object];let p=v.world;let gn=normalize(select(-v.normal,v.normal,front));let rd=normalize(p-u.eye.xyz);let uv=texUV(p,gn,o);let lod=max(0.,log2(max(length(dpdx(uv)),length(dpdy(uv)))*512.));let n=bump(gn,o,uv,lod);let base=inscription(p,o,baseColor(p,n,o,uv,lod));let rough=o.color.w;let metal=o.surf.y;let day=u.view.z;
let ambient=mix(vec3f(.39,.43,.44),vec3f(.16,.19,.25),smoothstep(.2,1.,day));let lightVis=visibility(p,gn,1,2.5);let heightShade=.63+.37*smoothstep(0.,.26,p.y);var col=base*ambient*(.74+.26*max(n.y,0.))*(.62+.38*lightVis)*heightShade*(1.-metal*.78);
let aperture=vec3f(-3.30,1.76,.02);let wd=normalize(aperture-p);let windowColor=mix(vec3f(.95,1.05,1.04),vec3f(.14,.24,.43),smoothstep(.18,1.,day));col+=direct(base,n,-rd,wd,rough,metal,windowColor*.42);
let sun=normalize(vec3f(-1.,mix(.85,.24,day),mix(-.34,.25,day)));let sunp=p+sun*((-3.36-p.x)/sun.x);if(sunp.y>.69&&sunp.y<2.75&&sunp.z> -2.28&&sunp.z<2.36&&day<.82){col+=direct(base,n,-rd,sun,rough,metal,vec3f(2.5,2.2,1.65)*pow(1.-day,2.)*visibility(p,gn,0,1.4));}
for(var i=0u;i<u32(u.counts.x);i++){let light=lights[i];let mid=(light.a.xyz+light.b.xyz)*.5;let closest=vec3f(clamp(p.x,min(light.a.x,light.b.x),max(light.a.x,light.b.x)),mid.y,mid.z);let ld=closest-p;let dist=length(ld);let enabled=select(1.,u.env.y,light.b.w>.5);let shadow=select(lightVis,.82+.18*lightVis,light.b.w>.5);let intensity=u.light.w*light.a.w*enabled*(.32+.68*day)/(1.+dist*dist*.66);col+=direct(base,n,-rd,normalize(ld),rough,metal,u.light.xyz*intensity*shadow);}
// Environment reflection is an approximation, not traced mirrored geometry.
let reflected=reflect(rd,n);let f0=mix(vec3f(.035),base,metal);let fresnel=f0+(1.-f0)*pow(1.-max(0.,dot(n,-rd)),5.);let reflection=mix(ambient,sky(reflected),.35);col+=reflection*fresnel*(1.-rough*.6);
if(o.flags.y==u.counts.y&&u.env.w>.5){col+=vec3f(.013,.028,.033);}
if(o.surf.z>.0){let enabled=select(u.env.y,1.,o.flags.x==5.||o.surf.z>1.5);col=u.light.xyz*(1.+u.light.w*2.)*enabled;}
col=min(max(col*exp2(u.env.x),vec3f(0)),vec3f(18.));let prev=textureLoad(history,vec2i(v.clip.xy),0).rgb;return vec4f(mix(prev,col,1./(u.state.w+1.)),1.);
}
@vertex fn skyVS(@builtin(vertex_index) i:u32)->@builtin(position) vec4f{var p=array<vec2f,3>(vec2f(-1,-1),vec2f(3,-1),vec2f(-1,3));return vec4f(p[i],.99999,1);}
@fragment fn skyFS(@builtin(position) pixel:vec4f)->@location(0) vec4f{let uv=pixel.xy/u.view.xy*2.-1.;let rd=normalize(u.forward.xyz+u.right.xyz*uv.x*u.eye.w-u.up.xyz*uv.y*u.forward.w);return vec4f(sky(rd)*exp2(u.env.x),1.);}
