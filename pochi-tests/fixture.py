"""Deterministic browser checks for long cooldowns. GitHub URL is fulfilled locally.
This fixture supplies the storage/asset bridge, real DOM, sprite files and production scripts."""
import json
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from live import EXT, HOST, OUT, URL, profile

def run():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp, sync_playwright() as pw:
        ctx = profile(pw,Path(tmp)/'local',False)
        page = ctx.pages[0]
        def local(route):
            name = route.request.url.split('/')[-1]
            if name.endswith('.png'):
                return route.fulfill(path=EXT/'sprites'/name,content_type='image/png')
            route.fulfill(content_type='text/html',body="""<!doctype html><main>
                <div class="js-calendar-graph" style="position:absolute;left:15%;top:65%;
                 width:65%;height:50px;border:1px solid green"></div></main>""")
        page.route('**/*',local)
        page.goto(URL)
        page.clock.install()
        page.evaluate("""() => {
          window.chrome = window.chrome || {};
          chrome.runtime = {getURL:path => location.origin+'/'+path};
          chrome.storage = {local:{get:async d=>({...d,reminders:true})},onChanged:{addListener(){}}};
          Object.defineProperty(document,'hidden',{configurable:true,get:()=>window.testHidden || false});
          Math.random = () => 0;
        }""")
        for name in ['gait.js','profile.js']:
            page.add_script_tag(path=EXT/name)
        page.locator(HOST).wait_for()
        page.evaluate("""() => {
          window.lines=[]; window.poses=new Set(); window.frames=0; window.bubblesFit=true;
          const shadow=document.querySelector('#pochi-profile-companion').shadowRoot;
          new MutationObserver(()=>{const img=shadow.querySelector('img');
            poses.add(img.src.split('/').pop()); frames++;
            const note=shadow.querySelector('.note'), text=note.textContent;
            if(text && !note.hidden) {
              const r=note.getBoundingClientRect();
              bubblesFit &&= r.left>=0 && r.right<=innerWidth && r.top>=0 &&
                r.bottom<img.getBoundingClientRect().bottom && getComputedStyle(note).pointerEvents==='none';
            }
            if(text && lines.at(-1)!==text) lines.push(text);
          }).observe(shadow,{subtree:true,attributes:true,childList:true});
        }""")
        page.evaluate("() => { window.testHidden=true; document.dispatchEvent(new Event('visibilitychange')); }")
        page.clock.fast_forward(21*60000)
        quiet = page.evaluate('frames')
        page.clock.run_for(5000)
        assert page.evaluate('frames') == quiet
        page.evaluate("() => { window.testHidden=false; document.dispatchEvent(new Event('visibilitychange')); }")
        page.clock.run_for(65000)
        assert 'Had water?' not in page.evaluate('lines')
        assert 'reading.png' in page.evaluate('[...poses]')
        page.clock.fast_forward(20*60000)
        page.clock.run_for(30000)
        assert page.evaluate('lines').count('Had water?')==1, page.evaluate('lines')
        page.clock.fast_forward(20*60000)
        page.clock.run_for(30000)
        assert any('stretch break' in s for s in page.evaluate('lines'))
        assert page.evaluate('bubblesFit')
        observed = page.evaluate('lines')
        # Same document Turbo/Navigation API transitions and repeated events.
        page.evaluate("history.pushState({},'', '/unrelated')")
        assert not page.locator(HOST).count()
        page.evaluate("history.pushState({},'', '/sushan5140')")
        page.evaluate("document.dispatchEvent(new Event('turbo:load'))")
        assert page.locator(HOST).count()==1
        ctx.close()
    result={'simulated_hidden_minutes':21,'observed_lines':observed,
            'checked':'hidden timer cancellation, visible-time reminder, seated calendar, same-document leave/return'}
    print(json.dumps(result,indent=2))
    (OUT/'fixture-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
    run()
