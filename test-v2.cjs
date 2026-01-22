#!/usr/bin/env node

/**
 * FreeSewing v2 API Test - This should actually work!
 */

const { freesewing } = require('@freesewing/core');
const Breanna = require('@freesewing/breanna');
const { plugin: themePlugin } = require('@freesewing/plugin-theme');
const fs = require('fs');

console.log('🎨 Using FreeSewing v2 API...');

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

// v2 API - use Breanna directly
console.log('Breanna type:', typeof Breanna, typeof Breanna.Breanna);

const PatternClass = Breanna.Breanna || Breanna.default || Breanna;
const pattern = new PatternClass({
    measurements,
    options: {},
    settings: {
        sa: 10,
        complete: true,
        paperless: false,
        units: 'metric'
    }
});

pattern.use(themePlugin);

console.log('🎨 Drafting v2 pattern...');
const svg = pattern.draft().render();

console.log(`✅ Rendered: ${svg.length} bytes`);

// Check content
const hasContent = svg.includes('<path') && svg.match(/d="M[\d\s\.,LCZ-]+"/);
console.log(`📦 Has path content: ${hasContent}`);

fs.writeFileSync('test-v2.svg', svg);
console.log('✅ Saved to test-v2.svg');
