import { Brian } from '@freesewing/brian';
import { pluginTheme } from '@freesewing/plugin-theme';
import fs from 'fs';

console.log('Testing Brian pattern v3...');

const pattern = new Brian({
  measurements: {
    chest: 920,
    neck: 360,
    hpsToWaistBack: 420,
    waistToHips: 200,
    shoulderToShoulder: 420,
    shoulderSlope: 55
  },
  settings: {
    sa: 10,
    complete: true,
    units: 'metric'
  }
});

pattern.use(pluginTheme);

console.log('Drafting...');
pattern.draft();

console.log('Rendering...');
const svg = pattern.render();

console.log('SVG length:', svg.length);

const match = svg.match(/<g id="fs-container">([\s\S]*?)<\/g>/);
if (match) {
  const content = match[1].trim();
  console.log('Container empty:', content.length === 0);
  if (content.length > 0) {
    console.log('✅ SUCCESS! Brian generated content!');
    console.log('Content preview:', content.substring(0, 200));
  }
}

fs.writeFileSync('test-brian.svg', svg);
