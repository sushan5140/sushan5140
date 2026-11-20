/* Native tab visibility check using a fresh Chromium for Testing instance.
   Run with Node 22+ and CHROMIUM_EXECUTABLE. Connect only to our own local pipe. */
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');
const {spawn} = require('node:child_process');
const {once} = require('node:events');
const sleep = ms => new Promise(resolve => setTimeout(resolve,ms));
async function run() {
  const ext = path.resolve(__dirname,'../pochi-extension');
  const dir = await fs.mkdtemp(path.join(os.tmpdir(),'pochi-visibility-'));
  const browser = spawn(process.env.CHROMIUM_EXECUTABLE,[
    '--user-data-dir='+dir,'--no-first-run','--no-default-browser-check','--disable-backgrounding-occluded-windows',
    '--disable-extensions-except='+ext,'--load-extension='+ext,
    '--remote-debugging-pipe','about:blank'
  ],{stdio:['ignore','ignore','ignore','pipe','pipe']});
  const closed = once(browser,'exit');
  let sequence = 0, pending = new Map(), buffer = '';
  browser.stdio[4].setEncoding('utf8');
  browser.stdio[4].on('data',data => {
    buffer += data;
    let i;
    while ((i=buffer.indexOf('\0'))>=0) {
      const packet = JSON.parse(buffer.slice(0,i));
      buffer = buffer.slice(i+1);
      const callback = pending.get(packet.id);
      if (callback) { pending.delete(packet.id); callback(packet); }
    }
  });
  function send(method,params={},sessionId) {
    const id = ++sequence;
    return new Promise((resolve,reject)=>{
      const timer = setTimeout(()=>{ pending.delete(id); reject(Error(method+' timed out')); },15000);
      pending.set(id,packet=>{
        clearTimeout(timer);
        if (packet.error) reject(Error(packet.error.message)); else resolve(packet.result);
      });
      browser.stdio[3].write(JSON.stringify({id,method,params,sessionId})+'\0');
    });
  }
  try {
    const {targetId} = await send('Target.createTarget',{url:'https://github.com/sushan5140'});
    const {sessionId} = await send('Target.attachToTarget',{targetId,flatten:true});
    const read = async expression => (await send('Runtime.evaluate',{expression,returnByValue:true},sessionId)).result.value;
    const host = "document.querySelector('#pochi-profile-companion')";
    for(let n=0;n<120 && !await read('Boolean('+host+')');n++) await sleep(500);
    assert.ok(await read('Boolean('+host+')'));
    await send('Target.activateTarget',{targetId});
    await send('Page.bringToFront',{},sessionId);
    await sleep(500);
    assert.equal(await read('document.visibilityState'),'visible');
    // Install only a passive verification observer in the disposable page.
    await read(`window.pochiMutations=0; new MutationObserver(m=>window.pochiMutations+=m.length)
      .observe(${host}.shadowRoot,{attributes:true,subtree:true,childList:true});`);
    const blank = await send('Target.createTarget',{url:'about:blank',newWindow:false});
    await send('Target.activateTarget',{targetId:blank.targetId});
    await sleep(400);
    assert.equal(await read('document.visibilityState'),'hidden');
    const before = await read('pochiMutations');
    await sleep(4500);
    assert.equal(await read('pochiMutations'),before);
    await send('Target.activateTarget',{targetId});
    await sleep(500);
    assert.equal(await read('document.visibilityState'),'visible');
    assert.ok(await read('pochiMutations')>before);
    await send('Target.closeTarget',{targetId});
    let open = true;
    for (let n=0;n<30 && open;n++) {
      await sleep(200);
      open = (await send('Target.getTargets')).targetInfos.some(t=>t.targetId===targetId);
    }
    assert.equal(open,false,'the original page target should close');
    assert.equal(JSON.parse(await fs.readFile(path.join(ext,'manifest.json'),'utf8')).background,undefined);
    console.log('PASS: native hidden tab, zero overlay mutations for 4.5 s, visible resume, closed target, no background entry point.');
  } finally {
    try { await send('Browser.close'); } catch { browser.kill(); }
    await closed;
    await fs.rm(dir,{recursive:true,force:true,maxRetries:4,retryDelay:250});
  }
}
run().catch(error=>{ console.error(error); process.exitCode=1; });
