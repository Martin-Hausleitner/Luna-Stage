from pathlib import Path
import functools,http.server,json,threading
from playwright.sync_api import sync_playwright
from gpu_probe import select_browser
ROOT=Path(__file__).resolve().parents[2];QA=ROOT/'qa/atelier'
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
    with sync_playwright() as p:
        config=select_browser(p,QA,f'http://127.0.0.1:{server.server_port}')
        (QA/'working-browser.json').write_text(json.dumps(config,indent=2))
        print('WORKING_BROWSER',json.dumps(config),flush=True)
finally:server.shutdown()
