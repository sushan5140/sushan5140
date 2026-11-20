/* Adapted from sushan5140/Pochi renderer/renderer.js at fa0bbf8.
   Distances, speeds and acceleration are in desktop pixels, then scaled
   together so that a smaller character takes proportionally shorter steps. */
const PochiGait = (() => {
  const sets = {
    side: ['walk_1_contact_right', 'walk_2_passing', 'walk_3_contact_left'],
    front: ['walk_front_1', 'walk_front_2', 'walk_front_3'],
    back: ['walk_back_1', 'walk_back_2', 'walk_back_3']
  };
  const sequence = [0, 1, 2, 1];
  function start(x, y, target, scale) {
    const distance = Math.hypot(target.x - x, target.y - y);
    const cruise = 130 * scale * (0.45 + 0.55 * Math.min(1, distance / (120 * scale)));
    return {x, y, target, scale, cruise, speed: 0, traveled: 0};
  }
  function step(leg, seconds) {
    const dt = Math.min(0.1, Math.max(0, seconds));
    const {target, scale} = leg;
    const dx = target.x - leg.x;
    const dy = target.y - leg.y;
    const remaining = Math.hypot(dx, dy);
    const brake = 440 * scale;
    const safe = Math.min(leg.cruise, Math.sqrt(2 * brake * remaining));
    const delta = (safe < leg.speed ? brake : 320 * scale) * dt;
    const speed = leg.speed + Math.max(-delta, Math.min(delta, safe - leg.speed));
    const distance = Math.min(remaining, (leg.speed + speed) * 0.5 * dt);
    const arrived = remaining - distance <= 0.5;
    leg.speed = speed;
    leg.traveled += distance;
    leg.x = arrived ? target.x : leg.x + dx / remaining * distance;
    leg.y = arrived ? target.y : leg.y + dy / remaining * distance;
    const set = Math.abs(dy) > Math.abs(dx) ? (dy < 0 ? 'back' : 'front') : 'side';
    const phase = leg.traveled / ((set === 'side' ? 20 : 28) * scale);
    const frame = sets[set][sequence[Math.floor(phase) % 4]];
    const bob = set === 'back' ? -3 * scale * (1 - Math.cos(Math.PI * phase)) / 2 : 0;
    return {arrived, frame, mirror: set === 'side' && dx < 0, bob};
  }
  return {start, step};
})();
if (typeof module !== 'undefined' && module.exports) module.exports = PochiGait;
