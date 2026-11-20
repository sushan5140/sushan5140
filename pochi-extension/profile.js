(() => {
  'use strict';
  const onProfile = () => location.origin === 'https://github.com' &&
    /^\/sushan5140\/?$/.test(location.pathname);
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const defaults = {enabled: true, reminders: false};
  const preferences = {...defaults};
  const between = (low, high) => low + Math.random() * (high - low);
  const clamp = (v, low, high) => Math.max(low, Math.min(high, v));
  const pick = items => items[Math.floor(Math.random() * items.length)];
  let companion;
  let suspended = false;
  let loaded = false;

  function createCompanion() {
    const host = document.createElement('div');
    host.id = 'pochi-profile-companion';
    const root = host.attachShadow({mode: 'open'});
    const style = document.createElement('style');
    style.textContent = `
      :host { all:initial !important; position:fixed !important; inset:0 !important;
        display:block !important; pointer-events:none !important; z-index:29 !important;
        overflow:hidden !important; contain:strict !important; }
      .pet { position:absolute; left:0; top:0; width:0; height:0; pointer-events:none; }
      .pet::before { content:""; position:absolute; left:-13px; bottom:-1px; width:26px;
        height:4px; border-radius:50%; background:radial-gradient(ellipse,#332d2645,transparent 72%); }
      img { position:absolute; bottom:0; left:0; width:auto; max-width:none;
        transform-origin:50% 100%; pointer-events:none; }
      .note { position:absolute; box-sizing:border-box; width:max-content; max-width:154px;
        background:#fffef7; color:#292b23; border:1px solid #69705b; padding:5px 8px;
        border-radius:9px; font:500 13px/1.4 system-ui,sans-serif; box-shadow:0 1px 3px #0002; }
      @media(forced-colors:active) { .note { background:Canvas; color:CanvasText; border-color:CanvasText; } }
    `;
    const pet = document.createElement('div');
    pet.className = 'pet';
    const img = document.createElement('img');
    img.alt = 'Pochi';
    img.draggable = false;
    const note = document.createElement('div');
    note.className = 'note';
    note.hidden = true;
    note.setAttribute('role','status');
    pet.append(img);
    root.append(style, pet, note);
    document.documentElement.append(host);

    const events = new AbortController();
    const signal = events.signal;
    // The source PNGs have different transparent foot margins. Register the
    // visible foot to the ledge and keep the character at a comparable scale.
    const register = {
      arms_crossed: [512,448,426], reading:[512,501,570], sleeping_pillow:[482,419,540],
      sleepy:[411,411,409], judging:[411,411,407], happy:[437,437,436], worried:[412,412,411]
    };
    let frameName, mirrored, height, x, y, leg, facing = 1, perch;
    let raf = 0, timer = 0, noteTimer = 0, layoutTimer = 0;
    let lastScroll = scrollY, lastFrame = 0, awakeSince = performance.now();
    let elapsed = 0, lastSpeech = 0, lastReminder = 0, reminderCount = 0;
    let firstWalk = true;
    let disposed = false;
    const activeTime = () => elapsed + (awakeSince === null ? 0 : performance.now() - awakeSince);
    const spriteHeight = () => innerWidth < 520 ? 58 : 76;
    function paint(name, mirror = false, bob = 0, stretch = 1) {
      if (frameName !== name || mirrored !== mirror || height !== spriteHeight()) {
        height = spriteHeight();
        if (frameName !== name) img.src = chrome.runtime.getURL('sprites/' + name + '.png');
        frameName = name;
        mirrored = mirror;
        const [canvas, foot, body] = register[name] ||
          (name.startsWith('walk_front') ? [627,616,604] :
           name.startsWith('walk_back') ? [607,595,585] : [609,595,582]);
        img.style.height = height * canvas / body + 'px';
        img.style.bottom = -height * (canvas - foot) / body + 'px';
      }
      img.style.transform = 'translateX(-50%) scale(' + (mirror ? -1 : 1) + ',' + stretch + ')';
      pet.style.transform = 'translate3d(' + x.toFixed(1) + 'px,' + (y + bob).toFixed(1) + 'px,0)';
    }
    function silence() {
      clearTimeout(noteTimer);
      note.textContent = '';
      note.hidden = true;
    }
    function cancel() {
      cancelAnimationFrame(raf);
      clearTimeout(timer);
      clearTimeout(layoutTimer);
      silence();
      leg = null;
    }
    const selectors = [
      ['graph', '.js-calendar-graph, .ContributionCalendar-grid, .js-yearly-contributions'],
      ['repository', '.pinned-item-list-item .Box, #user-repositories-list li'],
      ['section', 'main article hr, main article h1, main article h2, main .vcard-details']
    ];
    function coversContent(px, py) {
      const el = document.elementFromPoint(px,py);
      if (el?.closest('a,button,input,summary,[role=button]')) return true;
      const caret = document.caretRangeFromPoint?.(px,py);
      const node = caret?.startContainer;
      if (node?.nodeType !== Node.TEXT_NODE || !node.length) return false;
      const i = Math.min(caret.startOffset,node.length-1);
      caret.setStart(node,i);
      caret.setEnd(node,i+1);
      const r = caret.getBoundingClientRect();
      return px >= r.left-3 && px <= r.right+3 && py >= r.top && py <= r.bottom;
    }
    function perches() {
      const points = [];
      const margin = Math.min(40, innerWidth / 2);
      const floor = Math.max(0, innerHeight - 5);
      for (const [kind, selector] of selectors) {
        for (const el of document.querySelectorAll(selector)) {
          const r = el.getBoundingClientRect();
          if (r.width < 50 || r.right < margin || r.left > innerWidth - margin) continue;
          // Alight on an actual top border or beside a section at its foot.
          const edges = kind === 'section' ? [[r.right - 32,r.bottom], [r.left + 32,r.bottom]] :
            [[r.right - 30,r.top], [r.left - 27,r.bottom]];
          for (const [px, py] of edges) {
            if (py < spriteHeight() + 95 || py > floor - 8 || px < margin || px > innerWidth - margin) continue;
            if ([-15,0,15].some(dx => [8,30,54].some(dy => coversContent(px+dx,py-dy)))) continue;
            points.push({x:px, y:py, kind});
          }
        }
      }
      for (const ratio of [0.12, 0.45, 0.84]) {
        points.push({x:clamp(innerWidth * (ratio + between(-0.04,0.04)),margin,innerWidth-margin),y:floor,kind:'floor'});
      }
      return points;
    }
    function say(line) {
      note.hidden = false;
      note.style.visibility = 'hidden';
      note.textContent = line;
      const {width,height: noteHeight} = note.getBoundingClientRect();
      const left = clamp(x - width / 2, 2, innerWidth - width - 2);
      const top = y - spriteHeight() - noteHeight - 7;
      if (top < 60) { silence(); return; }
      // Leave buttons, links, disclosure controls and inputs readable.
      for (const sx of [left + 3, left + width / 2, left + width - 3]) {
        for (const sy of [top + 3, top + noteHeight/2, top + noteHeight-3]) {
          if (coversContent(sx,sy)) { silence(); return; }
        }
      }
      note.style.left = left + 'px';
      note.style.top = top + 'px';
      note.style.visibility = 'visible';
      lastSpeech = activeTime();
      noteTimer = setTimeout(silence, 4200);
    }
    function rest(first = false) {
      leg = null;
      const time = activeTime();
      let pose = 'arms_crossed';
      let line = '';
      if (!first && preferences.reminders && time - lastReminder >= 20 * 60000) {
        lastReminder = time;
        line = reminderCount++ % 2 ? 'Small stretch break? Your spine would appreciate it.' : 'Had water?';
        pose = 'happy';
      } else if (!first) {
        if (perch.kind === 'graph') {
          pose = 'reading';
          line = 'So many little squares.';
        } else if (perch.kind === 'repository') {
          pose = 'judging';
          line = 'Just one more README.';
        } else {
          pose = pick(['arms_crossed','reading','sleeping_pillow','sleepy','worried']);
          if (pose === 'worried') line = 'I meant to do that.';
        }
        if (time - lastSpeech < 60000 || Math.random() > 0.22) line = '';
      }
      paint(pose);
      if (line) say(line);
      if (motion.matches) return;
      // One gentle breath in an idle spell. No perpetual animation at rest.
      if (!first && pose === 'arms_crossed') {
        img.animate([{scale:'1 1'},{scale:'1 1.006'},{scale:'1 1'}],{duration:3600});
      }
      timer = setTimeout(depart, first ? between(1700,3100) :
        pose === 'sleepy' ? between(26000,52000) : between(6200,16000));
    }
    function animate(now) {
      if (!leg) return;
      if (now - lastFrame >= 1000/30 - 1) {
        const result = PochiGait.step(leg,(now - lastFrame)/1000);
        lastFrame = now;
        x = leg.x;
        y = leg.y;
        paint(result.frame,result.mirror,result.bob);
        if (result.arrived) { rest(); return; }
      }
      raf = requestAnimationFrame(animate);
    }
    function depart() {
      if (document.hidden || motion.matches || !onProfile() || disposed) return;
      silence();
      const options = perches().filter(p => Math.hypot(p.x-x,p.y-y) > 55);
      if (!options.length) { rest(true); return; }
      const interesting = options.filter(p => p.kind !== 'floor');
      const graph = interesting.filter(p => p.kind === 'graph');
      let next = pick(options);
      if (interesting.length && Math.random() < 0.72) next = pick(interesting);
      if (graph.length && perch.kind !== 'graph' && Math.random() < 0.65) next = pick(graph);
      if (firstWalk) {
        const across = options.filter(p => Math.abs(p.x-x) > Math.min(innerWidth/3,160) &&
          Math.abs(p.y-y) <= Math.abs(p.x-x));
        if (across.length) next = pick(across);
        firstWalk = false;
      }
      const direction = Math.sign(next.x-x) || facing;
      const pivot = direction !== facing;
      facing = direction;
      perch = next;
      leg = PochiGait.start(x,y,next,spriteHeight()/144);
      function walk() {
        lastFrame = performance.now();
        raf = requestAnimationFrame(animate);
      }
      if (pivot) {
        paint('walk_front_2');
        timer = setTimeout(walk,220);
      } else walk();
    }
    function place() {
      cancel();
      if (document.hidden || disposed) return;
      const choices = perches();
      const nearby = choices.filter(p => p.kind !== 'floor');
      perch = nearby.length ? pick(nearby) : choices[choices.length-1];
      x = perch.x; y = perch.y;
      lastScroll = scrollY;
      rest(true);
    }
    function geometry(event) {
      if (document.hidden) return;
      cancel();
      img.getAnimations().forEach(a => a.cancel());
      // Follow the document ledge during native scrolling. Park again after
      // scrolling ends; read the landmark rectangles just once per burst.
      if (event.type === 'scroll' && perch.kind !== 'floor') {
        y -= scrollY-lastScroll;
        perch.y -= scrollY-lastScroll;
      }
      lastScroll = scrollY;
      x = clamp(x, Math.min(38,innerWidth/2), Math.max(innerWidth-38,innerWidth/2));
      if (perch.kind === 'floor') y = innerHeight-5;
      paint('arms_crossed');
      layoutTimer = setTimeout(() => {
        if (event.type === 'scroll' && y > spriteHeight()+90 && y <= innerHeight &&
            Math.hypot(x-perch.x,y-perch.y) < 1) rest(true);
        else place();
      },180);
    }
    function visibility() {
      if (document.hidden) {
        if (awakeSince !== null) elapsed += performance.now() - awakeSince;
        awakeSince = null;
        cancel();
        img.getAnimations().forEach(a => a.cancel());
        host.style.visibility = 'hidden';
      } else {
        if (awakeSince === null) awakeSince = performance.now();
        host.style.visibility = '';
        place();
      }
    }
    if (document.hidden) awakeSince = null;
    document.addEventListener('visibilitychange',visibility,{signal});
    window.addEventListener('scroll',geometry,{passive:true,signal});
    window.addEventListener('resize',geometry,{signal});
    document.addEventListener('toggle',geometry,{capture:true,signal});
    motion.addEventListener('change',() => {
      img.getAnimations().forEach(a => a.cancel());
      place();
    },{signal});
    place();
    return {silence, destroy() {
      disposed = true;
      cancel();
      events.abort();
      host.remove();
    }};
  }

  function stop() { companion?.destroy(); companion = null; }
  function sync() {
    if (!loaded || suspended || !onProfile() || !preferences.enabled) stop();
    else if (!companion) companion = createCompanion();
  }
  chrome.storage.onChanged.addListener((changes,area) => {
    if (area !== 'local') return;
    for (const key of Object.keys(defaults)) {
      if (changes[key]) preferences[key] = changes[key].newValue ?? defaults[key];
    }
    if (!preferences.reminders) companion?.silence();
    sync();
  });
  document.addEventListener('turbo:before-cache',stop);
  document.addEventListener('turbo:before-render',stop);
  document.addEventListener('turbo:load',sync);
  window.navigation?.addEventListener('currententrychange',sync);
  window.addEventListener('popstate',sync);
  window.addEventListener('pageshow',() => { suspended = false; sync(); });
  window.addEventListener('pagehide',() => { suspended = true; stop(); });
  chrome.storage.local.get(defaults).then(values => {
    Object.assign(preferences,values);
    loaded = true;
    sync();
  });
})();
