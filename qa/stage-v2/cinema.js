// Fifty authored additional real-time sequences. Original six-chapter film is unchanged.
const filmGroups=['Raum','Holz','Stein','Licht','Messing','Kochen','Oberflächen','Wohnen','Entscheidung','Ruhe'];
const shots=[
 ['Vom Vorraum ins Zuhause',0,[3.70,1.72,5.95],[3.02,1.70,4.90],[-.25,1.28,-.55],51,.48,0],
 ['Die klare Linie',0,[.30,1.64,4.45],[-.25,1.62,4.18],[.05,1.48,-2.39],49,.36,0],
 ['Insel im Raum',0,[2.96,1.69,3.53],[2.47,1.65,3.10],[.15,.96,.30],48,.58,0],
 ['Blick von der Fensterseite',0,[-2.18,1.76,3.39],[-1.90,1.66,2.98],[.42,1.20,-1.15],51,.20,0],
 ['Ein Raum, zwei Zonen',0,[3.58,2.48,4.70],[3.29,2.30,4.42],[.05,.92,-.30],52,.61,0],
 ['Die gerillte Eiche',1,[.38,1.20,1.28],[.08,1.10,1.25],[.18,.63,.92],38,.14,0],
 ['Faser im Streiflicht',1,[1.88,1.20,1.69],[1.70,1.09,1.46],[.63,.58,.91],40,.09,0],
 ['Sechs Fronten, eine Maserung',1,[1.17,1.12,-.97],[.76,1.07,-1.09],[.06,.56,-2.03],47,.22,0],
 ['Nussbaum in der Tiefe',1,[2.43,1.69,3.66],[2.22,1.61,3.38],[.02,1.06,-.38],47,.59,2],
 ['Raucheiche am Abend',1,[2.48,1.65,3.59],[2.18,1.61,3.30],[.12,1.01,-.45],48,.86,5],
 ['Die weiche Steinkante',2,[1.96,1.41,1.64],[1.82,1.32,1.49],[1.25,.935,.77],38,.26,0],
 ['Vom Stein zum Boden',2,[2.41,1.08,2.31],[2.24,.98,2.12],[1.52,.53,.62],39,.61,0],
 ['Licht auf dem Schliff',2,[.45,1.64,2.30],[.22,1.53,2.14],[.20,.963,.20],39,.43,1],
 ['Die mineralische Fläche',2,[-.33,2.42,1.96],[-.56,2.27,1.82],[.05,.955,.30],43,.18,0],
 ['Rückwand ohne Unterbrechung',2,[.46,1.65,-1.17],[.02,1.66,-1.18],[.0,1.30,-2.72],42,.72,0],
 ['Erstes Licht',3,[3.06,1.87,4.68],[2.92,1.82,4.43],[-.25,1.22,-.40],50,.015,0],
 ['Ein heller Vormittag',3,[-1.70,1.78,3.69],[-1.48,1.72,3.41],[.28,1.17,-.73],51,.17,1],
 ['Goldene Stunde',3,[2.65,1.74,4.30],[2.37,1.70,4.09],[-.15,1.16,-.45],50,.52,0],
 ['Wenn die Leuchten übernehmen',3,[3.17,1.89,4.73],[2.94,1.82,4.41],[-.18,1.23,-.40],50,.91,0],
 ['Blaue Stunde, warmes Zuhause',3,[2.81,1.75,4.22],[2.55,1.74,4.04],[-.05,1.22,-.49],49,1,0],
 ['Die Kurve der Armatur',4,[-.01,1.52,-1.10],[-.22,1.48,-1.21],[-.53,1.16,-2.53],36,.23,0],
 ['Gebürstetes Messing',4,[-.05,1.41,-1.22],[-.25,1.42,-1.31],[-.53,1.27,-2.55],30,.58,0],
 ['Das Becken ist eingelassen',4,[-.16,1.98,-1.36],[-.36,1.87,-1.42],[-.55,.82,-2.40],38,.31,1],
 ['Kleine Bewegung, grosser Unterschied',4,[-.60,1.54,-1.18],[-.42,1.49,-1.29],[-.285,1.05,-2.68],34,.72,0],
 ['Metall im Abendlicht',4,[.11,1.49,-1.10],[-.13,1.46,-1.27],[-.53,1.22,-2.53],34,.93,3],
 ['Eine ruhige Kochzone',5,[1.32,1.90,-1.10],[1.13,1.78,-1.16],[.89,.99,-2.42],40,.24,0],
 ['Glas, nicht eine schwarze Fläche',5,[1.51,1.59,-1.02],[1.28,1.48,-1.13],[.89,.99,-2.42],38,.75,3],
 ['Der Backofen ist integriert',5,[3.22,1.77,-.31],[2.98,1.72,-.47],[2.28,1.46,-2.01],42,.66,0],
 ['Griff und Schattenfuge',5,[2.77,1.69,-1.04],[2.61,1.65,-1.11],[2.28,1.72,-2.00],33,.44,2],
 ['Bereit zum Kochen',5,[1.41,1.68,-.20],[1.13,1.64,-.39],[.04,1.08,-2.36],49,.37,0],
 ['Sand, seidenmatt',6,[2.51,1.76,3.82],[2.21,1.71,3.58],[.02,1.08,-.49],50,.28,1],
 ['Nussbaum, warm und dunkel',6,[2.44,1.74,3.83],[2.14,1.70,3.57],[.01,1.08,-.48],50,.43,2],
 ['Graphit mit Messing',6,[2.52,1.77,3.87],[2.24,1.70,3.57],[.02,1.09,-.49],50,.39,3],
 ['Salbei im Tageslicht',6,[2.52,1.79,3.87],[2.19,1.73,3.58],[.01,1.09,-.49],50,.21,4],
 ['Raucheiche mit Naturstein',6,[2.52,1.78,3.87],[2.21,1.70,3.55],[.01,1.08,-.49],50,.46,5],
 ['Ein Platz an der Insel',7,[1.68,1.22,3.12],[1.43,1.17,2.91],[.72,.66,1.62],43,.43,0],
 ['Gebogene Lehne, feines Gestell',7,[1.58,1.24,2.81],[1.44,1.20,2.64],[.94,.74,1.70],36,.32,0],
 ['Keramik und drei Früchte',7,[-.28,1.59,1.30],[-.48,1.47,1.13],[-.96,1.07,.14],36,.32,0],
 ['Die Olive am Fenster',7,[-1.11,1.72,2.41],[-1.35,1.69,2.19],[-2.58,1.12,.70],43,.27,0],
 ['Barfuss am Morgen',7,[1.60,.94,3.39],[1.31,.82,3.12],[.09,.04,1.65],45,.10,0],
 ['Ein Preis, mitten im Raum',8,[.94,2.70,3.47],[.70,2.58,3.25],[.12,.97,.25],47,.79,0],
 ['Die Zahl im Naturstein',8,[.62,2.48,2.80],[.42,2.39,2.65],[.27,.96,.36],44,.63,0],
 ['Sandlack, klar entschieden',8,[.86,2.71,3.53],[.66,2.61,3.28],[.12,.97,.25],47,.57,1],
 ['Material und Zusage',8,[1.24,2.76,3.57],[.97,2.67,3.33],[.12,.97,.25],47,.72,2],
 ['Ihr Zuhause, Ihr Entschluss',8,[.85,2.77,3.70],[.63,2.61,3.33],[.12,.97,.25],48,.87,0],
 ['Nach dem Gespräch',9,[3.40,2.03,5.48],[3.32,2.01,5.39],[-.30,1.32,-.52],53,.84,0],
 ['Still und hell',9,[3.23,1.91,5.13],[3.16,1.90,5.05],[-.25,1.28,-.48],52,.17,1],
 ['Nur der Raum',9,[.72,1.72,4.75],[.66,1.72,4.66],[.09,1.28,-.96],51,.56,0],
 ['Später Abend',9,[3.09,1.94,4.96],[3.00,1.91,4.86],[-.21,1.24,-.46],51,.98,2],
 ['Angekommen',9,[2.80,1.80,4.75],[2.75,1.79,4.69],[-.18,1.27,-.52],51,.78,0]
].map((s,i)=>({id:i,name:s[0],group:s[1],eye:s[2],end:s[3],to:s[4],fov:s[5],sun:s[6],material:s[7],duration:8+(i%3),price:s[1]===8,quiet:s[1]===9}));
Luna.cam.films=shots;Luna.cam.activeShot=-1;Luna.cam.shotPlaying=false;Luna.cam.shotTime=0;
const library=document.createElement('dialog');library.id='library';library.setAttribute('aria-labelledby','library-title');library.innerHTML='<div class="library-head"><div><span class="eyebrow">DIE FILMSAMMLUNG</span><h2 id="library-title">50 neue Blickwinkel.</h2><p>Echtzeit-Kamerasequenzen. Wählen Sie, was Sie erleben möchten.</p></div><button id="close-library" aria-label="Filmsammlung schliessen">Schliessen <span>Esc</span></button></div><div id="film-groups" role="tablist" aria-label="Filmthemen"></div><div id="film-cards" role="tabpanel" aria-live="polite"></div><div class="library-foot"><span>Eine Küche. Sechs Oberflächen. Ihr Licht.</span><button id="tour-original">Den 48-Sekunden-Film starten →</button></div>';
document.body.append(library);
const filmButton=document.createElement('button');filmButton.id='open-library';filmButton.textContent='Filmsammlung · 50';filmButton.title='V: 50 zusätzliche Kamerasequenzen';filmButton.setAttribute('aria-haspopup','dialog');$('chapters').append(filmButton);
const caption=document.createElement('div');caption.id='shot-caption';caption.setAttribute('aria-live','polite');$('rail').prepend(caption);
const groupEl=$('film-groups');let selectedGroup=0;
function populateFilms(group){selectedGroup=group;[...groupEl.children].forEach((b,i)=>{b.setAttribute('aria-selected',String(i===group));b.tabIndex=i===group?0:-1});$('film-cards').innerHTML='';shots.filter(s=>s.group===group).forEach(s=>{let b=document.createElement('button');b.className='film-card';b.dataset.shot=s.id;b.disabled=!Luna.gpu.ready;if(b.disabled)b.title='Diese Echtzeitsequenz benötigt WebGPU. Die sechs Standbilder bleiben verfügbar.';b.setAttribute('aria-label',s.name+', '+s.duration+' Sekunden, '+Luna.scene.palettes[s.material]);b.innerHTML='<span class="film-number">'+String(s.id+1).padStart(2,'0')+'</span><span class="film-title">'+s.name+'</span><span class="film-meta">'+Luna.scene.palettes[s.material]+' · '+s.duration+' s</span><span class="film-arrow" aria-hidden="true">↗</span>';b.onclick=()=>{closeLibrary();Luna.cam.playShot(s.id)};$('film-cards').append(b)});}
filmGroups.forEach((name,i)=>{let b=document.createElement('button');b.id='film-group-'+i;b.role='tab';b.textContent=name;b.onclick=()=>populateFilms(i);b.onkeydown=e=>{if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();let j=(i+(e.key==='ArrowRight'?1:9))%10;populateFilms(j);groupEl.children[j].focus()}};groupEl.append(b)});
function openLibrary(){Luna.cam.playing=false;Luna.cam.shotPlaying=false;Luna.hud.sync();populateFilms(selectedGroup);library.showModal();$('close-library').focus()}
function closeLibrary(){library.close();filmButton.focus()}
filmButton.onclick=openLibrary;$('close-library').onclick=closeLibrary;library.addEventListener('click',e=>{if(e.target===library)closeLibrary()});
$('tour-original').onclick=()=>{closeLibrary();Luna.cam.goto(0,false);Luna.cam.toggle()};
Luna.cam.stopShot=()=>{Luna.cam.shotPlaying=false;Luna.cam.activeShot=-1;caption.textContent='';document.body.classList.remove('shot-active');};
const originalGoto=Luna.cam.goto,originalSeek=Luna.cam.seek,originalToggle=Luna.cam.toggle;
Luna.cam.goto=(...args)=>{Luna.cam.stopShot();return originalGoto(...args)};
Luna.cam.seek=(...args)=>{Luna.cam.stopShot();return originalSeek(...args)};
Luna.cam.playShot=(id,play=true)=>{
 id=clamp(Math.floor(Number(id)||0),0,49);const s=shots[id],old={eye:[...Luna.cam.eye],to:[...Luna.cam.to],fov:Luna.cam.fov,sun:Luna.scene.sun};
 Luna.cam.playing=false;Luna.cam.transition=null;Luna.cam.manual=false;Luna.cam.chapter=s.quiet?5:s.price?4:s.group===6?3:2;Luna.cam.activeShot=id;Luna.cam.shotTime=0;Luna.cam.shotOld=old;Luna.cam.shotPlaying=play&&Luna.gpu.ready&&!matchMedia('(prefers-reduced-motion: reduce)').matches;
 Luna.scene.material=s.material;Luna.scene.sun=s.sun;Luna.scene.price=s.price;Luna.scene.ceo=false;
 if(!Luna.cam.shotPlaying){Luna.cam.eye=[...s.eye];Luna.cam.to=[...s.to];Luna.cam.fov=s.fov;}
 document.body.classList.add('shot-active');caption.textContent=String(id+1).padStart(2,'0')+' / 50  ·  '+s.name;Luna.hud.sync();Luna.gpu.invalidate();Luna.hud.announce(s.name);
};
Luna.cam.advanceShot=(dt)=>{
 if(!Luna.cam.shotPlaying||Luna.cam.activeShot<0)return false;const s=shots[Luna.cam.activeShot];Luna.cam.shotTime=Math.min(s.duration+.9,Luna.cam.shotTime+dt);const t=Luna.cam.shotTime,entry=smooth(clamp(t/.9)),phase=smooth(clamp((t-.9)/s.duration));
 const target=V.lerp(s.eye,s.end,phase),old=Luna.cam.shotOld;Luna.cam.eye=V.lerp(old.eye,target,entry);Luna.cam.to=V.lerp(old.to,s.to,entry);Luna.cam.fov=mix(old.fov,s.fov,entry);Luna.scene.sun=mix(old.sun,s.sun,entry);
 filmButton.style.setProperty('--clip-progress',clamp((t-.9)/s.duration));
 if(t>=s.duration+.9){Luna.cam.shotPlaying=false;Luna.hud.sync()}return true;
};
Luna.cam.toggle=()=>{if(Luna.cam.activeShot>=0){if(Luna.cam.shotTime>=shots[Luna.cam.activeShot].duration+.9){Luna.cam.playShot(Luna.cam.activeShot)}else{Luna.cam.shotPlaying=!Luna.cam.shotPlaying;Luna.hud.sync();Luna.gpu.invalidate()}}else originalToggle()};$('play').onclick=Luna.cam.toggle;
const originalSync=Luna.hud.sync;Luna.hud.sync=()=>{originalSync();const film=Luna.cam.activeShot>=0;if(film){controls.forEach(b=>b.setAttribute('aria-current','false'));$('play').textContent=Luna.cam.shotPlaying?'Ⅱ':'▷';$('play').setAttribute('aria-label',Luna.cam.shotPlaying?'Sequenz pausieren':'Sequenz abspielen')}$('room').setAttribute('aria-label','Küche der Familie Berger. '+Luna.scene.palettes[Luna.scene.material]+'. Berühren Sie eine Front für die nächste Oberfläche. Ziehen Sie zum Umsehen.');};
Luna.scene.selectMaterial=index=>{Luna.cam.stopShot();Luna.cam.playing=false;Luna.cam.transition=null;Luna.cam.manual=true;Luna.scene.material=clamp(Math.floor(index),0,5);Luna.hud.sync();Luna.store.write();Luna.gpu.invalidate();Luna.hud.hint(Luna.scene.palettes[Luna.scene.material]+' · M: nächste Oberfläche');Luna.hud.announce(Luna.scene.palettes[Luna.scene.material])};
const originalCycle=Luna.scene.cycle;Luna.scene.cycle=()=>{if(!Luna.gpu.ready){originalCycle();return}Luna.scene.selectMaterial((Luna.scene.material+1)%6)};
const originalPrice=Luna.scene.togglePrice;Luna.scene.togglePrice=()=>{Luna.cam.stopShot();return originalPrice()};
$('sun').addEventListener('input',()=>Luna.cam.stopShot());
for(const el of [$('room'),$('still')]){
 el.addEventListener('pointerdown',()=>{if(Luna.cam.activeShot>=0)Luna.cam.stopShot()},{capture:true});
 el.addEventListener('wheel',()=>Luna.cam.stopShot(),{passive:true});
 el.addEventListener('dblclick',e=>{if(!Luna.gpu.ready)return;const h=Luna.scene.pick(e.clientX,e.clientY);if(!h.object)return;Luna.cam.playing=false;Luna.cam.manual=true;Luna.cam.transition=null;Luna.cam.to=V.lerp(Luna.cam.to,h.point,.55);Luna.gpu.invalidate();Luna.hud.hint('Detailansicht · Ziehen zum Umsehen · Esc für die Gesamtansicht')});
}
addEventListener('keydown',e=>{
 if(e.ctrlKey||e.metaKey||e.altKey)return;
 if(library.open){if(e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();closeLibrary()}else if(e.key===' '){e.stopImmediatePropagation()}return;}
 if(e.target.tagName==='INPUT')return;let k=e.key.toLowerCase();
 if(k==='v'){e.preventDefault();e.stopImmediatePropagation();openLibrary()}
 if(k==='['||k===']'){e.preventDefault();e.stopImmediatePropagation();Luna.cam.playShot((Luna.cam.activeShot+(k===']'?1:49)+50)%50)}
},true);
const originalSnapshot=Luna.gpu.snapshot;Luna.gpu.snapshot=async()=>{const old={activeShot:Luna.cam.activeShot,shotTime:Luna.cam.shotTime,shotPlaying:Luna.cam.shotPlaying,shotOld:Luna.cam.shotOld};await originalSnapshot();Object.assign(Luna.cam,old);if(old.activeShot>=0){caption.textContent=String(old.activeShot+1).padStart(2,'0')+' / 50  ·  '+shots[old.activeShot].name;document.body.classList.add('shot-active')}Luna.hud.sync()};
if(params.has('shot'))Luna.cam.playShot(Number(params.get('shot'))-1,!params.has('paused'));
Luna.gpu.version='2.0';
