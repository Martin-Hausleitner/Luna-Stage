#!/usr/bin/env python3
"""Refine the existing STAGE 2 single-file kitchen; no replacement screenshot/iframe."""
from pathlib import Path
import argparse,subprocess,hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--input');args=p.parse_args()
if args.input:
 s=Path(args.input).read_text()
else:
 subprocess.run(['python','qa/stage-v2/build.py'],cwd=ROOT,check=True)
 s=(ROOT/'Luna-Stage.html').read_text()
def rep(a,b):
 global s
 if a not in s:raise ValueError('Missing source anchor: '+a[:100])
 s=s.replace(a,b,1)
def between(a,b,new):
 global s
 i=s.index(a);j=s.index(b,i);s=s[:i]+new+'\n'+s[j:]
rep('LUNA STAGE 2.0','LUNA STAGE 3.0')
rep("Luna.gpu.version='2.0'","Luna.gpu.version='3.0-detail'")
rep("ceo:false,objects:[]","ceo:false,lights:true,objects:[]")
rep("[.34,.37,.36],0);","[.115,.166,.207],0);")
rep("[.43,.45,.43],0);","[.13,.18,.22],0);")
rep("[.64,.63,.59],0);","[.62,.61,.56],0);")
rep('for(let i=0;i<87;i++){let x=-1.14+i*.0293;rod([x,.227,.919],[x,.814,.919],.0122,2,[1,1,1]);}', '''for(let i=0;i<4;i++)rounded([-.84+i*.64,.527,.908],[.316,.321,.018],.003,2,[1,1,1]);''')
rep("rounded([.12,.914,.46],[1.43,.045,.62],.019,3,[.71,.67,.575]);","rounded([.12,.914,.46],[1.43,.045,.62],.009,3,[.82,.80,.74]);")
rep("rounded([1.520,.49,.46],[.04,.424,.62],.017,3,[.71,.67,.575]);","rounded([1.520,.49,.46],[.04,.424,.62],.009,3,[.82,.80,.74]);")
rep('[1.86,.337,.02],3,[.62,.60,.55]','[1.86,.337,.02],3,[.81,.79,.73]')
s=s.replace('[.63,.61,.55]', '[.81,.79,.73]')
rep("[.297,.512,.018],12,[.60,.58,.52]","[.297,.512,.018],12,[.60,.58,.53]")
between('// Two layered architectural pendants','// Three light, curved stools',r'''
// Hollow bronze pendants, illuminated inner diffuser and thin suspension.
for(const x of [-.62,.79]){
 cyl([x,3.20,.39],.043,.015,4,[.024,.027,.03]);
 rod([x,3.195,.39],[x,2.68,.39],.0028,4,[.013,.017,.018]);
 cyl([x,2.555,.39],.157,.234,5,[.35,.285,.195]);
 cyl([x,2.435,.39],.15,.005,5,[.52,.37,.18]);
 cyl([x,2.430,.39],.137,.005,6,[1,.76,.44]);
}
''')
between('// Three light, curved stools','// Quiet, hand-thrown ceramics',r'''
// Three oak stools: rounded wooden backs, woven linen cushions, foot rails.
for(const x of [-.85,.04,.94]){
 for(const dx of [-1,1])for(const dz of [-1,1]){
  rod([x+dx*.182,.027,1.65+dz*.166],[x+dx*.150,.663,1.65+dz*.133],.024,8,[.79,.64,.48]);
  cyl([x+dx*.182,.015,1.65+dz*.166],.025,.015,4,[.023,.026,.025]);
 }
 for(const z of [1.50,1.80])rod([x-.17,.225,z],[x+.17,.225,z],.013,8,[.75,.61,.45]);
 for(const xx of [-.171,.171])rod([x+xx,.225,1.50],[x+xx,.225,1.80],.011,8,[.75,.61,.45]);
 cyl([x,.645,1.65],.234,.027,8,[.70,.57,.43]);
 cyl([x,.686,1.65],.244,.073,10,[.69,.64,.53]);
 ell([x,.721,1.65],[.239,.019,.239],10,[.72,.68,.57]);
 for(let i=0;i<36;i++){
  let a=i*Math.PI/18,b=(i+1)*Math.PI/18;
  rod([x+Math.cos(a)*.243,.712,1.65+Math.sin(a)*.243],[x+Math.cos(b)*.243,.712,1.65+Math.sin(b)*.243],.0018,10,[.55,.49,.38]);
 }
 for(const dx of [-.175,.175])rod([x+dx,.635,1.813],[x+dx,.898,1.838],.017,8,[.77,.63,.45]);
 rounded([x,.883,1.848],[.238,.048,.025],.008,8,[.85,.70,.51]);
}
''')
between('// An olive, not a cluster','// Three architectural skirting',r'''
// Every leaf is an oriented, thin 3D ellipsoid, not a camera-facing sprite.
function leaf(c,d,width,col){const length=Math.hypot(...d);O.push({c,s:d.map(v=>Math.abs(v)+width+.003),m:14,col,type:5,shadow:1,extra:[...d,width],tag:'olive-leaf'});}
function vessel(c,rb,rt,h,thick,m,col){O.push({c,s:[Math.max(rb,rt),h/2,Math.max(rb,rt)],m,col,type:6,shadow:1,extra:[rb,rt,thick,0],tag:'vessel'});}
let seed3=20260914;
function rnd(){seed3=(Math.imul(seed3,1664525)+1013904223)>>>0;return seed3/4294967296;}
const plant=[-2.53,0,.56];
vessel([-2.53,.275,.56],.215,.255,.53,.019,7,[.63,.60,.51]);
cyl([-2.53,.027,.56],.217,.025,7,[.36,.33,.27]);
cyl([-2.53,.502,.56],.231,.008,24,[.057,.041,.022]);
for(let i=0;i<48;i++){let a=i*Math.PI/24,b=(i+1)*Math.PI/24;rod([-2.53+Math.cos(a)*.245,.54,.56+Math.sin(a)*.245],[-2.53+Math.cos(b)*.245,.54,.56+Math.sin(b)*.245],.01,7,[.67,.64,.55]);}
for(let i=0;i<38;i++){let a=rnd()*Math.PI*2,r=Math.sqrt(rnd())*.212;ell([-2.53+Math.cos(a)*r,.513,.56+Math.sin(a)*r],[.006+rnd()*.008,.004,.007+rnd()*.005],7,[.13,.10,.066]);}
const trunk=[[-2.53,.507,.56],[-2.50,.72,.56],[-2.545,.94,.55],[-2.51,1.17,.58],[-2.53,1.40,.575]];
for(let i=1;i<trunk.length;i++)rod(trunk[i-1],trunk[i],.032-i*.004,24,[.17,.126,.073]);
for(let branch=0;branch<18;branch++){
 let a=branch*2.399963,r=.29+rnd()*.22,base=[-2.52,1.00+(branch%5)*.073,.565];
 let tip=[-2.53+Math.cos(a)*r,1.56+rnd()*.50,.56+Math.sin(a)*r];
 let elbow=V.lerp(base,tip,.51);elbow[1]-=.075;
 rod(base,elbow,.007+(branch%3)*.0017,24,[.20,.16,.09]);rod(elbow,tip,.004,24,[.23,.18,.10]);
 for(let twig=0;twig<3;twig++){
  let t=.35+twig*.27,root=V.lerp(elbow,tip,t),ang=a+(twig%2?-.9:1.0);
  let end=V.add(root,[Math.cos(ang)*(.12+rnd()*.085),.09+rnd()*.16,Math.sin(ang)*(.12+rnd()*.085)]);
  rod(root,end,.0017,24,[.27,.22,.13]);
  for(let k=0;k<7;k++)for(const sign of [-1,1]){
   let q=(k+.55)/7,c=V.lerp(root,end,q),az=ang+sign*(.62+rnd()*.48),le=.032+rnd()*.022;
   let dir=V.norm([Math.cos(az),.12+rnd()*.75,Math.sin(az)]);let dd=V.mul(dir,le);
   let lc=V.add(c,dd);let v=rnd();leaf(lc,dd,.008+rnd()*.0045,[.10+v*.095,.145+v*.105,.054+v*.068]);
  }
 }
}
Luna.scene.detailStats={oliveLeaves:O.filter(o=>o.tag==='olive-leaf').length,plant:'individual oriented 3D leaves, branched timber, hollow stone planter'};
// Additional, smaller herb plant next to the real sink.
vessel([-1.45,1.07,-2.58],.055,.075,.18,.007,7,[.70,.67,.59]);
for(let j=0;j<11;j++){let a=j*2.4,end=[-1.45+Math.cos(a)*.08,1.27+rnd()*.12,-2.58+Math.sin(a)*.075];rod([-1.45,1.15,-2.58],end,.0016,24,[.19,.24,.06]);for(let k=0;k<4;k++){let c=V.lerp([-1.45,1.16,-2.58],end,.28+k*.22);leaf(c,[Math.cos(a+k)*.025,.011,Math.sin(a+k)*.025],.013,[.16,.24,.061]);}}
''')
rep('box([.12,.008,1.66],[1.58,.006,.50],10,[.44,.40,.33],1,.003);','box([-2.39,.011,2.25],[.80,.008,1.25],10,[.29,.28,.25],1,.003);')
rep('// Stackless bounding-volume hierarchy.',r'''
// Real parallax outside the window. Window illumination is an emissive material.
for(let row=0;row<3;row++)for(let i=0;i<14;i++){
 const x=-10.5-row*9.5-rnd()*2,z=-20+i*3.15+row*.86,h=5.7+rnd()*11.4,w=.75+rnd()*.65,depth=.7+rnd()*1.2;
 let id=box([x,-10+h/2,z],[depth,h/2,w],21,[.09+row*.019,.13+row*.025,.18+row*.028],0,0);
 box([x,-10+h+.06,z],[depth+.025,.07,w+.025],21,[.16,.20,.25],0,0);
 if(i%3===0)box([x,-10+h+.35,z],[depth*.5,.3,w*.5],21,[.12,.17,.23],0,0);
}
box([-3.19,1.62,.21],[.012,.009,2.15],5,[.22,.24,.25],0);
// Continuous under-cabinet diffuser, profile and island shadow-line lighting.
box([0,1.67,-2.39],[1.81,.005,.043],5,[.40,.36,.24]);
box([.12,.838,.9],[1.25,.002,.007],6,[1,.73,.39]);
// Two boards, porcelain jar, amber oil bottles and glass on the island.
rounded([1.30,1.155,-2.702],[.112,.178,.016],.02,8,[.85,.71,.49]);
rounded([1.46,1.151,-2.681],[.097,.160,.013],.017,8,[.96,.78,.50]);
rounded([1.30,1.345,-2.702],[.035,.050,.016],.018,8,[.85,.71,.49]);
cyl([1.59,1.112,-2.55],.063,.254,7,[.68,.65,.56]);
cyl([1.59,1.248,-2.55],.058,.018,7,[.76,.73,.64]);
function bottle(x,y,z,scale=1){cyl([x,y+.088*scale,z],.041*scale,.176*scale,22,[.23,.15,.058]);ell([x,y+.18*scale,z],[.041*scale,.035*scale,.041*scale],22,[.26,.18,.085]);cyl([x,y+.235*scale,z],.018*scale,.078*scale,22,[.33,.26,.14]);cyl([x,y+.280*scale,z],.022*scale,.014*scale,5,[.32,.28,.18]);}
bottle(-1.12,.983,-2.61,.88);bottle(-.995,.983,-2.61,.69);
cyl([-.53,.983,.13],.137,.020,8,[.78,.63,.43]);bottle(-.53,.995,.13,1);
// Refined fruit bowl replaces the flat green plate.
vessel([-.96,1.032,.13],.108,.178,.072,.009,7,[.70,.62,.43]);
for(let i=0;i<3;i++){let x=-1.04+i*.08,z=.13+(i%2)*.056;ell([x,1.107+(i===1?.026:0),z],[.049,.051,.047],25,[.72,.315,.035]);}
// Oven door rebates, glazed cavity, shelf racks and a warm interior accent.
for(let j=0;j<3;j++){
 box([2.285,1.245+j*.128,-2.025],[.266,.004,.004],5,[.20,.24,.25]);
 for(let k=0;k<7;k++)box([2.045+k*.080,1.245+j*.128,-2.026],[.0018,.007,.0025],5,[.21,.25,.26]);
}
box([2.285,1.804,-2.031],[.082,.011,.002],4,[.045,.060,.065]);
// Restrained framed abstract art, mounted to the wall, never a UI panel.
rounded([3.76,1.76,-2.745],[.345,. fifty,.023],.004,8,[.27,.22,.15]);
box([3.76,1.76,-2.716],[.317,.47,.002],23,[.63,.60,.53]);
// Stackless bounding-volume hierarchy.'''.replace('. fifty','.50'))
rep('guard<4096u','guard<16384u')
rep("eye:[3.7,1.92,5.95],to:[-.25,1.30,-.60],end:[3.05,1.80,4.85],sun:.52,fov:51", "eye:[3.05,1.86,4.80],to:[-.30,1.32,-.60],end:[2.77,1.81,4.47],sun:.73,fov:51")
rep("Luna.scene.material=i===3&&phase>.20&&phase<.84?1:0", "Luna.scene.material=(i===0||i===2||i===5||i===3&&phase>.20&&phase<.84)?1:0")
rep(' if(kind==1){',r'''
 if(kind==5){
  let tdir=normalize(o.extra.xyz);let bdir=normalize(cross(tdir,vec3f(.01,1.,.07)));let ndir=cross(tdir,bdir);
  let scale=vec3f(length(o.extra.xyz),o.extra.w,.0017);
  let q=vec3f(dot(p,tdir),dot(p,bdir),dot(p,ndir))/scale;
  let d=vec3f(dot(rd,tdir),dot(rd,bdir),dot(rd,ndir))/scale;
  let aa=dot(d,d);let bb=dot(q,d);let hh=bb*bb-aa*(dot(q,q)-1.);
  if(hh<0.){return vec4f(1e5,0,0,0);}let t=(-bb-sqrt(hh))/aa;if(t<.0003){return vec4f(1e5,0,0,0);}
  let nn=(q+d*t)/scale;return vec4f(t,normalize(tdir*nn.x+bdir*nn.y+ndir*nn.z));
 }
 if(kind==6){
  var best=vec4f(1e5,0,0,0);let slope=(o.extra.y-o.extra.x)/(s.y*2.);let mid=(o.extra.y+o.extra.x)*.5;
  for(var side=0;side<2;side++){
   let r=mid-select(0.,o.extra.z,side==1);let rr=r+slope*p.y;
   let aa=dot(rd.xz,rd.xz)-slope*slope*rd.y*rd.y;let bb=dot(p.xz,rd.xz)-rr*slope*rd.y;let cc=dot(p.xz,p.xz)-rr*rr;let hh=bb*bb-aa*cc;
   if(hh>=0.&&abs(aa)>.0000001){for(var k=0;k<2;k++){let t=(-bb+select(-1.,1.,k==1)*sqrt(hh))/aa;let pp=p+rd*t;
    if(t>.0003&&t<best.x&&abs(pp.y)<s.y&&!(side==1&&pp.y< -s.y+o.extra.z)){
     best=vec4f(t,normalize(vec3f(pp.x,-(r+slope*pp.y)*slope,pp.z))*select(1.,-1.,side==1));
    }
   }}
  }
  if(abs(rd.y)>.000001){for(var k=0;k<2;k++){let yy=select(-s.y,s.y,k==1);let t=(yy-p.y)/rd.y;let rr=select(o.extra.x,o.extra.y,k==1);let q=p.xz+rd.xz*t;let r=length(q);if(t>.0003&&t<best.x&&r<rr&&(k==0||r>rr-o.extra.z)){best=vec4f(t,0,select(-1.,1.,k==1),0);}}}
  return best;
 }
 if(kind==1){''')
between('fn sky(rd:', 'fn materialUV(', r'''
fn sky(rd:vec3f)->vec3f{
 let day=u.view.z;let h=smoothstep(-.12,.65,rd.y);
 let morning=mix(vec3f(.76,.82,.86),vec3f(.25,.46,.69),h);
 let dusk=mix(vec3f(.28,.20,.17),vec3f(.035,.081,.18),h);
 let clouds=noise(vec3f(rd.x*5.,rd.y*15.,rd.z*6.));
 let envuv=vec2f(fract(atan2(rd.z,rd.x)/6.283185+.57),clamp(.50-asin(clamp(rd.y,-1.,1.))/3.14159,.01,.99));
 let photo=textureSampleLevel(environment,surfaceSampler,envuv,0.).rgb;
 return mix(morning,dusk,smoothstep(.15,.96,day))*(.90+.09*clouds)+photo*.008;
}
''')
s=s.replace('m==2||m==8||m>=15','m==2||m==8||(m>=15&&m<=20)')
rep('if(m==1){c*=.98+.025*noise(p*36.);}', 'if(m==1){c*=.96+.06*noise(p*38.)+.025*noise(p*180.);}')
between(' if(m==3){let q=p*', ' if(m==7)', r'''
 if(m==3){
  let q=p*vec3f(.84,.90,1.08);let f=noise(q*2.4)+noise(q*5.8)*.38+noise(q*15.)*.12;
  let line=abs(sin(q.x*2.5+q.z*2.6+q.y*2.1+f*3.4));
  let main=1.-smoothstep(.012,.050,line);let halo=1.-smoothstep(.03,.18,line);
  let hair=1.-smoothstep(.003,.013,abs(sin(q.x*15.-q.z*4.+f*6.)));
  c*=.98-.23*main-.075*halo-.045*hair+.02*noise(p*120.);
 }
''')
rep('if(m==7){c*=.97+.05*noise(p*112.);}', 'if(m==7){let pits=pow(noise(p*108.),9.);c*=.88+.14*noise(p*49.)-.7*pits;}')
rep('if(m==10){c*=.93+.055*noise(p*280.);}', 'if(m==10){let a=sin(p.x*1800.)*sin(p.z*1800.);c*=.94+.043*a+.04*noise(p*250.);}')
rep('if(m==14){c*=.81+.24*noise(p*87.);}',r'''
 if(m==14){let t=normalize(o.extra.xyz);let b=normalize(cross(t,vec3f(.01,1.,.07)));let v=abs(dot(p-o.centre.xyz,b));let rib=exp(-v*1500.);let underside=dot(n,cross(t,b))<0.;c*=select(1.,1.32,underside);c=mix(c,c*1.35+vec3f(.03,.026,.006),rib*.45);}
 if(m==24){let fib=sin(p.y*14.+noise(p*6.)*4.+atan2(p.z-.56,p.x+2.53)*21.);c*=.71+.16*fib+.3*noise(p*65.);}
 if(m==25){c*=.89+.15*noise(p*310.);}
 if(m==23){let uv=p.xy;let shape=smoothstep(.16,.18,length((uv-vec2f(3.75,1.86))*vec2f(1.,.72)));c=mix(vec3f(.19,.245,.26),c,shape);let band=smoothstep(.016,.019,abs(p.y-1.55-sin(p.x*7.)*.035));c=mix(vec3f(.41,.29,.18),c,band);}
''')
rep('col+=vec3f(.15,.13,.10)*max(0.,edge-a);}return col;',r'''col+=vec3f(.15,.13,.10)*max(0.,edge-a);}
 if(n.z>.8&&abs(p.z-.926)<.012&&p.x>-1.11&&p.x<.20&&p.y>.51&&p.y<.78&&u.state.z<.5){let uv=vec2f((p.x+1.11)/2.65,.81+(.78-p.y)*.44);let a=glyph(uv);col=mix(col,col*.28,a*.70);}
 return col;''')
rep('if(m==3){return .34;}','if(m==3){return .21;}')
rep('if(m==13){return .12;}','if(m==13||m==22){return .10;}')
rep('if(m==8){return .44;}','if(m==8){return .37;}')
rep('if(m==6){return o.col.xyz*mix(1.2,4.5,day);}', 'if(m==6){return o.col.xyz*mix(1.2,5.0,day)*u.up.w;}')
rep('let bounce=mix(vec3f(.155,.163,.165),vec3f(.055,.065,.095),day);', 'let bounce=mix(vec3f(.21,.22,.22),vec3f(.13,.145,.175),day);')
rep(' let bounce=mix(',r'''
 // Facade windows are lit at dusk; floors, mullions and blinds remain geometry-aligned.
 if(m==21){
  var uv=p.zy;let tile=floor(uv*vec2f(2.15,1.18));let f=fract(uv*vec2f(2.15,1.18));
  let mask=smoothstep(.12,.17,f.x)*(1.-smoothstep(.69,.74,f.x))*smoothstep(.17,.20,f.y)*(1.-smoothstep(.65,.71,f.y));
  let rn=hash(vec3f(tile,objects[id].centre.x));let on=select(0.,1.,rn>.39);
  let warm=mix(vec3f(.92,.35,.075),vec3f(.62,.74,.81),step(.88,rn));
  var city=base*mix(.93,.42,day)*(1.-mask*.76);city+=warm*mask*on*smoothstep(.25,.87,day)*1.8;
  city*=.90+.1*noise(p*29.);return city;
 }
 let bounce=mix(''')
rep('mix(.09,3.1,day)', 'mix(.09,4.0,day)*u.up.w')
rep('2.31,.39+pp.y','2.414,.39+pp.y')
rep('mix(.55,1.8,day)', 'mix(.55,2.35,day)*u.up.w')
rep('vec3f(.045,.032,.016)*day','vec3f(.045,.032,.016)*day*u.up.w')
rep(' if(m==14){col+=base*light*.12*max(0.,dot(-n,wl));}', ' if(m==14){col+=base*light*.18*max(0.,dot(-n,wl));col+=vec3f(.13,.10,.04)*pow(max(0.,dot(reflect(rd,n),wl)),18.)*day;}')
rep(' // Induction zones,', ' if(abs(p.x)<1.4&&p.z>.70&&p.z<1.40&&p.y<.84){col+=base*vec3f(.32,.17,.055)*day*u.up.w*exp(-abs(p.y-.835)*8.);}\n // Induction zones,')
rep('if(m!=6&&u.right.w<.5)', 'if(m!=6&&m!=21&&u.right.w<.5)')
rep('m==13||m==2||m==12||m==8','m==13||m==2||m==12||m==8||m==22')
rep("light=baseColor(rp,rh.normal,rh.id)*mix(vec3f(.44,.44,.39),vec3f(.13,.17,.25),u.view.z);", "light=direct(rp,shadeNormal(rp,rh.normal,rh.id),rr,rh.id);")
rep('objects[rh.id].col.xyz*mix(1.2,4.5,u.view.z)','objects[rh.id].col.xyz*mix(1.2,5.0,u.view.z)*u.up.w')
rep('let x=textureLoad(hdr,vec2i(p.xy),0).rgb*1.06;',r'''
 let dim=vec2i(textureDimensions(hdr));let pix=vec2i(p.xy);var glow=vec3f(0);
 for(var k=0;k<8;k++){let a=f32(k)*.785398;let d=vec2f(cos(a),sin(a));for(var j=1;j<=3;j++){let pt=clamp(pix+vec2i(d*f32(j*j)*2.),vec2i(0),dim-vec2i(1));let c=textureLoad(hdr,pt,0).rgb;glow+=max(c-vec3f(1.1),vec3f(0))*.009;}}
 let x=(textureLoad(hdr,pix,0).rgb+glow)*1.08;''')
rep('...b.u,Math.hypot(...V.sub(Luna.cam.to,Luna.cam.eye)),w,h', '...b.u,s.lights?1:0,w,h')
rep('s.price,s.ceo,Luna.cam.chapter].join', 's.price,s.ceo,s.lights,Luna.cam.chapter].join')
rep('if(hit.object?.swatch!==undefined)', 'if(hit.object?.m===6)Luna.scene.toggleLights();else if(hit.object?.swatch!==undefined)')
rep("else if(k==='m'){Luna.scene.cycle()}", "else if(k==='m'){Luna.scene.cycle()}else if(k==='l'){Luna.scene.toggleLights()}")
rep('Luna.gpu.version=', "Luna.scene.toggleLights=()=>{Luna.cam.stopShot();Luna.cam.playing=false;Luna.scene.lights=!Luna.scene.lights;Luna.hud.hint(Luna.scene.lights?'Pendelleuchten und LED-Licht an':'Leuchten aus · L zum Einschalten');Luna.gpu.invalidate()};\nLuna.gpu.version=")
rep('let presentPipeline,format,staticEntries,', 'let framePending=false;let presentPipeline,format,staticEntries,')
rep("device.queue.submit([enc.finish()]);sampleCount++;", "device.queue.submit([enc.finish()]);framePending=true;device.queue.onSubmittedWorkDone().then(()=>{framePending=false});sampleCount++;")
rep('if(Luna.gpu.snapshotBusy){raf=', 'if(Luna.gpu.snapshotBusy||framePending){raf=')
rep('Luna.gpu.targetSamples=64','Luna.gpu.targetSamples=80')
rep('function tick(now){',r'''
Luna.gpu.wait=async()=>{if(device)await device.queue.onSubmittedWorkDone()};
Luna.gpu.captureFrame=async(samples=32,w=1920,h=1080)=>{
 const old=Luna.gpu.snapshotBusy;Luna.gpu.snapshotBusy=true;
 try{await Luna.gpu.wait();for(let i=0;i<samples;i++){Luna.gpu.render(w,h);await Luna.gpu.wait();}const out=document.createElement('canvas');out.width=w;out.height=h;out.getContext('2d').drawImage($('room'),0,0);return out.toDataURL('image/png');}finally{Luna.gpu.snapshotBusy=old;}
};
function tick(now){''')
s=s.replace('Schliessen','Schließen')
(ROOT/'Luna-Stage.html').write_text(s)
meta={'version':'3.0-detail','bytes':len(s.encode()),'sha256':hashlib.sha256(s.encode()).hexdigest(),'source':'existing STAGE 2 application','reference_image_used_as_room':False}
(ROOT/'qa/stage-v3/build-receipt.json').write_text(json.dumps(meta,indent=2))
print(json.dumps(meta,indent=2))
