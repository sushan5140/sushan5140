const test = require('node:test');
const assert = require('node:assert/strict');
const {start, step} = require('../pochi-extension/gait');

for (const [label,x,y,prefix,mirror] of [
  ['right',300,0,'walk_',false],['left',-300,0,'walk_',true],
  ['up',0,-300,'walk_back_',false],['down',0,300,'walk_front_',false]
]) {
  test(label + ' travel uses the desktop stride and arrives exactly', () => {
    const leg = start(0,0,{x,y},0.5);
    const frames = new Set();
    let prior = 0, braking = false, arrived = false;
    for (let i=0; i<1000; i++) {
      const s = step(leg,1/30);
      frames.add(s.frame);
      assert.ok(s.frame.startsWith(prefix));
      assert.equal(s.mirror,mirror);
      assert.ok(leg.speed <= 65);
      if (leg.speed < prior) braking = true;
      prior = leg.speed;
      if (s.arrived) { arrived = true; break; }
    }
    assert.ok(arrived && braking);
    assert.equal(frames.size,3);
    assert.deepEqual([leg.x,leg.y],[x,y]);
  });
}
test('a delayed frame stays bounded and short trips have a gentler cap', () => {
  const leg = start(0,0,{x:20,y:0},0.5);
  assert.ok(leg.cruise < 65);
  step(leg,10);
  assert.ok(leg.x > 0 && leg.x < 1);
  assert.equal(step(start(3,7,{x:3,y:7},0.5),0).arrived,true);
});
