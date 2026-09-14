"""Prepare non-live release branches from one explicitly approved native-QA artifact."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[2];QA=ROOT/'qa/atelier';REPO='Martin-Hausleitner/Luna-Stage'
def run(*args,cwd=ROOT):
    return subprocess.check_output(list(args),cwd=cwd,text=True).strip()
def api(path):return json.loads(run('gh','api',path))
approval=json.loads((QA/'approved-release.json').read_text())
if approval.get('visual')!='PASS':raise ValueError('No approved visual review')
run_id=int(approval['run_id']);expected=approval['runtime_sha256']
if not re.fullmatch('[0-9a-f]{64}',expected):raise ValueError('Invalid runtime SHA')
workflow=api(f'repos/{REPO}/actions/runs/{run_id}')
if workflow['conclusion']!='success' or workflow['head_branch']!='atelier-live-20260914':raise ValueError('The approved QA run did not succeed on the isolated branch')
for branch,key in [('main','expected_main'),('gh-pages','expected_pages')]:
    if api(f'repos/{REPO}/git/ref/heads/{branch}')['object']['sha']!=approval[key]:raise ValueError('Concurrent change on '+branch+'; re-review required')
artifact=Path(tempfile.mkdtemp(prefix='luna-approved-'))
run('gh','run','download',str(run_id),'--repo',REPO,'--name','Luna-Stage-Atelier-QA','--dir',str(artifact))
html=artifact/'Luna-Stage.html';data=html.read_bytes()
if hashlib.sha256(data).hexdigest()!=expected:raise ValueError('Downloaded runtime differs from approved source')
report=json.loads((artifact/'qa/atelier/acceptance-report.json').read_text())
if report.get('result')!='PASS' or report.get('source_sha256')!=expected or not all(report['checks'].values()):raise ValueError('Native acceptance did not pass for these bytes')
if report.get('baked_fallback_frames')!=6:raise ValueError('New default-kitchen stills were not baked')
output=ROOT/'release-output';output.mkdir(exist_ok=True);package=output/'Luna-Stage';package.mkdir(exist_ok=True)
shutil.copy(html,package/'Luna-Stage.html');shutil.copy(ROOT/'LICENSE',package/'LICENSE');(package/'.nojekyll').touch()
shutil.copytree(artifact/'qa/atelier',package/'qa/atelier')
pq=package/'qa/atelier'
# Retain final runtime sources, tests and evidence, not bootstrap patch instructions.
for name in ['fixes.py','publish.py','approved-release.json','probe_only.py','gpu-probe.html','check.js']:
    (pq/name).unlink(missing_ok=True)
(pq/'embedded-stills.json').write_text(re.search(r'const embeddedStills=(\[.*?\]);',data.decode(),re.S).group(1))
shutil.copy(QA/'clean_build.py',pq/'build.py');(pq/'clean_build.py').unlink(missing_ok=True)
shutil.copy(QA/'VISION.md',pq/'VISION.md')
shutil.copy(QA/'README-release.md',package/'README.md')
for image in (pq/'screenshots').glob('*.png'):
    if not image.name.startswith('raw-'):shutil.copy(image,package/'qa'/image.name)
receipt={'runtime_sha256':expected,'bytes':len(data),'qa_run':run_id,'qa_commit':workflow['head_sha'],'local_browser':'PASS','visual':'PASS','pages':'PENDING LIVE VERIFICATION','gpu':report.get('gpu'),'checks':report['checks'],'film_wall_seconds':report.get('film_wall_seconds'),'approval':approval}
(pq/'release-integrity.json').write_text(json.dumps(receipt,indent=2))
rebuild=json.loads(run('python',str(pq/'build.py'),cwd=package));receipt['offline_rebuild']=rebuild['offline_rebuild']
(pq/'release-integrity.json').write_text(json.dumps(receipt,indent=2))
readme=(package/'README.md').read_text();readme+='\n## Verified release bytes\n\nRuntime SHA-256: `'+expected+'`. The native browser suite and independent visual review refer to these bytes.\n\nOn software adapters, the runtime transfers **actual WebGPU-rendered pixels** to a Canvas2D presentation surface to work around Vulkan/compositor interoperability. This is not the no-WebGPU still fallback. Hardware adapters keep direct WebGPU presentation. Software tests do not measure physical-GPU frame rates.\n\nRun `python3 qa/atelier/build.py` for a fully offline byte-verified rebuild.\n';(package/'README.md').write_text(readme)
run('git','fetch','origin','main','gh-pages')
run('git','config','user.name','Martin Hausleitner');run('git','config','user.email','55828102+Martin-Hausleitner@users.noreply.github.com')
source_branch='atelier-release-'+expected[:10];pages_branch='atelier-pages-'+expected[:10]
commits={}
for base,branch,role in [('main',source_branch,'source'),('gh-pages',pages_branch,'pages')]:
    work=Path(tempfile.mkdtemp(prefix='luna-'+role+'-'));run('git','worktree','add','-b',branch,str(work),'origin/'+base)
    # Related old QA remains in the Git history; new canonical QA is version-specific.
    if (work/'qa').exists():shutil.rmtree(work/'qa')
    shutil.copytree(package/'qa',work/'qa')
    for name in ['README.md','LICENSE','.nojekyll']:shutil.copy(package/name,work/name)
    if role=='source':shutil.copy(html,work/'Luna-Stage.html')
    else:
        shutil.copy(html,work/'index.html')
        if (work/'Luna-Stage.html').exists():(work/'Luna-Stage.html').unlink()
    run('git','add','--all',cwd=work)
    run('git','commit','-m','LUNA STAGE Atelier: verified live kitchen design, native WebGPU, embedded surfaces',cwd=work)
    commits[role]=run('git','rev-parse','HEAD',cwd=work)
    run('git','push','origin','HEAD:refs/heads/'+branch,cwd=work)
result={'runtime_sha256':expected,'source_branch':source_branch,'pages_branch':pages_branch,'source_commit':commits['source'],'pages_commit':commits['pages'],'expected_main':approval['expected_main'],'expected_pages':approval['expected_pages'],'live_branches_changed':False}
(output/'release-candidate.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
