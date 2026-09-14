'use strict';
/* LUNA STAGE 2.0 / Atelier. Original native JS + WGSL. Metres internally; mm in the UI. */
const $=id=>document.getElementById(id),clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v)),mix=(a,b,t)=>a+(b-a)*t,smooth=t=>t*t*(3-2*t),TAU=Math.PI*2;
const V={add:(a,b)=>a.map((v,i)=>v+b[i]),sub:(a,b)=>a.map((v,i)=>v-b[i]),mul:(a,s)=>a.map(v=>v*s),dot:(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),cross:(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],norm:a=>{let l=Math.hypot(...a)||1;return a.map(v=>v/l)},lerp:(a,b,t)=>a.map((v,i)=>mix(v,b[i],t))};
const Q={id:[0,0,0,1],axis:(a,t)=>[...V.mul(V.norm(a),Math.sin(t/2)),Math.cos(t/2)],mul:(a,b)=>[a[3]*b[0]+a[0]*b[3]+a[1]*b[2]-a[2]*b[1],a[3]*b[1]-a[0]*b[2]+a[1]*b[3]+a[2]*b[0],a[3]*b[2]+a[0]*b[1]-a[1]*b[0]+a[2]*b[3],a[3]*b[3]-a[0]*b[0]-a[1]*b[1]-a[2]*b[2]],inv:q=>[-q[0],-q[1],-q[2],q[3]],rotate:(q,p)=>{const t=V.mul(V.cross(q.slice(0,3),p),2);return V.add(p,V.add(V.mul(t,q[3]),V.cross(q.slice(0,3),t)))},fromY:d=>{const n=V.norm(d);return n[1]<-.9999?[1,0,0,0]:V.norm([n[2],0,-n[0],1+n[1]])}};
const hexRGB=h=>/^#[0-9a-f]{6}$/i.test(h)?[1,3,5].map(i=>parseInt(h.slice(i,i+2),16)/255):[.65,.61,.53];
const rgbHex=c=>'#'+c.map(v=>Math.round(clamp(v)*255).toString(16).padStart(2,'0')).join('');
const clone=o=>JSON.parse(JSON.stringify(o));
const params=new URLSearchParams(location.search),reduced=matchMedia('(prefers-reduced-motion: reduce)'),forcedFallback=params.get('backend')==='canvas2d';
const Luna=window.Luna={version:'2.0.0',theme:{accent:'#0078C8',navy:'#16202a'},gpu:{ready:false,backend:'Canvas2D',errors:[],frames:0,revision:0,samples:0,invalidate:()=>{}},cam:{},scene:{objects:[],groups:[]},hud:{},store:{key:'luna.stage.v1'},editor:{open:false,selected:null,surface:'front',snap:true,tab:'room'},qa:{}};
// texture: 0 plain, 1 oak, 2 stone, 3 fine concrete, 4 walnut, 5 linen, 6 imported bitmap.
const materials=Luna.scene.materials=[
{id:'oak',name:'Eiche',color:'#b89a70',rough:.49,tex:1,metal:0,scale:1},
{id:'smoked',name:'Raucheiche',color:'#705b44',rough:.50,tex:1,metal:0,scale:1},
{id:'walnut',name:'Nussbaum',color:'#896044',rough:.43,tex:4,metal:0,scale:1},
{id:'sand',name:'Sandlack',color:'#c8c1af',rough:.42,tex:0,metal:0,scale:1},
{id:'chalk',name:'Kreide',color:'#e0dfd4',rough:.54,tex:0,metal:0,scale:1},
{id:'sage',name:'Salbei',color:'#7e8a77',rough:.50,tex:0,metal:0,scale:1},
{id:'graphite',name:'Graphit',color:'#3a4141',rough:.39,tex:0,metal:0,scale:1},
{id:'travertine',name:'Travertin',color:'#c6bca6',rough:.49,tex:2,metal:0,scale:1},
{id:'ivory',name:'Keramik',color:'#d7d5c9',rough:.26,tex:2,metal:0,scale:1.25},
{id:'nero',name:'Nero',color:'#444747',rough:.24,tex:2,metal:0,scale:.85},
{id:'plaster',name:'Kalkputz',color:'#c1bfb3',rough:.82,tex:3,metal:0,scale:1},
{id:'brass',name:'Messing',color:'#b9a374',rough:.25,tex:0,metal:.85,scale:1},
{id:'blackmetal',name:'Schwarz',color:'#353d3e',rough:.30,tex:0,metal:.7,scale:1},
{id:'linen',name:'Leinen',color:'#d3cdbd',rough:.87,tex:5,metal:0,scale:1},
{id:'clay',name:'Ton',color:'#a2735b',rough:.74,tex:3,metal:0,scale:1},
{id:'custom',name:'Eigene',color:'#ffffff',rough:.55,tex:6,metal:0,scale:1}
];
const mat=id=>materials.find(m=>m.id===id)||materials[0];
const slotNames={front:'Fronten',upper:'Hängeschränke',stone:'Arbeitsplatte',wall:'Wände',floor:'Boden',metal:'Metall',seat:'Polster',ceramic:'Keramik',leaf:'Blätter',fixed:'Festes Detail'};
const themes=Luna.theme.presets=[
{id:'atelier',name:'Atelier',desc:'Eiche · Travertin',swatches:['#b79b72','#d0c5ae','#d9d5c9'],styles:{front:'oak',upper:'sand',stone:'travertine',wall:'plaster',floor:'oak',metal:'brass',seat:'linen'},sun:.70},
{id:'nord',name:'Nord',desc:'Kreide · Eiche',swatches:['#d7d9d3','#aeb7b6','#b3a080'],styles:{front:'chalk',upper:'chalk',stone:'ivory',wall:'chalk',floor:'oak',metal:'blackmetal',seat:'linen'},sun:.14},
{id:'olive',name:'Olive',desc:'Salbei · Keramik',swatches:['#808b79','#ccc9b9','#bca27d'],styles:{front:'sage',upper:'sage',stone:'ivory',wall:'plaster',floor:'oak',metal:'brass',seat:'linen'},sun:.38},
{id:'nocturne',name:'Nocturne',desc:'Raucheiche · Nero',swatches:['#645442','#343d3d','#9a845d'],styles:{front:'smoked',upper:'graphite',stone:'nero',wall:'graphite',floor:'smoked',metal:'brass',seat:'linen'},sun:.92},
{id:'terra',name:'Terra',desc:'Nussbaum · Ton',swatches:['#946c50','#aa7f69','#cec0a5'],styles:{front:'walnut',upper:'clay',stone:'travertine',wall:'plaster',floor:'oak',metal:'blackmetal',seat:'linen'},sun:.54}
];
let building=null,nextPrimitive=0;
const groups=Luna.scene.groups;
function group(id,name,kind,pivot,fn,locked=false){const g={id,name,kind,pivot,offset:[0,0,0],scale:[1,1,1],yaw:0,overrides:{},hidden:false,locked,parts:[]};groups.push(g);building=g;fn();building=null;return g}
function shape(type,c,s,slot='front',material=null,color=null,opt={}){if(!building)throw Error('Primitive requires a group');const p={id:nextPrimitive++,type,c:V.sub(c,building.pivot),s,slot,material,color,q:opt.q||[0,0,0,1],shadow:opt.shadow??1,flag:opt.flag||0,bevel:opt.bevel??.006};building.parts.push(p);return p}
const box=(c,s,slot='front',m=null,color=null,opt={})=>shape(0,c,s,slot,m,color,opt);
const ell=(c,s,slot='ceramic',m=null,color=null,opt={})=>shape(1,c,s,slot,m,color,{...opt,bevel:0});
const cyl=(c,r,h,slot='metal',m=null,color=null,opt={})=>shape(2,c,[r,h/2,r],slot,m,color,{...opt,bevel:.0015});
function rod(a,b,r,slot='metal',m=null,color=null,opt={}){return cyl(V.mul(V.add(a,b),.5),r,Math.hypot(...V.sub(b,a)),slot,m,color,{...opt,q:Q.fromY(V.sub(b,a))})}
function drawCabinet(x,id){group('cabinet-'+id,'Unterschrank '+String(id+1).padStart(2,'0'),'cabinet',[x,0,-2.43],()=>{
box([x,.11,-2.44],[.291,.105,.32],'fixed','graphite');box([x,.52,-2.43],[.297,.32,.365]);
for(const [y,h] of [[.322,.136],[.62,.153],[.816,.034]]){box([x,y,-2.045],[.295,h,.022]);}
box([x,.842,-2.063],[.27,.009,.024],'metal','blackmetal');
});}
group('walls','Wände & Decke','room',[0,0,0],()=>{
box([.55,1.65,-2.91],[4.1,1.65,.06],'wall',null,null,{shadow:0});box([.55,3.28,2],[4.1,.06,5.4],'wall',null,null,{shadow:0,flag:9});box([4.57,1.65,1.7],[.06,1.65,4.55],'wall',null,null,{shadow:0});
box([-3.43,.32,.2],[.07,.32,3.11],'wall',null,null,{shadow:0});box([-3.43,3.01,.2],[.07,.26,3.11],'wall',null,null,{shadow:0});box([-3.43,1.7,-2.64],[.07,1.1,.28],'wall',null,null,{shadow:0});box([-3.43,1.7,2.92],[.07,1.1,.45],'wall',null,null,{shadow:0});box([-3.43,1.65,5.67],[.07,1.65,2.3],'wall',null,null,{shadow:0});
box([.3,.036,-2.835],[3.65,.034,.014],'wall');
},true);
group('floor','Dielenboden','room',[0,0,0],()=>box([.5,-.07,1.5],[4.0,.07,5.9],'floor',null,null,{shadow:0,flag:7}),true);
group('window','Fenster & Laibung','room',[-3.33,0,0],()=>{
box([-3.32,.66,.03],[.18,.028,2.38],'stone','ivory');
for(const z of [-2.30,.20,2.38])box([-3.355,1.714,z],[.028,1.049,.017],'metal','blackmetal');for(const y of [.67,2.76])box([-3.355,y,.04],[.028,.019,2.345],'metal','blackmetal');
rod([-3.32,2.91,-2.5],[-3.32,2.91,2.6],.012,'metal','blackmetal');
for(let i=0;i<9;i++)shape(2,[-3.18,1.63,2.12+i*.072],[.046,1.24,.047],'seat','linen','#c8c6b9',{shadow:1});
},true);
for(let i=0;i<6;i++)drawCabinet(-1.5+i*.6,i);
// The 3 600 mm worktop is physically open at the sink, not a black decal covering solid stone.
group('worktop','Zeile · Platte & Armatur','worktop',[0,0,-2.43],()=>{
const y=.917;
box([-1.393,y,-2.407],[.445,.032,.415],'stone');box([.812,y,-2.407],[1.026,.032,.415],'stone');box([-.574,y,-2.763],[.375,.032,.059],'stone');box([-.574,y,-2.084],[.375,.032,.092],'stone');
box([0,1.233,-2.823],[1.838,.287,.021],'stone');
// Recessed sink. Thin rim and a dark basin below the worktop.
box([-.574,.838,-2.43],[.354,.012,.213],'metal','blackmetal');
for(const x of [-.929,-.219])box([x,.888,-2.43],[.010,.055,.225],'metal','blackmetal');for(const z of [-2.652,-2.208])box([-.574,.888,z],[.363,.055,.009],'metal','blackmetal');
for(const x of [-.943,-.205])box([x,.953,-2.43],[.005,.005,.228],'metal','brass');for(const z of [-2.657,-2.203])box([-.574,.953,z],[.374,.005,.005],'metal','brass');
cyl([-.57,1.071,-2.72],.014,.255,'metal');for(let i=0;i<13;i++){const a=Math.PI-i*Math.PI/13,b=Math.PI-(i+1)*Math.PI/13;rod([-.57,1.20+Math.sin(a)*.148,-2.57+Math.cos(a)*.148],[-.57,1.20+Math.sin(b)*.148,-2.57+Math.cos(b)*.148],.014,'metal')}
rod([-.57,1.2,-2.422],[-.57,1.14,-2.422],.015,'metal');cyl([-.30,.989,-2.72],.021,.10,'metal');rod([-.30,1.03,-2.72],[-.23,1.07,-2.72],.009,'metal');
// Hob with actually modelled induction-ring inlays.
box([.90,.957,-2.43],[.375,.008,.261],'fixed','blackmetal','#172126',{flag:4,bevel:.005});
for(const xx of [.725,1.085])for(const zz of [-2.57,-2.295]){for(let i=0;i<22;i++){const a=i*TAU/22,b=(i+1)*TAU/22;rod([xx+Math.cos(a)*.091,.966,zz+Math.sin(a)*.091],[xx+Math.cos(b)*.091,.966,zz+Math.sin(b)*.091],.0009,'fixed','graphite','#455051')}}
});
for(let i=0;i<3;i++)group('upper-'+i,'Hängeschrank '+(i+1),'upper',[-1.5+i*.6,0,-2.58],()=>{const x=-1.5+i*.6;box([x,2.24,-2.60],[.297,.408,.219],'upper');box([x,2.23,-2.366],[.295,.400,.017],'upper');box([x,1.824,-2.441],[.28,.005,.017],'fixed',null,'#ffe5b8',{flag:6});});
group('shelf','Offenes Regal','upper',[.91,0,-2.60],()=>{
box([.91,2.435,-2.608],[.88,.022,.214],'front');box([.91,1.84,-2.602],[.88,.024,.216],'front');box([.91,1.812,-2.455],[.82,.003,.012],'fixed',null,'#ffe5b8',{flag:6});
for(let i=0;i<7;i++)box([.23+i*.055,2.024+((i%3)*.012),-2.6],[.022,.157+((i%3)*.012),.10],'fixed','plaster',['#697573','#b5a28b','#a1836b'][i%3]);
cyl([1.46,1.97,-2.64],.083,.215,'ceramic','linen');ell([1.46,2.072,-2.64],[.08,.035,.08],'ceramic','linen');
cyl([1.19,2.547,-2.63],.070,.184,'ceramic','clay');cyl([1.19,2.65,-2.63],.034,.039,'ceramic','clay');
cyl([.63,2.50,-2.6],.137,.084,'ceramic','linen');
});
group('fridge','Kühlschrank · integriert','tower',[-2.21,0,-2.43],()=>{
box([-2.21,1.378,-2.46],[.38,1.244,.374],'upper');for(const [y,h] of [[.715,.542],[1.97,.663]])box([-2.21,y,-2.065],[.374,h,.019],'upper');box([-1.862,1.43,-2.057],[.012,1.14,.026],'metal','blackmetal');
});
group('oven','Backofen · Hochschrank','tower',[2.26,0,-2.43],()=>{
box([2.26,1.378,-2.46],[.38,1.244,.374],'upper');box([2.26,.54,-2.065],[.374,.37,.019],'upper');box([2.26,2.216,-2.065],[.374,.408,.019],'upper');
box([2.26,1.43,-2.058],[.355,.295,.029],'fixed','blackmetal','#242d31');box([2.26,1.397,-2.024],[.31,.224,.008],'fixed','graphite','#202a30',{flag:4});box([2.26,1.721,-2.018],[.354,.03,.012],'metal','blackmetal');
rod([2.006,1.649,-1.985],[2.514,1.649,-1.985],.011,'metal');
for(const x of [2.035,2.485]){shape(2,[x,1.721,-1.993],[.013,.009,.013],'metal',null,null,{q:Q.axis([1,0,0],Math.PI/2)})}
box([2.26,1.72,-1.999],[.065,.005,.001],'fixed',null,'#b2c2be',{flag:5});
});
group('pantry','Vorratsschrank','tower',[3.03,0,-2.43],()=>{box([3.03,1.378,-2.46],[.38,1.244,.374],'upper');box([3.03,1.40,-2.065],[.374,1.216,.019],'upper');box([2.681,1.40,-2.053],[.009,1.135,.019],'metal','blackmetal')});
group('island','Insel · Monolith','island',[.05,0,.42],()=>{
box([.05,.106,.42],[1.27,.10,.44],'fixed','graphite','#303b3e');box([.05,.537,.42],[1.32,.324,.472],'front');
for(let i=0;i<68;i++)shape(2,[-1.252+i*.039,.537,.904],[.0158,.323,.020],'front');
box([.05,.904,.43],[1.44,.044,.644],'stone',null,null,{flag:1,bevel:.012});
box([1.462,.497,.43],[.028,.40,.644],'stone',null,null,{bevel:.009});box([-1.362,.497,.43],[.028,.40,.644],'stone',null,null,{bevel:.009});
box([.05,.858,.42],[1.32,.012,.475],'metal','blackmetal');
});
function stool(x,id){return group('stool-'+id,'Hocker '+id,'stool',[x,0,1.70],()=>{
for(const dx of [-.153,.153])for(const dz of [-.15,.15])rod([x+dx*1.22,.015,1.70+dz*1.2],[x+dx,.666,1.70+dz],.011,'metal','blackmetal');
rod([x-.166,.253,1.531],[x+.166,.253,1.531],.009,'metal','blackmetal');rod([x-.166,.253,1.531],[x-.166,.253,1.869],.008,'metal','blackmetal');rod([x+.166,.253,1.531],[x+.166,.253,1.869],.008,'metal','blackmetal');
ell([x,.696,1.70],[.235,.045,.222],'seat');cyl([x,.66,1.70],.205,.018,'front','oak');
rod([x-.181,.65,1.872],[x-.181,.911,1.889],.012,'front','oak');rod([x+.181,.65,1.872],[x+.181,.911,1.889],.012,'front','oak');
ell([x,.898,1.902],[.224,.069,.043],'seat');
})}[-.92,.015,.95].forEach((x,i)=>stool(x,i+1));
group('pendant','Pendelleuchte · Linie','light',[.05,0,.42],()=>{
box([.05,3.193,.42],[.8,.013,.035],'metal','blackmetal');for(const x of [-.71,.81])rod([x,3.18,.42],[x,2.30,.42],.0032,'metal','blackmetal');
rod([-1.02,2.285,.42],[1.12,2.285,.42],.024,'metal');box([.05,2.266,.42],[1.075,.003,.016],'fixed',null,'#ffe5b8',{flag:6});
});
group('composition','Schale · Birnen & Leinen','decor',[-.94,0,.20],()=>{
box([-.93,.955,.19],[.233,.007,.187],'seat','linen','#aa9f85',{q:Q.axis([0,1,0],.08),bevel:.002});
cyl([-.96,.972,.18],.185,.02,'front','oak');ell([-.96,1.015,.18],[.174,.043,.172],'ceramic','clay','#8f8772');
for(const [x,z] of [[-.99,.17],[-.884,.22]]){ell([x,1.077,z],[.056,.069,.050],'ceramic','clay','#b5a25d');ell([x,1.131,z],[.026,.04,.028],'ceramic','clay','#b5a25d');rod([x,1.151,z],[x+.008,1.177,z+.012],.003,'front','walnut')}
});
group('coffee','Kaffee & Bücher','decor',[-1.44,0,-2.49],()=>{
box([-1.43,.967,-2.52],[.145,.012,.11],'fixed','clay');box([-1.42,.991,-2.52],[.14,.011,.105],'fixed','sage');cyl([-1.46,1.055,-2.51],.046,.104,'ceramic','linen');cyl([-1.46,1.109,-2.51],.036,.001,'fixed','walnut','#634e37');
});
group('olive-tree','Olivenbaum','plant',[-2.61,0,.88],()=>{
cyl([-2.61,.244,.88],.20,.47,'ceramic','plaster','#a8a595');cyl([-2.61,.477,.88],.177,.003,'fixed','smoked');rod([-2.61,.46,.88],[-2.57,1.59,.875],.016,'front','walnut');
for(let j=0;j<7;j++){const a=j*2.39996,r=.20+(j%3)*.045,y=1.15+(j%4)*.15;const end=[-2.60+Math.cos(a)*r,y+.22,.88+Math.sin(a)*r];rod([-2.59,y-.2,.88],end,.004,'front','walnut');
for(let k=0;k<9;k++){const b=k*2.4+j,rad=.07+(k%3)*.044,p=[end[0]+Math.cos(b)*rad,end[1]+((k%4)-1.5)*.048,end[2]+Math.sin(b)*rad];ell(p,[.055,.008,.019],'leaf','sage',['#596344','#6f7a51','#77815a'][k%3],{q:Q.mul(Q.axis([0,1,0],b),Q.axis([0,0,1],.25+(k%3)*.4))});}
}
});
// Namespaces are explicit and small. All editable geometry remains parameter data, not DOM snapshots.
Object.assign(Luna.scene,{family:'Berger',runMM:3600,priceEUR:18740,vat:20,week:38,material:0,price:false,ceo:false,sun:.70,kelvin:2700,power:1,exposure:0,strip:true,quality:'auto',theme:'atelier',styles:clone(themes[0].styles),customImage:null,customName:'',revision:0});
const factoryGroups=clone(groups),factoryScene={theme:'atelier',styles:clone(themes[0].styles),sun:.70,kelvin:2700,power:1,exposure:0,strip:true,quality:'auto',material:0};
Luna.scene.group=id=>groups.find(g=>g.id===id);
Luna.scene.surface=(g,slot,p=null)=>{let base=mat(p?.material||Luna.scene.styles[slot]||({ceramic:'linen',leaf:'sage',fixed:'graphite'}[slot])||'oak');let d={...base};if(p?.color)d.color=p.color;if(!p?.material&&slot==='front'&&Luna.scene.material===1)d={...mat('sand')};const override=g.overrides[slot];if(override&&slot!=='fixed')d={...mat(override.id||d.id),...override};if(p?.flag===6||p?.flag===5)d={...d,emission:p.flag===6?1:0.25};return d};
Luna.scene.getBounds=g=>{let lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];for(const p of g.parts){let r=[0,1,2].map(k=>[0,1,2].reduce((s,j)=>s+Math.abs(Q.rotate(p.q,[j===0?1:0,j===1?1:0,j===2?1:0])[k])*p.s[j],0));for(let k=0;k<3;k++){lo[k]=Math.min(lo[k],p.c[k]-r[k]);hi[k]=Math.max(hi[k],p.c[k]+r[k])}}return {lo,hi,size:V.sub(hi,lo)}};
for(const g of groups)g.bounds=Luna.scene.getBounds(g);
Luna.scene.bounds=()=>({runMM:3600,modules:6,moduleMM:600,objects:Luna.scene.objects.length,editableGroups:groups.filter(g=>!g.locked&&!g.hidden).length});
