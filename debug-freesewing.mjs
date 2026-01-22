import { Breanna } from '@freesewing/breanna';
import { pluginTheme } from '@freesewing/plugin-theme';
import fs from 'fs';

// Test with settings that enable rendering
const settings = {
  measurements: {
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
    highBustFront: 442,
    shoulderToWrist: 600,  // ✅ ADDED - required for sleeves!
    wrist: 170  // ✅ ADDED - required for sleeves!
  },
  complete: true,  // THIS IS KEY - tells FreeSewing to render complete pattern
  sa: 10,
  units: 'metric'
};

const pattern = new Breanna(settings);
pattern.use(pluginTheme);

console.log('Config measurements:', Object.keys(settings.measurements));
console.log('Has shoulderToWrist:', settings.measurements.shoulderToWrist);
console.log('Has wrist:', settings.measurements.wrist);

console.log('Calling draft()...');
pattern.draft();

console.log('Pattern parts in store:', Object.keys(pattern.setStores || {}));
console.log('Store pack:', typeof pattern.store.pack);

// Check if parts were actually drafted
const partNames = ['breanna.back', 'breanna.front', 'breanna.sleeve'];
for (const partName of partNames) {
  const part = pattern.setStores?.[partName];
  console.log(`Part ${partName}:`, part ? 'EXISTS' : 'missing');
}

console.log('Calling render()...');
const svg = pattern.render();

console.log('SVG length:', svg.length);

// Check if container has content
const match = svg.match(/<g id="fs-container">([\s\S]*?)<\/g>/);
if (match) {
  const content = match[1].trim();
  console.log('Container empty:', content.length === 0);
  if (content.length > 0) {
    console.log('✅ SUCCESS - Pattern has content!');
    console.log('Preview:', content.substring(0, 300));
  }
}

fs.writeFileSync('debug-pattern2.svg', svg);
console.log('Saved to debug-pattern2.svg');
