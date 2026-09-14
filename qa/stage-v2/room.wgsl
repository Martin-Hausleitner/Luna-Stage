struct Params {eye:vec4f, forward:vec4f, right:vec4f, up:vec4f, view:vec4f, state:vec4f};
struct Obj {centre:vec4f, size:vec4f, col:vec4f, extra:vec4f};
struct Node {lo:vec4f, hi:vec4f};
struct Hit {t:f32, id:i32, normal:vec3f};
@group(0) @binding(0) var<uniform> u:Params;
@group(0) @binding(1) var<storage,read> objects:array<Obj>;
@group(0) @binding(2) var lettering:texture_2d<f32>;
@group(0) @binding(3) var letterSampler:sampler;
@group(0) @binding(4) var history:texture_2d<f32>;
@group(0) @binding(5) var<storage,read> tree:array<Node>;
@group(0) @binding(6) var surfaces:texture_2d_array<f32>;
@group(0) @binding(7) var surfaceSampler:sampler;
@group(0) @binding(8) var environment:texture_2d<f32>;
var<private> seed:vec3f;
const PI=3.14159265359;
@vertex fn vs(@builtin(vertex_index) i:u32)->@builtin(position) vec4f {var p=array<vec2f,3>(vec2f(-1,-1),vec2f(3,-1),vec2f(-1,3));return vec4f(p[i],0,1);}
fn hash(p:vec3f)->f32 {let v=fract(p*.1031);let q=v+dot(v,v.yzx+33.33);return fract((q.x+q.y)*q.z);}
fn noise(p:vec3f)->f32 {let i=floor(p);let f=fract(p);let a=f*f*(3.-2.*f);return mix(mix(mix(hash(i),hash(i+vec3f(1,0,0)),a.x),mix(hash(i+vec3f(0,1,0)),hash(i+vec3f(1,1,0)),a.x),a.y),mix(mix(hash(i+vec3f(0,0,1)),hash(i+vec3f(1,0,1)),a.x),mix(hash(i+vec3f(0,1,1)),hash(i+vec3f(1,1,1)),a.x),a.y),a.z);}
fn rand(k:f32)->vec2f{if(u.right.w>.5){return vec2f(.5);}return vec2f(hash(seed+vec3f(k,17,31)),hash(seed+vec3f(41,k,73)));}
fn slab(ro:vec3f,rd:vec3f,lo:vec3f,hi:vec3f)->vec2f {let inv=1./(rd+vec3f(.00000001));let a=(lo-ro)*inv;let b=(hi-ro)*inv;let q=min(a,b);let w=max(a,b);return vec2f(max(max(q.x,q.y),q.z),min(min(w.x,w.y),w.z));}
fn roundedDistance(p:vec3f,s:vec3f,r:f32)->f32{let q=abs(p)-s+vec3f(r);return min(max(q.x,max(q.y,q.z)),0.)+length(max(q,vec3f(0)))-r;}
fn intersect(ro:vec3f,rd:vec3f,o:Obj)->vec4f{
 let p=ro-o.centre.xyz;let s=o.size.xyz;let kind=i32(o.centre.w);
 if(kind==1){let q=p/s;let d=rd/s;let a=dot(d,d);let b=dot(q,d);let h=b*b-a*(dot(q,q)-1.);if(h<0.){return vec4f(1e5,0,0,0);}let t=(-b-sqrt(h))/a;if(t<.0004){return vec4f(1e5,0,0,0);}return vec4f(t,normalize((p+rd*t)/(s*s)));}
 if(kind==3){let ba=o.extra.xyz*2.;let pa=p+o.extra.xyz;let r=o.extra.w;let baba=dot(ba,ba);let bard=dot(ba,rd);let bapa=dot(ba,pa);let rdoa=dot(rd,pa);let oaoa=dot(pa,pa);let a=baba-bard*bard;let b=baba*rdoa-bapa*bard;let c=baba*oaoa-bapa*bapa-r*r*baba;let h=b*b-a*c;
  if(h>=0.&&abs(a)>.00000001){let t=(-b-sqrt(h))/a;let y=bapa+t*bard;if(y>0.&&y<baba&&t>.0004){return vec4f(t,normalize(pa+rd*t-ba*y/baba));}}
  var best=vec4f(1e5,0,0,0);for(var k=0;k<2;k++){let oc=p-select(-o.extra.xyz,o.extra.xyz,k==1);let bb=dot(rd,oc);let hh=bb*bb-dot(oc,oc)+r*r;if(hh>=0.){let t=-bb-sqrt(hh);if(t>.0004&&t<best.x){best=vec4f(t,normalize(oc+rd*t));}}}return best;
 }
 if(kind==2){let a=dot(rd.xz,rd.xz);let b=dot(p.xz,rd.xz);let h=b*b-a*(dot(p.xz,p.xz)-s.x*s.x);var t=1e5;var n=vec3f(0,1,0);if(h>=0.&&a>.000001){let tt=(-b-sqrt(h))/a;let y=p.y+tt*rd.y;if(tt>.0004&&abs(y)<s.y){t=tt;n=normalize(vec3f(p.x+tt*rd.x,0,p.z+tt*rd.z));}}if(abs(rd.y)>.000001){let tt=(select(-s.y,s.y,rd.y<0.)-p.y)/rd.y;let q=p.xz+tt*rd.xz;if(tt>.0004&&tt<t&&dot(q,q)<s.x*s.x){t=tt;n=vec3f(0,select(-1.,1.,rd.y<0.),0);}}return vec4f(t,n);}
 let interval=slab(p,rd,-s,s);if(interval.y<max(interval.x,.0004)){return vec4f(1e5,0,0,0);}var t=max(interval.x,.0004);
 if(kind==4){for(var k=0;k<16;k++){let d=roundedDistance(p+rd*t,s,o.extra.w);if(d<.00008){let q=abs(p+rd*t)-s+vec3f(o.extra.w);return vec4f(t,normalize(sign(p+rd*t)*max(q,vec3f(.0000001))));}t+=d;if(t>interval.y){return vec4f(1e5,0,0,0);}}return vec4f(1e5,0,0,0);}
 if(interval.x<.0004){t=interval.y;}let q=(p+rd*t)/s;var n=vec3f(0,0,sign(q.z));if(abs(q.x)>abs(q.z)&&abs(q.x)>abs(q.y)){n=vec3f(sign(q.x),0,0);}else if(abs(q.y)>abs(q.z)){n=vec3f(0,sign(q.y),0);}return vec4f(t,n);
}
fn trace(ro:vec3f,rd:vec3f,limit:f32,shadow:bool)->Hit {
 var best=Hit(limit,-1,vec3f(0));var i=0u;
 for(var guard=0u;guard<4096u;guard++){
  if(i>=arrayLength(&tree)){break;}let node=tree[i];let ab=slab(ro,rd,node.lo.xyz,node.hi.xyz);
  if(ab.y<max(ab.x,.0003)||ab.x>best.t){i=u32(node.hi.w);continue;}
  if(node.lo.w>=0.){let id=i32(node.lo.w);let o=objects[id];if(!shadow||o.col.w>.5){let h=intersect(ro,rd,o);if(h.x<best.t){best=Hit(h.x,id,h.yzw);if(shadow){return best;}}}}i++;
 }return best;
}
fn sky(rd:vec3f)->vec3f{
 let day=u.view.z;let uv=vec2f(fract(atan2(rd.z,rd.x)/(2.*PI)+.57),clamp(.50-asin(clamp(rd.y,-1.,1.))/PI,0.01,.99));
 let photo=pow(textureSampleLevel(environment,surfaceSampler,uv,0.).rgb,vec3f(2.2));
 let dusk=mix(vec3f(.12,.20,.34),vec3f(.036,.075,.17),clamp(rd.y*3.,0.,1.));
 var col=mix(photo*.82,photo*vec3f(.10,.15,.25)+dusk*.11,smoothstep(.45,1.,day));
 return max(col,vec3f(.005,.008,.014));
}
fn materialUV(p:vec3f,n:vec3f,id:i32)->vec2f{
 let o=objects[id];var uv=vec2f(p.x,p.y);if(abs(n.x)>.65){uv=vec2f(p.z,p.y);}if(abs(n.y)>.65){uv=vec2f(p.z,p.x);}
 if(i32(o.size.w)==8&&p.y<.03){let row=floor(p.z/.205);let panel=floor((p.x+hash(vec3f(row,3,7))*1.8)/1.8);uv=vec2f((p.z-row*.205)*1.8+hash(vec3f(row,panel,2))*1.3,p.x*.65+hash(vec3f(row,panel,8))*2.);}
 else{uv+=vec2f(hash(vec3f(o.centre.x,2,3))*.62,0.);}return uv/1.8;
}
fn finish(wood:vec3f,mat:f32)->vec3f{
 let m=i32(round(mat));if(m==1){return vec3f(.53,.50,.435);}if(m==2){return wood*vec3f(.48,.34,.23);}if(m==3){return vec3f(.034,.047,.052);}if(m==4){return vec3f(.25,.30,.225);}if(m==5){return wood*vec3f(.49,.49,.45);}return wood;
}
fn baseColor(p:vec3f,n:vec3f,id:i32)->vec3f {
 let o=objects[id];let m=i32(o.size.w);var c=o.col.xyz;let uv=materialUV(p,n,id);let lod=max(0.,log2(max(.6,distance(u.eye.xyz,p)*1024./(u.view.y*1.8))));
 if(m==2||m==8||m>=15){let raw=pow(textureSampleLevel(surfaces,surfaceSampler,uv,0,lod).rgb,vec3f(2.2));let wood=raw*vec3f(.82,.82,.77);c=finish(wood,select(u.view.w,f32(m-15),m>=15));if(m==8){c=wood*o.col.xyz;}
  if(m==8&&p.y<.03){let row=floor(p.z/.205);let fx=fract((p.x+hash(vec3f(row,3,7))*1.8)/1.8);let fz=fract(p.z/.205);let seam=min(min(fx,1.-fx)*1.8,min(fz,1.-fz)*.205);c*=.45+.55*smoothstep(0.,.0018,seam);}
 }
 if(m==12){c=mix(o.col.xyz,finish(vec3f(.33,.20,.10),u.view.w),select(.08,.82,u.view.w==3.||u.view.w==4.));}
 if(m==1){c*=.98+.025*noise(p*36.);}
 if(m==3){let q=p*vec3f(1.7,1.25,1.8);let f=noise(q*.67)*.55+noise(q*2.7)*.26+noise(q*7.4)*.14;let vein=pow(max(0.,1.-abs(sin(q.x*.82+q.z*.81+q.y*.72+f*3.5))),18.);let pore=pow(noise(p*73.),10.);c*=.87+.15*f-.16*vein-.11*pore;}
 if(m==7){c*=.97+.05*noise(p*112.);}
 if(m==10){c*=.93+.055*noise(p*280.);}
 if(m==14){c*=.81+.24*noise(p*87.);}
 return c;
}
fn glyph(uv:vec2f)->f32{if(any(uv<vec2f(0))||any(uv>vec2f(1))){return 0.;}return textureSampleLevel(lettering,letterSampler,uv,0.).a;}
fn inscription(p:vec3f,n:vec3f,c:vec3f)->vec3f{
 var col=c;if(n.y>.85&&abs(p.y-.959)<.008&&p.x>-.76&&p.x<1.39&&p.z>0.&&p.z<1.03){let uv=vec2f((p.x+.76)/2.15,(p.z+.005)/1.05*.77);var a=glyph(uv)*select(u.state.x,u.state.y,uv.y>.52);let edge=glyph(uv+vec2f(.00055,.0008))*select(u.state.x,u.state.y,uv.y>.52);col=mix(col,col*.13,a*.93);col+=vec3f(.15,.13,.10)*max(0.,edge-a);}return col;
}
fn roughness(m:i32)->f32{if(m==5){return .25;}if(m==13){return .12;}if(m==3){return .34;}if(m==2){return select(.40,.26,u.view.w==1.||u.view.w==3.||u.view.w==4.);}if(m==8){return .44;}if(m==12){return .29;}return .64;}
fn shadeNormal(p:vec3f,n:vec3f,id:i32)->vec3f{
 let o=objects[id];let m=i32(o.size.w);var normal=n;
 if(i32(o.centre.w)==0&&o.col.w>.5){let radius=min(o.extra.w,min(min(o.size.x,o.size.y),o.size.z)*.38);let q=abs(p-o.centre.xyz)-o.size.xyz+vec3f(radius);normal=normalize(sign(p-o.centre.xyz)*max(q,vec3f(.000001)));}
 if((m==2&&(u.view.w==0.||u.view.w==2.||u.view.w==5.))||m==8){let nm=textureSampleLevel(surfaces,surfaceSampler,materialUV(p,n,id),1,1.).rgb*2.-1.;var t=vec3f(1,0,0);var b=vec3f(0,1,0);if(abs(n.y)>.65){t=vec3f(0,0,1);b=vec3f(1,0,0);}else if(abs(n.x)>.65){t=vec3f(0,0,1);}normal=normalize(normal+t*nm.x*.24+b*nm.y*.24);}
 return normal;
}
fn brdf(base:vec3f,n:vec3f,v:vec3f,l:vec3f,rough:f32,metal:f32)->vec3f{
 let h=normalize(v+l);let nv=max(.001,dot(n,v));let nl=max(0.,dot(n,l));let nh=max(0.,dot(n,h));let vh=max(0.,dot(v,h));
 let a=rough*rough;let a2=a*a;let dd=nh*nh*(a2-1.)+1.;let d=a2/max(.00001,PI*dd*dd);let k=(rough+1.)*(rough+1.)/8.;let g=nv/(nv*(1.-k)+k)*nl/max(.001,nl*(1.-k)+k);let f0=mix(vec3f(.04),base,metal);let f=f0+(1.-f0)*pow(1.-vh,5.);
 return ((1.-f)*(1.-metal)*base/PI+d*g*f/max(.004,4.*nv*max(.001,nl)))*nl;
}
fn visibility(p:vec3f,n:vec3f,l:vec3f,d:f32)->f32{return select(0.,1.,trace(p+n*.0012,l,d,true).id<0);}
fn direct(p:vec3f,n:vec3f,rd:vec3f,id:i32)->vec3f{
 let o=objects[id];let m=i32(o.size.w);let day=u.view.z;let base=inscription(p,n,baseColor(p,n,id));let v=-rd;let rough=roughness(m);let metal=select(0.,.86,m==5);if(m==6){return o.col.xyz*mix(1.2,4.5,day);}
 let bounce=mix(vec3f(.155,.163,.165),vec3f(.055,.065,.095),day);var col=base*bounce*(.75+.25*max(n.y,0.))*(1.-.26*exp(-max(0.,p.y)*12.));
 let q=rand(2.)-.5;let wp=vec3f(-3.16,1.83+q.x*1.64,.28+q.y*3.65);let w=wp-p;let wl=normalize(w);let light=mix(vec3f(4.2,4.05,3.7),vec3f(.35,.67,1.14),smoothstep(.25,1.,day));
 col+=brdf(base,n,v,wl,rough,metal)*light*visibility(p,n,wl,length(w));
 let sj=(rand(4.)-.5)*.012;let sl=normalize(vec3f(-1.,mix(.91,.24,day)+sj.x,mix(-.48,.30,day)+sj.y));let st=(-3.28-p.x)/sl.x;let sp=p+sl*st;
 if(sp.y>.86&&sp.y<2.76&&sp.z>-1.90&&sp.z<2.30){col+=brdf(base,n,v,sl,rough,metal)*vec3f(6.0,4.9,3.25)*visibility(p,n,sl,12.)*pow(1.-day,2.4);}
 for(var j=0;j<2;j++){let pp=(rand(9.+f32(j))-.5)*.19;let lp=vec3f(select(-.62,.79,j==1)+pp.x,2.31,.39+pp.y);let d=lp-p;let len=length(d);let ld=d/len;let power=mix(.09,3.1,day);let cone=smoothstep(.05,.58,ld.y);col+=brdf(base,n,v,ld,rough,metal)*vec3f(1.,.63,.32)*power*visibility(p,n,ld,len-.008)*cone/(.25+len*len*.38);}
 if(p.z<-1.66&&abs(p.x)<2.0){let lp=vec3f(clamp(p.x+(rand(15.).x-.5)*.30,-1.78,1.78),1.65,-2.375);let d=lp-p;let len=length(d);let ld=d/max(.001,len);col+=brdf(base,n,v,ld,rough,metal)*vec3f(1.,.63,.35)*mix(.55,1.8,day)*visibility(p,n,ld,len-.016)/(.12+len*len*1.4);}
 col+=base*vec3f(.045,.032,.016)*day*exp(-abs(p.y-2.8)*1.8);
 if(m==14){col+=base*light*.12*max(0.,dot(-n,wl));}
 if(m==13&&n.y>.8&&p.z<-2.10&&p.x>.5&&p.x<1.3){for(var j=0;j<4;j++){let cc=vec2f(.71+f32(j%2)*.36,-2.57+f32(j/2)*.29);let ring=abs(length(p.xz-cc)-.097);col+=vec3f(.035)*exp(-ring*1100.);}}
 return col;
}
fn hemisphere(n:vec3f,q:vec2f)->vec3f {let a=2.*PI*q.x;let r=sqrt(q.y);let t=normalize(cross(n,select(vec3f(0,1,0),vec3f(1,0,0),abs(n.y)>.9)));let b=cross(n,t);return normalize(t*cos(a)*r+b*sin(a)*r+n*sqrt(1.-q.y));}
@fragment fn fs(@builtin(position) pixel:vec4f)->@location(0) vec4f{
 seed=vec3f(pixel.xy,u.state.w+1.);let jitter=rand(53.)-.5;let uv=((pixel.xy+jitter)/u.view.xy)*2.-1.;let rd=normalize(u.forward.xyz+u.right.xyz*uv.x*u.eye.w-u.up.xyz*uv.y*u.forward.w);let hit=trace(u.eye.xyz,rd,80.,false);var col=sky(rd);
 if(hit.id>=0){let p=u.eye.xyz+rd*hit.t;let n=shadeNormal(p,hit.normal,hit.id);let m=i32(objects[hit.id].size.w);let base=baseColor(p,n,hit.id);col=direct(p,n,rd,hit.id);
  if(m!=6&&u.right.w<.5){let bounceDir=hemisphere(n,rand(33.));let bh=trace(p+hit.normal*.0015,bounceDir,7.,false);if(bh.id>=0){let bp=p+bounceDir*bh.t;let bc=baseColor(bp,bh.normal,bh.id);let occ=1.-.34*exp(-bh.t*8.);col*=occ;col+=base*bc*mix(.055,.028,u.view.z);if(i32(objects[bh.id].size.w)==6){col+=base*objects[bh.id].col.xyz*.17;}}else{col+=base*sky(bounceDir)*.10;}}
  if(m==3||m==5||m==13||m==2||m==12||m==8){let rough=roughness(m);let reflected=reflect(rd,n);let tangent=hemisphere(n,rand(41.));let rr=normalize(mix(reflected,tangent,rough*rough*.35));let rh=trace(p+hit.normal*.0018,rr,30.,false);var light=vec3f(.025,.03,.04);if(rr.x<-.01){let t=(-3.28-p.x)/rr.x;let wp=p+rr*t;if(t>0.&&wp.y>.84&&wp.y<2.78&&wp.z>-1.91&&wp.z<2.33){light=sky(rr);}}if(rh.id>=0){let rp=p+rr*rh.t;light=baseColor(rp,rh.normal,rh.id)*mix(vec3f(.44,.44,.39),vec3f(.13,.17,.25),u.view.z);if(i32(objects[rh.id].size.w)==6){light=objects[rh.id].col.xyz*mix(1.2,4.5,u.view.z);}}
   let f0=select(.04,.66,m==5);let f=f0+(1.-f0)*pow(1.-max(.0,dot(n,-rd)),5.);col=col*(1.-f*.65)+light*f*select(1.,.65,m==13);
  }
 }
 let prev=textureLoad(history,vec2i(pixel.xy),0).rgb;return vec4f(mix(prev,col,1./(u.state.w+1.)),1.);
}
