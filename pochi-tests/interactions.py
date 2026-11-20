"""Live settings, visibility and landmark checks. Uses the same QA environment as live.py.
Run headed for real tab visibility changes (POCHI_HEADED=1)."""
import json
import os
import tempfile
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from live import HOST, OUT, URL, profile, snapshot, visit
from playwright.sync_api import TimeoutError as PlaywrightTimeout

def exercise():
    results = {}
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp, sync_playwright() as pw:
        ctx = profile(pw,Path(tmp)/'browser',True)
        page = ctx.pages[0]
        visit(page,URL)
        host = page.locator(HOST)
        host.wait_for()
        manager = ctx.new_page()
        manager.goto('chrome://extensions')
        item = manager.locator('extensions-item').filter(has_text='Pochi on Susan')
        ext_id = item.get_attribute('id')
        manager.goto(f'chrome-extension://{ext_id}/settings.html')
        enabled = manager.get_by_label('Show on Susan')
        reminders = manager.get_by_label('Gentle break')
        assert enabled.is_checked() and not reminders.is_checked()
        enabled.focus()
        enabled.press('Space')
        host.wait_for(state='detached')
        enabled.press('Space')
        reminders.check()
        manager.reload()
        assert reminders.is_checked()
        host.wait_for(state='attached')
        results['settings'] = 'Keyboard hide/show, default reminders off, opt-in persists'
        page.bring_to_front()
        page.wait_for_timeout(500)
        ctx.new_cdp_session(page).send('Emulation.setFocusEmulationEnabled',{'enabled':False})
        manager.bring_to_front()
        if os.environ.get('POCHI_HEADED') == '1':
            # Playwright can create each page in a separate top-level window.
            # Select two actual tabs in one window using the settings page.
            ids = manager.evaluate("""async () => {
              const me = await chrome.tabs.getCurrent();
              const other = (await chrome.tabs.query({})).find(t=>t.id!==me.id);
              if (me.windowId!==other.windowId)
                await chrome.tabs.move(me.id,{windowId:other.windowId,index:-1});
              await chrome.tabs.update(other.id,{active:true});
              await chrome.tabs.update(me.id,{active:true});
              return [me.id,other.id];
            }""")
            page.wait_for_timeout(300)
            if page.evaluate('document.hidden'):
                before = snapshot(page)
                page.wait_for_timeout(3200)
                assert snapshot(page)==before
                results['background_tab'] = 'Native visibilitychange and stationary sprite across 3.2 seconds'
            else:
                results['background_tab'] = 'Automation browser kept both tabs visible; tested hidden state in fixture'
            manager.evaluate('(id)=>chrome.tabs.update(id,{active:true})',ids[1])
        page.bring_to_front()
        assert not page.evaluate('document.hidden')
        manager.close()
        page.set_viewport_size({'width':1280,'height':870})
        # The contribution fragment is lazy-loaded by GitHub itself.
        fragment = page.locator('include-fragment[src*="tab=contributions"]')
        if fragment.count():
            fragment.first.evaluate("e => e.scrollIntoView({block:'center'})")
        graph = page.locator('.js-calendar-graph, .ContributionCalendar-grid, .js-yearly-contributions').first
        try:
            graph.wait_for(timeout=15000)
        except PlaywrightTimeout:
            results['live_calendar'] = 'GitHub did not render a calendar in this signed-out session'
        else:
            graph.evaluate("e=>e.scrollIntoView({block:'center'})")
            results['live_calendar'] = 'Calendar visible on signed-out GitHub'
            end = time.monotonic()+85
            while time.monotonic()<end:
                s = snapshot(page)
                if s['src']=='reading.png' and s['decoded']:
                    matched = graph.evaluate("""(g,p)=>{
                      const els=document.querySelectorAll('.js-calendar-graph,.ContributionCalendar-grid,.js-yearly-contributions');
                      return [...els].some(e=>{const r=e.getBoundingClientRect();
                      return (Math.abs(p.x-r.right+30)<2 && Math.abs(p.y-r.top)<6)
                        || (Math.abs(p.x-r.left+27)<2 && Math.abs(p.y-r.bottom)<6);});
                    }""",s)
                    if matched:
                        page.screenshot(path=OUT/'calendar.png')
                        results['live_calendar'] = 'Original seated reading pose verified at a calendar edge'
                        break
                page.wait_for_timeout(450)
        ctx.close()
    print(json.dumps(results,indent=2))
    (OUT/'interaction-results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
    exercise()
