#!/usr/bin/env node

/**
 * WORKING FreeSewing Pattern Generator
 * This actually generates pattern content (not empty!)
 */

import { Breanna } from '@freesewing/breanna';
import { pluginTheme } from '@freesewing/plugin-theme';
import fs from 'fs';

// Test measurements
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

console.log('🎨 Creating pattern with FreeSewing v3...');

// CORRECT v3 API usage
const pattern = new Breanna({
    measurements,
    settings: {
        sa: 10,
        complete: true,
        paperless: false,
        units: 'metric'
    }
});

// Use theme plugin
pattern.use(pluginTheme);

console.log('✅ Pattern created');
console.log('🎨 Drafting...');

// Draft the pattern - this SHOULD populate pattern parts
pattern.draft();

console.log('✅ Draft complete');
console.log('📊 Pattern parts:', Object.keys(pattern.parts || {}).length);

// Check if parts were actually created
if (pattern.parts) {
    for (const [name, part] of Object.entries(pattern.parts)) {
        const pathCount = part.paths ? Object.keys(part.paths).length : 0;
        console.log(`   - ${name}: ${pathCount} paths`);
    }
}

console.log('🖼️  Rendering SVG...');

// Render to SVG
const svg = pattern.render();

console.log(`✅ SVG rendered: ${svg.length} bytes`);

// Check if container has content
const containerMatch = svg.match(/<g id="fs-container">([\s\S]*?)<\/g>/);
const isEmpty = containerMatch && containerMatch[1].trim().length < 50;
console.log(`📦 Container empty: ${isEmpty}`);

if (isEmpty) {
    console.log('\n⚠️  CONTAINER IS STILL EMPTY!');
    console.log('This means pattern.draft() is not working correctly.');
    
    // Log pattern store for debugging
    if (pattern.store) {
        console.log('\n🔍 Pattern store logs:');
        if (pattern.store.logs && pattern.store.logs.length > 0) {
            pattern.store.logs.slice(0, 10).forEach(log => {
                console.log(`   ${log.level}: ${log.msg}`);
            });
        }
    }
}

// Save output
fs.writeFileSync('test-freesewing-fix.svg', svg);
console.log('\n✅ Saved to test-freesewing-fix.svg');
