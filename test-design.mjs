#!/usr/bin/env node

/**
 * Try using Design class from core instead of pattern-specific class
 */

import { Design } from '@freesewing/core';
import * as breannaPlugin from '@freesewing/breanna';
import { pluginTheme } from '@freesewing/plugin-theme';
import fs from 'fs';

console.log('📦 Checking FreeSewing exports...');
console.log('Breanna exports:', Object.keys(breannaPlugin));

// Try to import the pattern parts directly
const { back, front, sleeve, base } = breannaPlugin;

console.log('✅ Pattern parts available');
console.log('   - back:', typeof back);
console.log('   - front:', typeof front);  
console.log('   - sleeve:', typeof sleeve);

// Create a custom design using the parts
const BodiceDesign = new Design({
    parts: [back, front, sleeve]
});

console.log('\n🎨 Creating pattern from design...');

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
    highBustFront: 442,
    shoulderToWrist: 600,
    wrist: 170
};

const pattern = new BodiceDesign({
    measurements,
    settings: {
        sa: 10,
        complete: true,
        paperless: false
    }
});

pattern.use(pluginTheme);

console.log('🎨 Drafting pattern...');
pattern.draft();

console.log('✅ Draft complete');
console.log('📊 Parts:', Object.keys(pattern.parts || {}).length);

const svg = pattern.render();

console.log(`✅ Rendered: ${svg.length} bytes`);

const isEmpty = svg.match(/<g id="fs-container">([\s\S]*?)<\/g>/)?.[1]?.trim().length < 50;
console.log(`📦 Container empty: ${isEmpty}`);

fs.writeFileSync('test-design-approach.svg', svg);
console.log('✅ Saved to test-design-approach.svg');
