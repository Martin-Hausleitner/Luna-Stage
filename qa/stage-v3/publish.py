#!/usr/bin/env python3
from pathlib import Path
import os,json,subprocess,hashlib,shutil,sys
ROOT=Path(__file__).resolve().parents[2];cfg=json.loads((ROOT/'qa/stage-v3/PUBLISH.json').read_text());repo=os.environ['GITHUB_REPOSITORY']
def api(path):return json.loads(subprocess.check_output(['gh','api',path],text=True))
def git(*args,cwd=ROOT):return subprocess.check_output(['git',*args],cwd=cwd,text=True).strip()
run=api(f'repos/{repo}/actions/runs/{cfg["run_id"]}');assert run['head_sha']==cfg['tested_commit'];assert run['conclusion']=='success'
# actions/download-artifact handles signed storage URLs without leaking API credentials.
incoming=ROOT/'_reviewed';assert hashlib.sha256((incoming/'Luna-Stage.html').read_bytes()).hexdigest()==cfg['source_sha256']
release=ROOT/'_release';subprocess.run([sys.executable,'qa/stage-v3/assemble.py','--input',str(incoming),'--output',str(release),'--source-sha256',cfg['source_sha256']],cwd=ROOT,check=True)
assembled=json.loads((release/'qa/v3/assembly.json').read_text());assert assembled['assembled_sha256']==cfg['assembled_sha256'],assembled
# Guard both unrelated concurrent changes and the canonical kitchen runtime.
git('fetch','origin','main','gh-pages');assert git('rev-parse','origin/main')==cfg['expected_main_commit']
assert git('rev-parse','origin/main:Luna-Stage.html')==cfg['expected_runtime_blob'];assert git('rev-parse','origin/gh-pages:index.html')==cfg['expected_pages_index_blob']
git('config','user.name','Martin Hausleitner');git('config','user.email','55828102+Martin-Hausleitner@users.noreply.github.com')
main=ROOT/'_publish_main';pages=ROOT/'_publish_pages';git('worktree','add','--detach',str(main),'origin/main');git('worktree','add','--detach',str(pages),'origin/gh-pages')
for target in [main,pages]:
 for file in release.rglob('*'):
  if not file.is_file():continue
  dest=target/file.relative_to(release);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,dest)
 for name in ['stage-v2','stage-v3']:
  for file in (ROOT/'qa'/name).glob('*.py'):
   dest=target/'qa'/name/file.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,dest)
shutil.copy2(release/'Luna-Stage.html',pages/'index.html')
git('add','Luna-Stage.html','README.md','LICENSE','.nojekyll','qa',cwd=main);git('commit','-m','Ship detailed LUNA STAGE 3.2: native 3D foliage, materials, LEDs and verified controls',cwd=main);main_sha=git('rev-parse','HEAD',cwd=main);git('push','origin','HEAD:main',cwd=main)
git('add','index.html','Luna-Stage.html','README.md','LICENSE','.nojekyll','qa',cwd=pages);git('commit','-m','Publish reviewed detailed native kitchen HTML and its evidence',cwd=pages);pages_sha=git('rev-parse','HEAD',cwd=pages);git('push','origin','HEAD:gh-pages',cwd=pages)
receipt={'main_commit':main_sha,'pages_commit':pages_sha,'source_sha256':assembled['assembled_sha256'],'reviewed_run':cfg['run_id'],'pages_index_identical':(pages/'index.html').read_bytes()==(main/'Luna-Stage.html').read_bytes(),'unrelated_main_index_preserved':git('rev-parse','HEAD:index.html',cwd=main)==git('rev-parse',cfg['expected_main_commit']+':index.html'),'result':'PUSHED; live verification recorded separately'}
(release/'qa/v3/publication.json').write_text(json.dumps(receipt,indent=2));shutil.make_archive(str(ROOT/'Luna-Stage-3.2'),'zip',release);print(json.dumps(receipt,indent=2))
