// Cabinet construction in metres. Native analytic geometry; no imported application.
const O=Luna.scene.objects;
function box(c,s,m=1,col=[1,1,1],shadow=1,r=.004){O.push({c,s,m,col,type:0,shadow,extra:[0,0,0,r]});return O.length-1}
function ell(c,s,m,col){O.push({c,s,m,col,type:1,shadow:1,extra:[0,0,0,0]});return O.length-1}
function cyl(c,r,h,m,col=[1,1,1]){O.push({c,s:[r,h/2,r],m,col,type:2,shadow:1,extra:[0,0,0,0]});return O.length-1}
function rod(a,b,r,m,col){const d=V.mul(V.sub(b,a),.5);O.push({c:V.mul(V.add(a,b),.5),s:d.map(v=>Math.abs(v)+r),m,col,type:3,shadow:1,extra:[...d,r]});return O.length-1}
function rounded(c,s,r,m,col){let id=box(c,s,m,col);O[id].type=4;O[id].extra[3]=r;return id}
// Envelope, plaster reveals and a recessed ceiling line.
box([0,-.07,.7],[4.5,.07,5.2],8,[.83,.78,.69],0);
box([.5,1.65,-2.86],[4,1.65,.07],1,[.34,.37,.36],0);
box([.5,3.27,1.5],[4,.06,6],1,[.64,.63,.59],0);
box([4.48,1.65,1.5],[.06,1.65,4.35],1,[.43,.45,.43],0);
box([-3.33,1.65,5.8],[.09,1.65,2.61],1,[.59,.58,.52],0);
box([-3.33,.4,.1],[.09,.4,3.1],1,[.59,.58,.52],0);
box([-3.33,3.01,.1],[.09,.28,3.1],1,[.59,.58,.52],0);
box([-3.33,1.77,-2.5],[.09,1.02,.58],1,[.59,.58,.52],0);
box([-3.33,1.77,3.1],[.09,1.02,.76],1,[.59,.58,.52],0);
rounded([-3.24,.82,.36],[.20,.042,2.33],.012,3,[.62,.58,.49]);
for(const z of [-1.92,.39,2.33]){box([-3.25,1.79,z],[.028,1.02,.022],4,[.028,.038,.04]);box([-3.225,1.79,z],[.008,1.0,.006],5,[.24,.25,.23]);}
for(const y of [.83,2.78])box([-3.25,y,.21],[.033,.026,2.15],4,[.028,.038,.04]);
box([.15,3.13,-2.64],[3.18,.028,.035],4,[.08,.075,.065]);
box([.15,3.142,-2.64],[3.12,.006,.018],6,[1,.76,.48]);
// Six modules, each 600 mm: body, shadow gap, front, recessed finger channel.
box([0,.13,-2.39],[1.8,.12,.31],4,[.045,.05,.045]);
for(let i=0;i<6;i++){
 let x=-1.5+i*.6;box([x,.54,-2.44],[.298,.365,.36],4,[.095,.083,.068]);
 for(let j=0;j<2;j++)box([x,.358+j*.354,-2.058],[.297,.172,.022],2);
 box([x,.884,-2.05],[.282,.014,.026],4,[.055,.052,.041]);
 box([x,.902,-2.075],[.282,.004,.006],5,[.29,.24,.16]);
}
// Rear top: four separate slabs leave a real sink aperture.
rounded([-.55,.947,-2.72],[.345,.032,.095],.007,3,[.63,.61,.55]);
rounded([-.55,.947,-2.073],[.345,.032,.10],.007,3,[.63,.61,.55]);
rounded([-1.38,.947,-2.395],[.485,.032,.425],.007,3,[.63,.61,.55]);
rounded([.96,.947,-2.395],[.895,.032,.425],.007,3,[.63,.61,.55]);
box([-.55,.772,-2.396],[.313,.008,.194],5,[.13,.15,.145]);
for(const x of [-.87,-.23])box([x,.857,-2.396],[.009,.093,.194],5,[.16,.18,.17]);
for(const z of [-2.596,-2.196])box([-.55,.857,z],[.32,.093,.009],5,[.16,.18,.17]);
cyl([-.55,.782,-2.42],.032,.002,5,[.22,.23,.21]);
for(let j=0;j<5;j++)box([-.55,.785,-2.44+j*.009],[.021,.001,.0015],4,[.018,.02,.02]);
box([0,1.315,-2.748],[1.86,.337,.02],3,[.62,.60,.55]);
for(let i=0;i<6;i++){box([-1.5+i*.6,2.185,-2.575],[.298,.515,.22],12,[.51,.49,.44]);box([-1.5+i*.6,2.185,-2.34],[.297,.512,.018],12,[.60,.58,.52]);}
box([0,1.664,-2.383],[1.80,.007,.018],6,[1,.71,.40]);
// Integrated towers and dark glass oven with recessed details.
for(const x of [-2.285,2.285]){
 box([x,1.39,-2.46],[.425,1.30,.36],4,[.035,.043,.045]);
 if(x<0){box([x,.703,-2.074],[.421,.598,.022],2);box([x,2.004,-2.074],[.421,.693,.022],2);}
 else{box([x,.51,-2.074],[.421,.40,.022],2);box([x,2.305,-2.074],[.421,.39,.022],2);}
 box([x,2.715,-2.46],[.43,.012,.37],5,[.23,.22,.18]);
}
box([2.285,1.48,-2.09],[.378,.471,.04],4,[.012,.017,.02]);
box([2.285,1.414,-2.044],[.322,.292,.012],13,[.021,.028,.032]);
box([2.285,1.81,-2.046],[.33,.047,.014],13,[.025,.029,.031]);
rod([2.003,1.733,-2.002],[2.567,1.733,-2.002],.012,5,[.47,.46,.40]);
for(let j=0;j<6;j++)box([2.285,1.055+j*.010,-2.039],[.304,.002,.009],5,[.1,.12,.12]);
box([2.30,1.817,-2.029],[.032,.003,.002],6,[.57,.70,.75]);
// Honed mineral island with true rounded edges and a waterfall side.
box([.12,.13,.42],[1.25,.115,.43],4,[.032,.039,.04]);
box([.12,.515,.42],[1.28,.32,.465],2);
for(let i=0;i<4;i++)box([-.84+i*.64,.53,-.061],[.316,.322,.016],2);
for(let i=0;i<87;i++){let x=-1.14+i*.0293;rod([x,.227,.919],[x,.814,.919],.0122,2,[1,1,1]);}
rounded([.12,.914,.46],[1.43,.045,.62],.019,3,[.71,.67,.575]);
rounded([1.520,.49,.46],[.04,.424,.62],.017,3,[.71,.67,.575]);
box([.10,.854,.46],[1.36,.011,.565],4,[.062,.052,.035]);
// Swan-neck tap: continuously curved brass profile, separate mixer.
const tap=[];for(let i=0;i<=12;i++){let a=Math.PI-i*Math.PI/12;tap.push([-.53,1.245+Math.sin(a)*.119,-2.565+Math.cos(a)*.119]);}
rod([-.53,.973,-2.684],tap[0],.014,5,[.58,.40,.19]);
for(let i=1;i<tap.length;i++)rod(tap[i-1],tap[i],.014,5,[.58,.40,.19]);
rod(tap.at(-1),[-.53,1.16,-2.446],.014,5,[.58,.40,.19]);
cyl([-.53,.982,-2.684],.024,.014,5,[.52,.36,.17]);
cyl([-.285,1.018,-2.684],.021,.075,5,[.58,.40,.19]);
rod([-.285,1.051,-2.684],[-.285,1.088,-2.635],.009,5,[.58,.40,.19]);
rounded([.89,.985,-2.42],[.37,.006,.27],.018,13,[.011,.017,.021]);
for(const x of [-.62,.79]){
 cyl([x,3.20,.39],.046,.015,4,[.026,.03,.027]);rod([x,3.195,.39],[x,2.43,.39],.003,4,[.013,.017,.015]);
 cyl([x,2.40,.39],.047,.09,5,[.39,.29,.15]);cyl([x,2.347,.39],.203,.018,4,[.027,.033,.03]);
 cyl([x,2.335,.39],.196,.006,5,[.48,.34,.17]);cyl([x,2.329,.39],.135,.004,6,[1,.77,.48]);
}
// Light, curved stools: tapered stance, rounded rails, leather cushions.
for(const x of [-.85,.04,.94]){
 for(const dx of [-1,1])for(const dz of [-1,1])rod([x+dx*.18,.025,1.65+dz*.18],[x+dx*.125,.63,1.65+dz*.125],.013,4,[.026,.032,.029]);
 for(const z of [1.50,1.80])rod([x-.16,.245,z],[x+.16,.245,z],.010,5,[.27,.22,.14]);
 ell([x,.671,1.65],[.229,.043,.221],10,[.26,.20,.13]);
 rod([x-.155,.63,1.78],[x-.19,.864,1.82],.013,4,[.025,.03,.027]);rod([x+.155,.63,1.78],[x+.19,.864,1.82],.013,4,[.025,.03,.027]);
 for(let j=0;j<16;j++){let a=-.9+j*1.8/16,b=-.9+(j+1)*1.8/16;rod([x+Math.sin(a)*.265,.875,1.65+Math.cos(a)*.245],[x+Math.sin(b)*.265,.875,1.65+Math.cos(b)*.245],.026,8,[.82,.68,.45]);}
}
// Hand-thrown ceramics. Hollow bowls, board edge, individual fruit stems.
cyl([-.95,.99,.14],.20,.04,8,[.86,.72,.52]);
ell([-.95,1.039,.14],[.156,.035,.156],7,[.23,.26,.235]);
for(let j=0;j<32;j++){let a=j*Math.PI/16,b=(j+1)*Math.PI/16;rod([-.95+Math.cos(a)*.151,1.061,.14+Math.sin(a)*.151],[-.95+Math.cos(b)*.151,1.061,.14+Math.sin(b)*.151],.01,7,[.24,.265,.24]);}
for(let j=0;j<3;j++){let x=-1.004+j*.064,z=.11+(j%2)*.07;ell([x,1.10,z],[.043,.045,.045],14,[.37,.27,.092]);rod([x,1.135,z],[x+.004,1.154,z-.001],.0025,8,[.30,.22,.10]);}
box([-1.43,1.0,-2.51],[.14,.013,.12],1,[.22,.285,.26]);box([-1.425,1.025,-2.515],[.136,.009,.118],1,[.48,.42,.32]);
cyl([-1.49,1.108,-2.52],.052,.145,7,[.63,.60,.51]);cyl([-1.49,1.184,-2.52],.043,.002,4,[.045,.035,.02]);
for(let j=0;j<14;j++){let a=j/14*Math.PI*2;ell([1.495+Math.cos(a)*.076,1.126,-2.51+Math.sin(a)*.076],[.016,.13,.016],7,[.52,.50,.43]);}
// Fine olive branches and narrow leaves, rather than green spheres.
cyl([-2.59,.265,.70],.214,.51,7,[.38,.39,.35]);cyl([-2.59,.524,.70],.191,.004,1,[.087,.07,.042]);
rod([-2.59,.51,.70],[-2.60,1.78,.70],.016,8,[.35,.28,.18]);
for(let j=0;j<11;j++){
 const a=j*2.39996,y=1.03+j*.065,r=.22+(j%3)*.065,end=[-2.59+Math.cos(a)*r,y+.19,.70+Math.sin(a)*r];
 rod([-2.60,y-.13,.70],end,.005,8,[.37,.31,.20]);
 for(let k=0;k<12;k++){let t=k/12,dx=Math.sin(k*2.4+j)*.095,dz=Math.cos(k*2.4+j)*.072;
 ell([mix(-2.60,end[0],.45+t*.55)+dx,mix(y-.07,end[1],t)+Math.sin(k*3)*.065,mix(.70,end[2],.45+t*.55)+dz],[.039,.009,.014],14,[.135+(k%3)*.023,.20+(k%4)*.022,.087]);}
}
box([.1,.028,-2.766],[3.28,.026,.012],4,[.04,.05,.048]);
box([.12,.008,1.66],[1.58,.006,.50],10,[.44,.40,.33],1,.003);
// Six physical finish samples on the rear worktop.
Luna.scene.swatches=[];
for(let i=0;i<6;i++){let id=rounded([-1.28+i*.15,.998,-2.075],[.062,.015,.04],.006,15+i,[1,1,1]);O[id].swatch=i;Luna.scene.swatches.push(O[id]);}
// Stackless BVH. One primitive per leaf; skip pointers bound traversal.
const nodes=[],ordered=[];
function buildBVH(items){const idx=nodes.length,lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];for(const o of items)for(let k=0;k<3;k++){lo[k]=Math.min(lo[k],o.c[k]-o.s[k]-.0001);hi[k]=Math.max(hi[k],o.c[k]+o.s[k]+.0001);}const n={lo,hi,first:-1,end:0};nodes.push(n);if(items.length===1){n.first=ordered.length;ordered.push(items[0]);}else{let axis=hi.map((v,k)=>v-lo[k]).indexOf(Math.max(...hi.map((v,k)=>v-lo[k])));items.sort((a,b)=>a.c[axis]-b.c[axis]);let half=items.length>>1;buildBVH(items.slice(0,half));buildBVH(items.slice(half));}n.end=nodes.length;return idx;}
buildBVH([...O]);O.splice(0,O.length,...ordered);Luna.scene.bvh=nodes;
Luna.scene.palettes=['Eiche natur','Sandlack','Nussbaum','Graphit','Salbeilack','Raucheiche'];
