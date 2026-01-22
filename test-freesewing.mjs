import { Breanna } from '@freesewing/breanna';

const measurements = {
  chest: 920,
  waist: 720,
  hips: 980,
  neck: 360,
  hpsToWaistBack: 420,
  hpsToBust: 400,
  waistToHips: 200,
  shoulderToShoulder: 420,
  shoulderSlope: 55,
  biceps: 320,
  bustFront: 460,
  bustSpan: 175,
  highBust: 874,
  highBustFront: 442
};

console.log('Test 1: Basic config');
const p1 = new Breanna({ measurements });
p1.draft();
console.log(`Result: Width=${p1.width}, Height=${p1.height}`);

console.log('\nTest 2: With layout');
const p2 = new Breanna({ measurements, layout: true });
p2.draft();
console.log(`Result: Width=${p2.width}, Height=${p2.height}`);

console.log('\nTest 3: With autoLayout');
const p3 = new Breanna({ measurements, autoLayout: { stacks: [] } });
p3.draft();
console.log(`Result: Width=${p3.width}, Height=${p3.height}`);

console.log('\nTest 4: With complete and layout');
const p4 = new Breanna({ measurements, complete: true, layout: true });
p4.draft();
console.log(`Result: Width=${p4.width}, Height=${p4.height}`);
