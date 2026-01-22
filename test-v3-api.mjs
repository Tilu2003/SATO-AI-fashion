import freesewing from '@freesewing/breanna';
import { pluginTheme } from '@freesewing/plugin-theme';

console.log('Testing FreeSewing v3...');
console.log('Breanna type:', typeof freesewing);

// v3 API: should be a function
const pattern = new freesewing({
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
    shoulderToWrist: 600,
    wrist: 170
  },
  settings: {
    sa: 10,
    complete: true,
    paperless: false,
    units: 'metric'
  }
}).use(pluginTheme);

console.log('Drafting...');
pattern.draft();

console.log('Rendering...');
const svg = pattern.render();

console.log('SVG length:', svg.length);

// Check container
const match = svg.match(/<g id="fs-container">([\s\S]*?)<\/g>/);
if (match) {
  const content = match[1].trim();
  console.log('Container has content:', content.length > 10);
  if (content.length > 10) {
    console.log('Preview:', content.substring(0, 300));
  }
}

import fs from 'fs';
fs.writeFileSync('test-v3-direct.svg', svg);
console.log('Saved to test-v3-direct.svg');
