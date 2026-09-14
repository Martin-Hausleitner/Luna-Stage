from pathlib import Path
p=Path(__file__).with_name('frame.py');s=p.read_text()
a="version:Luna.gpu.version})";assert a in s;s=s.replace(a,"version:Luna.gpu.version,presentation:Luna.gpu.presentation})",1)
a="page.screenshot(path=str(out/(name+'.png')));record('frame',"
b="page.screenshot(path=str(out/(name+'.png')));assert min(ImageStat.Stat(Image.open(out/(name+'.png')).convert('RGB').crop((100,100,1820,800))).stddev)>10, 'Browser room is blank';r['checks']['browser_room_visible']=True;record('frame',"
assert a in s;s=s.replace(a,b,1)
a="  assert not r['errors'];assert not page.evaluate('Luna.gpu.errors');r['checks']['zero_gpu_js_errors']=True"
b="""  if ch==4:
   page.evaluate('Luna.scene.price=false;Luna.scene.ceo=false;Luna.gpu.invalidate()')
   image(page.evaluate('Luna.gpu.captureFrame(4,1920,1080)'),'fallback-price-clean.png');r['checks']['clean_fallback_frame']=True
  if ch==6:
   page.evaluate('Luna.gpu.snapshotBusy=false')
   with page.expect_download(timeout=600000) as event:page.keyboard.press('s')
   event.value.save_as(str(out/'STAGE-Berger-Abend.png'));page.wait_for_function('!Luna.gpu.snapshotBusy',timeout=10000);page.evaluate('Luna.gpu.snapshotBusy=true')
   im=Image.open(out/'STAGE-Berger-Abend.png');assert im.size==(1920,1080);assert min(ImageStat.Stat(im.convert('RGB')).stddev)>10
   assert page.evaluate('Luna.scene.ceo');r['checks']['snapshot_png_and_restore']=True
  if ch==0:
   film=b.new_page(viewport={'width':320,'height':180});film.goto(f'http://127.0.0.1:{srv.server_port}/Luna-Stage.html')
   film.wait_for_function('window.Luna && Luna.gpu.firstGPUMS',timeout=120000);started=time.monotonic();seen=set()
   while time.monotonic()-started<65:
    state=film.evaluate('({t:Luna.cam.time,c:Luna.cam.chapter,playing:Luna.cam.playing})');seen.add(state['c'])
    if state['t']>=48:break
    film.wait_for_timeout(200)
   elapsed=time.monotonic()-started;assert state['t']>=48 and 40<elapsed<55,(state,elapsed);assert seen==set(range(6)),seen
   r['film_seconds']=elapsed;r['checks']['six_chapter_film_wall_clock']=True;film.close()
  assert not r['errors'];assert not page.evaluate('Luna.gpu.errors');r['checks']['zero_gpu_js_errors']=True"""
assert a in s;s=s.replace(a,b,1);p.write_text(s)
