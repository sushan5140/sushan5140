"""Run with playwright installed and Chromium for Testing available.
CHROMIUM_EXECUTABLE selects a specific binary. POCHI_EVIDENCE selects the output directory.
Use a temporary, signed-out browser profile; no operational GitHub credentials."""
import json
import os
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "pochi-extension"
OUT = Path(os.environ.get("POCHI_EVIDENCE", "pochi-evidence"))
URL = "https://github.com/sushan5140"
HOST = "#pochi-profile-companion"
OUT.mkdir(exist_ok=True, parents=True)

def snapshot(page):
    return page.locator(HOST).evaluate("""h => {
      const img=h.shadowRoot.querySelector('img'), r=img.getBoundingClientRect();
      return {x:r.x+r.width/2, y:r.bottom, src:img.src.split('/').pop(),
        decoded:img.complete && img.naturalWidth>0, flip:img.style.transform,
        through:document.elementFromPoint(r.x+r.width/2,r.y+r.height/2)!==h};
    }""")

def metrics(cdp):
    return {m['name']:m['value'] for m in cdp.send('Performance.getMetrics')['metrics']}

def measure(page, cdp, seconds):
    initial = metrics(cdp)
    page.wait_for_timeout(seconds*1000)
    final = metrics(cdp)
    return {k:round(final[k]-initial[k],4) for k in
            ['TaskDuration','ScriptDuration','LayoutCount','RecalcStyleCount']}

def profile(p, profile_dir, enabled):
    args = []
    if enabled:
        args = [f'--disable-extensions-except={EXT}', f'--load-extension={EXT}']
    return p.chromium.launch_persistent_context(profile_dir, channel='chromium',
        executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or None,
        args=args, headless=os.environ.get('POCHI_HEADED') != '1',
        viewport={'width':1280,'height':870}, device_scale_factor=1)

def visit(page,url):
    response = page.goto(url,wait_until='domcontentloaded',timeout=60000)
    assert response and response.ok, (url, response and response.status)
    page.locator('main').first.wait_for()

def run():
    results = {}
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp, sync_playwright() as pw:
        plain = profile(pw, Path(tmp)/'plain',False)
        page = plain.pages[0]
        visit(page, URL)
        assert not page.locator(HOST).count()
        summaries = page.locator('article details > summary')
        assert summaries.count() >= 3
        summaries.first.click()
        assert summaries.first.evaluate('s=>s.parentNode.open')
        gif = page.locator('article img[alt*="original Pochi"]').first
        gif.scroll_into_view_if_needed()
        page.wait_for_function("""() => [...document.querySelectorAll('article img')]
          .some(i=>i.alt.includes('original Pochi') && i.complete && i.naturalWidth>0)""")
        results['ordinary_visitor'] = 'Profile, existing GIF and disclosure control verified'
        plain.close()
        ctx = profile(pw, Path(tmp)/'extension',True)
        page = ctx.pages[0]
        visit(page, URL)
        page.locator(HOST).wait_for()
        page.wait_for_function("""() => document.querySelector('#pochi-profile-companion')
          ?.shadowRoot.querySelector('img')?.naturalWidth > 0""")
        cdp = ctx.new_cdp_session(page)
        cdp.send('Performance.enable')
        results['browser'] = cdp.send('Browser.getVersion')['product']
        page.screenshot(path=OUT/'profile.png',animations='allow')
        samples = []
        deadline = time.monotonic()+28
        while time.monotonic()<deadline:
            item = snapshot(page)
            samples.append(item)
            if item['src'].startswith('walk_') and item['decoded']:
                if 'walking_performance_1s' not in results:
                    page.screenshot(path=OUT/'walking.png',animations='allow')
                    results['walking_performance_1s'] = measure(page,cdp,1)
            steps = [s for s in samples if s['src'].startswith('walk_') and s['decoded']]
            if (len({s['src'] for s in steps})>=3 and
                max([s['x'] for s in samples])-min([s['x'] for s in samples])>65):
                break
            page.wait_for_timeout(110)
        assert all(s['through'] for s in samples)
        assert len({s['src'] for s in steps}) >= 3, samples[-4:]
        span = max(s['x'] for s in samples)-min(s['x'] for s in samples)
        assert span>65
        results['walk'] = {'horizontal_span_px':round(span,1),'frames':sorted({s['src'] for s in steps})}
        page.evaluate("window.scrollBy(0,510)")
        page.wait_for_timeout(450)
        page.set_viewport_size({'width':900,'height':660})
        page.wait_for_timeout(450)
        spot = snapshot(page)
        assert 0<spot['x']<900 and 0<spot['y']<680 and spot['through'], spot
        page.emulate_media(reduced_motion='reduce')
        page.wait_for_timeout(400)
        initial = snapshot(page)
        results['reduced_motion_performance_3s'] = measure(page,cdp,3)
        assert snapshot(page)==initial, (snapshot(page),initial)
        assert page.locator(HOST).evaluate("h=>h.shadowRoot.getAnimations().length") == 0
        page.screenshot(path=OUT/'resting.png')
        repo = page.locator('article a[href="https://github.com/sushan5140/Pochi"]').first
        repo.click()
        page.wait_for_url('**/sushan5140/Pochi')
        page.locator(HOST).wait_for(state='detached')
        page.go_back(wait_until='domcontentloaded')
        page.locator(HOST).wait_for()
        visit(page,URL+'?tab=repositories')
        page.locator(HOST).wait_for()
        visit(page,'https://github.com/github')
        assert not page.locator(HOST).count()
        visit(page,URL+'/Pochi')
        assert not page.locator(HOST).count()
        visit(page,URL)
        page.locator(HOST).wait_for()
        page.close()
        assert not ctx.service_workers and not ctx.background_pages
        ctx.close()
        results['lifecycle'] = 'Profile queries, repository click, Back, unrelated account, tab close'
    print(json.dumps(results,indent=2))
    (OUT/'live-results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')

if __name__ == '__main__':
    run()
