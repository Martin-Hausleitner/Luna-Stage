/* Validated local documents and a bounded history. A v1 scene migrates without restoring the CEO margin. */
let undoStack=[],redoStack=[],historyBefore=null,saveTimer=0,customBitmap=null;
const sceneFields=['theme','styles','sun','kelvin','power','exposure','strip','quality','material'];
Luna.store.document=()=>({schema:'luna.stage.project',version:2,family:'Berger',scene:Object.fromEntries(sceneFields.map(k=>[k,clone(Luna.scene[k])])),groups:groups.filter(g=>!g.locked).map(g=>({id:g.id,name:g.name,template:g.template||g.id,offset:g.offset,scale:g.scale,yaw:g.yaw,overrides:g.overrides,hidden:g.hidden})),room:groups.filter(g=>g.locked).map(g=>({id:g.id,overrides:g.overrides})),customImage:Luna.scene.customImage,customName:Luna.scene.customName,camera:{eye:Luna.cam.eye,to:Luna.cam.to,fov:Luna.cam.fov,chapter:Luna.cam.chapter},savedAt:new Date().toISOString()});
const comparable=d=>JSON.stringify({...d,savedAt:null});
Luna.store.validate=d=>{
if(!d||d.schema!=='luna.stage.project'||d.version!==2||typeof d!=='object')throw Error('Keine gültige LUNA-STAGE-Projektdatei.');
const s=d.scene;if(!s||!themes.some(t=>t.id===s.theme))throw Error('Unbekanntes Thema.');
for(const [k,lo,hi] of [['sun',0,1],['kelvin',2200,5000],['power',0,2],['exposure',-1,1]])if(!Number.isFinite(s[k])||s[k]<lo||s[k]>hi)throw Error('Ungültiger Lichtwert: '+k);
if(!s.styles||Object.keys(s.styles).some(k=>!slotNames[k]||!materials.some(m=>m.id===s.styles[k])))throw Error('Ungültige Materialauswahl.');
if(!Array.isArray(d.groups)||d.groups.length>64||!Array.isArray(d.room)||d.room.length>4)throw Error('Ungültige Elementliste.');
const vector=(a,lo,hi)=>Array.isArray(a)&&a.length===3&&a.every(x=>Number.isFinite(x)&&x>=lo&&x<=hi);
const validOverrides=o=>{if(!o||Array.isArray(o)||typeof o!=='object')return false;return Object.entries(o).every(([slot,v])=>Object.hasOwn(slotNames,slot)&&v&&typeof v==='object'&&(!v.id||materials.some(m=>m.id===v.id))&&(!v.color||/^#[0-9a-f]{6}$/i.test(v.color))&&(v.rough===undefined||Number.isFinite(v.rough)&&v.rough>=.05&&v.rough<=.95)&&(v.scale===undefined||Number.isFinite(v.scale)&&v.scale>=.25&&v.scale<=3)&&Object.keys(v).every(k=>['id','color','rough','scale'].includes(k)))};
const ids=new Set();for(const g of d.groups){if(typeof g.id!=='string'||!/^[a-z0-9-]{1,60}$/.test(g.id)||ids.has(g.id)||!factoryGroups.some(f=>f.id===(g.template||g.id)&&!f.locked))throw Error('Unbekanntes oder doppeltes Element.');ids.add(g.id);if(!vector(g.offset,-10,10)||!vector(g.scale,.15,3)||!Number.isFinite(g.yaw)||Math.abs(g.yaw)>TAU*3||!validOverrides(g.overrides)||typeof g.hidden!=='boolean'||typeof g.name!=='string'||g.name.length>80)throw Error('Ungültige Geometrie.');}
for(const g of d.room)if(!factoryGroups.some(f=>f.locked&&f.id===g.id)||!validOverrides(g.overrides))throw Error('Ungültige Raumoberfläche.');
if(d.customImage!==null&&d.customImage!==undefined&&(!/^data:image\/(png|jpeg|webp);base64,[a-zA-Z0-9+/=]+$/.test(d.customImage)||d.customImage.length>1600000))throw Error('Ungültige eingebettete Textur.');
if(d.camera&&(!vector(d.camera.eye,-15,15)||!vector(d.camera.to,-15,15)||Math.hypot(...V.sub(d.camera.eye,d.camera.to))<.1||!Number.isFinite(d.camera.fov)||d.camera.fov<20||d.camera.fov>90))throw Error('Ungültige Kamera.');
return clone(d);
};
Luna.store.apply=d=>{
const valid=Luna.store.validate(d),byid=new Map(valid.groups.map(g=>[g.id,g]));
groups.splice(0,groups.length,...clone(factoryGroups));for(const g of groups){if(g.locked){g.overrides=clone(valid.room.find(r=>r.id===g.id)?.overrides||{})}else{const x=byid.get(g.id);if(x){Object.assign(g,{offset:x.offset,scale:x.scale,yaw:x.yaw,overrides:x.overrides,hidden:x.hidden});byid.delete(g.id)}}g.bounds=Luna.scene.getBounds(g)}
for(const x of byid.values()){const template=factoryGroups.find(g=>g.id===(x.template||x.id));const g={...clone(template),...x};g.bounds=Luna.scene.getBounds(g);groups.push(g)}
for(const k of sceneFields)if(valid.scene[k]!==undefined)Luna.scene[k]=clone(valid.scene[k]);Luna.scene.customImage=valid.customImage||null;Luna.scene.customName=String(valid.customName||'Eigene Textur').slice(0,100);
if(valid.camera)Object.assign(Luna.cam,{eye:[...valid.camera.eye],to:[...valid.camera.to],fov:valid.camera.fov,chapter:clamp(Math.floor(valid.camera.chapter||0),0,5)});
Luna.scene.ceo=false;Luna.cam.playing=false;Luna.cam.transition=null;Luna.cam.manual=true;
if(!Luna.scene.group(Luna.editor.selected)||Luna.scene.group(Luna.editor.selected)?.hidden)Luna.editor.selected='island';
Luna.scene.rebuild?.();Luna.editor.sync?.();Luna.hud.sync?.();Luna.gpu.invalidate();return valid;
};
Luna.store.write=()=>{try{localStorage.setItem(Luna.store.key,JSON.stringify(Luna.store.document()));$('save-state').textContent='Lokal gesichert';$('save-state').classList.remove('warning');Luna.store.saved=true;return true}catch{Luna.store.saved=false;$('save-state').textContent='Nicht gesichert · bitte exportieren';$('save-state').classList.add('warning');return false}};
Luna.store.schedule=()=>{clearTimeout(saveTimer);$('save-state').textContent='Änderung wird gesichert …';saveTimer=setTimeout(Luna.store.write,250)};
Luna.editor.begin=()=>{if(!historyBefore)historyBefore=Luna.store.document()};
Luna.editor.commit=()=>{if(historyBefore){const now=Luna.store.document();if(comparable(historyBefore)!==comparable(now)){undoStack.push(historyBefore);if(undoStack.length>40)undoStack.shift();redoStack=[];}historyBefore=null}Luna.store.schedule();Luna.editor.syncHistory?.()};
Luna.editor.transaction=fn=>{Luna.editor.begin();fn();Luna.scene.rebuild();Luna.editor.commit();Luna.editor.sync();Luna.hud.sync();Luna.gpu.invalidate()};
Luna.editor.undo=()=>{if(!undoStack.length)return;redoStack.push(Luna.store.document());const d=undoStack.pop();Luna.store.apply(d);Luna.gpu.loadCustom?.();Luna.editor.syncHistory();Luna.store.schedule();Luna.hud.hint('Letzte Änderung rückgängig gemacht.')};
Luna.editor.redo=()=>{if(!redoStack.length)return;undoStack.push(Luna.store.document());Luna.store.apply(redoStack.pop());Luna.gpu.loadCustom?.();Luna.editor.syncHistory();Luna.store.schedule();Luna.hud.hint('Änderung wiederhergestellt.')};
Luna.theme.apply=id=>{const t=themes.find(t=>t.id===id);if(!t)return;Luna.editor.transaction(()=>{Luna.scene.theme=t.id;Luna.scene.styles=clone(t.styles);Luna.scene.sun=t.sun;Luna.scene.material=0;for(const g of groups)g.overrides={};Luna.cam.playing=false;Luna.cam.manual=true;Luna.cam.transition=null});Luna.hud.hint(t.name+' · Oberflächen neu abgestimmt. Ihre Möbel bleiben an ihrem Platz.')};
Luna.cam.chapters=[
{name:'Ankunft',eye:[3.76,1.97,6.12],to:[-.10,1.28,-.45],end:[3.03,1.92,4.92],sun:.53,fov:50},
{name:'Holz',eye:[1.76,1.39,3.1],to:[-.29,.72,.50],end:[1.28,1.23,2.67],sun:.06,fov:45},
{name:'Abend',eye:[3.16,2.04,4.99],to:[-.12,1.30,-.41],end:[2.9,1.99,4.7],sun:.91,fov:50},
{name:'Oberfläche',eye:[2.82,1.87,4.23],to:[.09,1.14,-.39],end:[2.52,1.86,4.10],sun:.27,fov:50},
{name:'Zahl',eye:[.83,2.58,3.51],to:[.05,.96,.36],end:[.67,2.49,3.35],sun:.73,fov:48},
{name:'Stille',eye:[3.21,2.02,5.30],to:[-.18,1.28,-.46],end:[3.21,2.02,5.30],sun:.82,fov:52}
];
const cs=Luna.cam.chapters;Object.assign(Luna.cam,{chapter:0,time:0,duration:48,playing:!reduced.matches,eye:[...cs[0].eye],to:[...cs[0].to],fov:50,manual:false,transition:null,lastUser:0});
Luna.cam.basis=()=>{const f=V.norm(V.sub(Luna.cam.to,Luna.cam.eye)),r=V.norm(V.cross(f,[0,1,0])),u=V.cross(r,f);return {f,r,u,tan:Math.tan(Luna.cam.fov*Math.PI/360)}};
Luna.cam.project=(p,w=innerWidth,h=innerHeight)=>{const b=Luna.cam.basis(),d=V.sub(p,Luna.cam.eye),z=V.dot(d,b.f);return {x:w/2+V.dot(d,b.r)/Math.max(.001,z)/b.tan*h/2,y:h/2-V.dot(d,b.u)/Math.max(.001,z)/b.tan*h/2,z}};
Luna.cam.ray=(x,y)=>{const b=Luna.cam.basis();return V.norm(V.add(b.f,V.add(V.mul(b.r,(x/innerWidth*2-1)*(innerWidth/innerHeight)*b.tan),V.mul(b.u,(1-y/innerHeight*2)*b.tan))))};
Luna.cam.stop=()=>{Luna.cam.playing=false;Luna.cam.transition=null;Luna.cam.manual=true;Luna.hud.sync?.()};
Luna.cam.apply=(i,phase=0)=>{const c=cs[i];Luna.cam.eye=V.lerp(c.eye,c.end,smooth(clamp(phase)));Luna.cam.to=[...c.to];Luna.cam.fov=c.fov;Luna.scene.sun=c.sun;Luna.scene.price=i===4;const m=i===3&&phase>.20&&phase<.84?1:0;if(m!==Luna.scene.material){Luna.scene.material=m;Luna.scene.rebuild?.()}};
Luna.cam.goto=(i,animate=true)=>{i=Number.isFinite(i)?clamp(Math.floor(i),0,5):0;const old={eye:[...Luna.cam.eye],to:[...Luna.cam.to],fov:Luna.cam.fov,sun:Luna.scene.sun};Luna.cam.chapter=i;Luna.cam.time=i*8;Luna.cam.manual=false;Luna.cam.playing=false;Luna.cam.apply(i,i===3?.50:.20);Luna.cam.transition=animate&&Luna.gpu.ready&&!reduced.matches?{old,start:performance.now()}:null;Luna.hud.sync?.();Luna.editor.syncLight?.();Luna.gpu.invalidate();Luna.hud.announce?.(cs[i].name)};
Luna.cam.seek=seconds=>{Luna.cam.time=clamp(seconds,0,48);const i=Math.min(5,Math.floor(Luna.cam.time/8));Luna.cam.chapter=i;Luna.cam.manual=false;Luna.cam.playing=false;Luna.cam.transition=null;Luna.cam.apply(i,(Luna.cam.time-i*8)/8);Luna.hud.sync?.();Luna.gpu.invalidate()};
Luna.cam.toggle=()=>{if(Luna.editor.open)Luna.editor.toggle(false);if(Luna.cam.time>=47.9){Luna.cam.time=0;Luna.cam.chapter=0}Luna.cam.manual=false;Luna.cam.transition=null;Luna.cam.playing=!Luna.cam.playing;Luna.hud.sync();Luna.gpu.invalidate()};
Luna.cam.view=id=>{Luna.cam.stop();if(id==='plan'){Object.assign(Luna.cam,{eye:[.02,7.8,1.6],to:[0,0,-.3],fov:47,chapter:2})}else if(id==='detail'){Object.assign(Luna.cam,{eye:[1.95,1.43,3.36],to:[0,.77,.49],fov:44,chapter:2})}else{Object.assign(Luna.cam,{eye:[3.05,1.98,5.20],to:[-.10,1.22,-.41],fov:52,chapter:2})}Luna.hud.sync();Luna.gpu.invalidate()};
Luna.cam.orbit=(dx,dy)=>{const offset=V.sub(Luna.cam.eye,Luna.cam.to),r=Math.hypot(...offset);let theta=Math.atan2(offset[0],offset[2])-dx*.0045,phi=Math.acos(clamp(offset[1]/r,-1,1))+dy*.0045;phi=clamp(phi,.16,1.48);Luna.cam.eye=V.add(Luna.cam.to,[Math.sin(theta)*Math.sin(phi)*r,Math.cos(phi)*r,Math.cos(theta)*Math.sin(phi)*r]);Luna.cam.stop();Luna.gpu.invalidate()};
Luna.cam.pan=(dx,dy)=>{const b=Luna.cam.basis(),r=Math.hypot(...V.sub(Luna.cam.eye,Luna.cam.to)),delta=V.mul(V.add(V.mul(b.r,-dx),V.mul(b.u,dy)),r*.0012);Luna.cam.eye=V.add(Luna.cam.eye,delta);Luna.cam.to=V.add(Luna.cam.to,delta);Luna.cam.stop();Luna.gpu.invalidate()};
Luna.cam.zoom=delta=>{const v=V.sub(Luna.cam.eye,Luna.cam.to),r=Math.hypot(...v),distance=clamp(r*Math.exp(delta*.001),1.1,12);Luna.cam.eye=V.add(Luna.cam.to,V.mul(V.norm(v),distance));Luna.cam.stop();Luna.gpu.invalidate()};
Luna.scene.cycle=()=>{if(!Luna.gpu.ready){Luna.cam.goto(Luna.scene.material?2:3,false);return}Luna.cam.stop();Luna.editor.transaction(()=>{Luna.scene.material=1-Luna.scene.material});Luna.hud.announce(Luna.scene.material?'Sandlack, seidenmatt':'Eiche natur')};
Luna.scene.togglePrice=()=>{Luna.cam.stop();Luna.scene.price=!Luna.scene.price;Luna.hud.sync();Luna.gpu.invalidate();Luna.hud.announce(Luna.scene.price?'18.740 Euro inklusive 20 Prozent Umsatzsteuer. Montage Kalenderwoche 38. Demo, keine Neuberechnung.':'Preis ausgeblendet')};
