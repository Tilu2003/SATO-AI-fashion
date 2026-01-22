#!/usr/bin/env node

import fs from 'fs';

function parseArgs() {
    const args = process.argv.slice(2);
    const result = {};
    for (let i = 0; i < args.length; i += 2) {
        const key = args[i].replace('--', '');
        result[key] = args[i + 1];
    }
    return result;
}

async function main() {
    const args = parseArgs();
    
    if (!args.from || !args.to || !args.pattern) {
        console.error('Usage: node freesewing-generator.js --from input.json --to output.svg --pattern breanna');
        process.exit(1);
    }

    if (!fs.existsSync(args.from)) {
        console.error(`Input file not found: ${args.from}`);
        process.exit(1);
    }

    try {
        const inputData = JSON.parse(fs.readFileSync(args.from, 'utf8'));
        console.log(`📖 Read input: ${args.from}`);

        let PatternClass;
        let pluginTheme;
        let pluginAnnotations;
        
        try {
            const patternModule = await import(`@freesewing/${args.pattern.toLowerCase()}`);
            const patternName = args.pattern.charAt(0).toUpperCase() + args.pattern.slice(1).toLowerCase();
            PatternClass = patternModule[patternName] || patternModule.default || patternModule;
            
            if (!PatternClass) {
                throw new Error(`Pattern class not found: ${patternName}`);
            }
            
            const themeModule = await import('@freesewing/plugin-theme');
            pluginTheme = themeModule.pluginTheme || themeModule.default;
            
            // Try to load annotations plugin for better markings
            try {
                const annotationsModule = await import('@freesewing/plugin-annotations');
                pluginAnnotations = annotationsModule.pluginAnnotations || annotationsModule.default;
            } catch (e) {
                console.log('ℹ️  Annotations plugin not available (optional)');
            }
            
        } catch (importError) {
            console.error(`Failed to import pattern '${args.pattern}': ${importError.message}`);
            process.exit(1);
        }

        const measurements = inputData.measurements || {};
        if (Object.keys(measurements).length === 0) {
            console.error('No measurements provided');
            process.exit(1);
        }

        console.log(`📏 Received ${Object.keys(measurements).length} measurements`);
        console.log(`   Sample: chest=${measurements.chest}, waist=${measurements.waist}, hips=${measurements.hips}`);

        const config = {
            measurements: measurements,
            options: inputData.options || {}
        };
        
        const settings = {
            sa: 10,  // Seam allowance 10mm  
            complete: true,  // Include all pattern details
            paperless: false,  // Include seam guidelines
            units: 'metric'
        };

        // FreeSewing v3 API: Pattern constructor takes settings separately
        console.log('⚙️  Creating pattern instance (v3)...');
        const pattern = new PatternClass({
            ...config,
            settings: settings
        });
        
        if (pluginTheme) {
            pattern.use(pluginTheme);
            console.log('✅ Theme plugin loaded');
        }
        
        // v3: draft() actually generates pattern content
        console.log('🎨 Drafting pattern (v3)...');
        pattern.draft();
        console.log('✅ Draft complete');
        
        // v3: render() returns the SVG string
        console.log('🖼️  Rendering SVG (v3)...');
        const svgRaw = pattern.render();

        if (!svgRaw || typeof svgRaw !== 'string' || !svgRaw.includes('<svg')) {
            throw new Error('Invalid SVG output');
        }

        // ✅ FIX: FreeSewing v4 sets width/height to 0, but paths are valid
        // We need to calculate bounding box from path data
        let svg = svgRaw;
        
        // Extract all path coordinates to calculate bounds
        const pathRegex = /<path[^>]+d="([^"]+)"/g;
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        let match;
        
        while ((match = pathRegex.exec(svg)) !== null) {
            const pathData = match[1];
            // Extract all numbers from path (M, L, C commands)
            const numbers = pathData.match(/-?\d+\.?\d*/g);
            if (numbers) {
                for (let i = 0; i < numbers.length; i += 2) {
                    const x = parseFloat(numbers[i]);
                    const y = parseFloat(numbers[i + 1]);
                    if (!isNaN(x) && !isNaN(y)) {
                        minX = Math.min(minX, x);
                        minY = Math.min(minY, y);
                        maxX = Math.max(maxX, x);
                        maxY = Math.max(maxY, y);
                    }
                }
            }
        }
        
        if (isFinite(minX) && isFinite(minY) && isFinite(maxX) && isFinite(maxY)) {
            // Add 20mm margin
            const margin = 20;
            minX -= margin;
            minY -= margin;
            maxX += margin;
            maxY += margin;
            
            const width = maxX - minX;
            const height = maxY - minY;
            
            console.log(`📐 Calculated bounds: ${width.toFixed(1)}mm x ${height.toFixed(1)}mm`);
            
            // Fix the SVG attributes
            svg = svg.replace(
                /width="0mm" height="0mm" viewBox="0 0 0 0"/,
                `width="${width.toFixed(1)}mm" height="${height.toFixed(1)}mm" viewBox="${minX.toFixed(1)} ${minY.toFixed(1)} ${width.toFixed(1)} ${height.toFixed(1)}"`
            );
        } else {
            console.warn('⚠️  Could not calculate SVG bounds, using defaults');
            svg = svg.replace(
                /width="0mm" height="0mm" viewBox="0 0 0 0"/,
                'width="500mm" height="700mm" viewBox="0 0 500 700"'
            );
        }

        fs.writeFileSync(args.to, svg);
        
        const fileSize = fs.statSync(args.to).size;
        console.log(`✅ Pattern generated: ${args.to} (${fileSize} bytes)`);
        process.exit(0);

    } catch (error) {
        console.error(`❌ Generation failed: ${error.message}`);
        if (error.stack) {
            console.error(error.stack);
        }
        process.exit(1);
    }
}

process.on('unhandledRejection', (error) => {
    console.error('❌ Unhandled error:', error);
    process.exit(1);
});

main();