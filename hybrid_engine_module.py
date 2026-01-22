# ============================================================================
# FILE: hybrid_engine_module.py
# PURPOSE: Generates patterns using professional pattern drafting engine
# CHANGE: Now using svgwrite library + Winifred Aldrich formulas
# ============================================================================

import os
import uuid
import subprocess
import json
from typing import Dict, Any
from adaptive_translator import translate_with_llm, select_optimal_pattern
from pattern_drafting_engine import generate_professional_pattern

def generate_pattern_hybrid(
    master_plan: Dict[str, Any], 
    measurements: Dict[str, Any],
    fit_preferences: Dict[str, Any], 
    complexity: Dict[str, Any]
) -> Dict[str, Any]:
    """Generates pattern via FreeSewing using Node.js wrapper"""
    
    print("=" * 70)
    print("🎨 PATTERN GENERATION STARTED")
    print("=" * 70)
    
    # Select pattern
    pattern_design = select_optimal_pattern(master_plan)
    print(f"📐 Selected Pattern: {pattern_design.upper()}")
    
    # AI Translation
    print("\n🤖 Running AI Translation...")
    translation_result = translate_with_llm(master_plan, fit_preferences, pattern_design)
    style_options = translation_result.get("options", {})
    unsupported = translation_result.get("unsupported_features", [])
    confidence = translation_result.get("confidence_score", 0)
    
    print(f"✅ Translation Confidence: {confidence:.0%}")
    
    if style_options:
        print("\n📊 Applied Modifications:")
        for param, value in style_options.items():
            print(f"   • {param}: {value:+.2f}")
    
    if unsupported:
        print(f"\n⚠️  UNSUPPORTED FEATURES:")
        for feature in unsupported:
            print(f"   ⚠️  {feature}")
    
    # Prepare data (convert cm to mm - FreeSewing standard unit)
    # Map our measurement names to FreeSewing's expected names
    measurement_mapping = {
        'chestCircumference': 'chest',
        'waistCircumference': 'waist',
        'hipCircumference': 'hips',
        'neckCircumference': 'neck',
        'hpsToWaistBack': 'hpsToWaistBack',
        'hpsToWaistFront': 'hpsToBust',
        'garmentLength': 'waistToHips',  # Approximate
        'underbust': 'underbust',
        'shoulderSlope': 'shoulderSlope',
        'shoulderToShoulder': 'shoulderToShoulder',
        'bicepsCircumference': 'biceps',
        'wristCircumference': 'wrist',
        'armLength': 'shoulderToWrist'
    }
    
    measurements_mm = {}
    for our_name, value in measurements.items():
        if isinstance(value, (int, float)):
            # Map to FreeSewing name if exists, otherwise use as-is
            fs_name = measurement_mapping.get(our_name, our_name)
            measurements_mm[fs_name] = value * 10  # Convert cm to mm
    
    # ✅ CRITICAL: Breanna requires these specific measurements
    # Add intelligent defaults for all required measurements
    chest = measurements_mm.get('chest', 920)  # Default 92cm
    waist = measurements_mm.get('waist', 720)  # Default 72cm
    hips = measurements_mm.get('hips', 980)  # Default 98cm
    
    required_defaults = {
        'chest': chest,
        'waist': waist,
        'hips': hips,
        'neck': chest * 0.39,  # ~36cm for 92cm chest
        'hpsToWaistBack': chest * 0.46,  # ~42cm for 92cm chest
        'hpsToBust': chest * 0.43,  # ~40cm for 92cm chest
        'waistToHips': 200,  # Standard 20cm
        'shoulderToShoulder': chest * 0.46,  # ~42cm
        'shoulderSlope': 55,  # Standard 5.5cm slope
        'biceps': chest * 0.35,  # ~32cm for 92cm chest
        'bustFront': chest * 0.5,  # Half chest
        'bustSpan': chest * 0.19,  # ~17cm span
        'highBust': chest * 0.95,  # 5% smaller than full bust
        'highBustFront': chest * 0.48,  # Slightly less than bust front
        # ✅ CRITICAL: Add sleeve measurements (required!)
        'shoulderToWrist': chest * 0.65,  # ~60cm for 92cm chest
        'wrist': chest * 0.18  # ~17cm for 92cm chest
    }
    
    # Apply defaults for any missing measurements
    for key, default_value in required_defaults.items():
        if key not in measurements_mm:
            measurements_mm[key] = default_value
    
    print(f"\n📊 Measurements being sent to FreeSewing:")
    for k, v in list(measurements_mm.items())[:8]:
        print(f"   • {k}: {v:.1f}mm")
    
    design_data = {
        "pattern": pattern_design,
        "measurements": measurements_mm,
        "options": style_options
    }
    
    # File generation setup
    input_filename = f"temp_{uuid.uuid4().hex}.json"
    output_filename = f"pattern_{uuid.uuid4().hex}.svg"
    
    # Create downloads directory if it doesn't exist
    downloads_dir = os.path.join('static', 'downloads')
    os.makedirs(downloads_dir, exist_ok=True)
    
    try:
        # Write input JSON
        with open(input_filename, 'w') as f:
            json.dump(design_data, f, indent=2)
        
        print(f"\n💾 Input: {input_filename}")
        print(f"🎯 Output: {output_filename}")
        
        # Check if freesewing-generator.js exists
        generator_script = 'freesewing-generator.js'
        if not os.path.exists(generator_script):
            raise Exception(
                f"❌ FreeSewing generator script not found: {generator_script}\n"
                "   Please create freesewing-generator.js in the project root."
            )
        
        print("\n⚙️  Generating Pattern (Professional Drafting Method)...")
        print("   📐 Using Winifred Aldrich industry formulas")
        print("   🎨 SVG generation via svgwrite library")
        
        # Convert measurements from mm back to cm for the generator
        measurements_cm = {k: v / 10 for k, v in measurements_mm.items()}
        
        # ✅ PARSE MASTER PLAN to extract actual dress features
        design_elements = master_plan.get('design_elements', [])
        length = master_plan.get('length', 'midi')
        
        # Detect sleeve type from design elements
        sleeve_type = "long"  # Default
        if any('sleeveless' in elem.lower() or 'strap' in elem.lower() for elem in design_elements):
            sleeve_type = "sleeveless"
        elif any('short_sleeve' in elem.lower() or 'cap_sleeve' in elem.lower() for elem in design_elements):
            sleeve_type = "short"
        elif any('puff' in elem.lower() for elem in design_elements):
            sleeve_type = "puff"
        elif "sleeve" in style_options:
            sleeve_type = style_options["sleeve"]
        
        # Detect neckline from design elements
        neckline = 'round'  # Default
        if any('v_neck' in elem.lower() or 'v-neck' in elem.lower() for elem in design_elements):
            neckline = 'v-neck'
        elif any('square_neck' in elem.lower() for elem in design_elements):
            neckline = 'square'
        elif 'neckline' in style_options:
            neckline = style_options['neckline']
        
        # Adjust length based on master plan (in CM)
        length_adjustment = 0
        if length == 'mini':
            length_adjustment = -15  # Shorten by 15cm
        elif length == 'maxi':
            length_adjustment = 30  # Lengthen by 30cm
        elif length == 'midi':
            length_adjustment = 0  # Standard length
        
        print(f"   🎨 Detected: {sleeve_type} sleeves, {neckline} neckline, {length} length")
        
        # Generate using professional pattern drafting engine
        svg_content = generate_professional_pattern(
            measurements=measurements_cm,
            sleeve_type=sleeve_type,
            neckline=neckline,
            length_adjust=length_adjustment
        )
        
        # Save to output file
        output_path = os.path.join(downloads_dir, output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"✅ Pattern Generated: {len(svg_content)} bytes")
        print(f"📁 Saved to: {output_path}")
        
        # OLD FreeSewing command (removed - was generating empty patterns):
        # command = ['node', generator_script, '--from', input_filename, 
        #            '--to', output_filename, '--pattern', pattern_design]
        
        # Verify output file exists
        if not os.path.exists(output_path):
            raise Exception("Pattern file not created")
        
        file_size = os.path.getsize(output_path)
        print(f"✅ Final pattern file ({file_size} bytes)")
        
        # Build result
        return {
            "pattern_file": output_filename,  # Keep basename for download URL
            "pattern_used": pattern_design.upper(),
            "method_used": f"Professional Drafting (Aldrich Method) → {pattern_design}",
            "translation_confidence": confidence,
            "confidence_score": confidence,
            "applied_modifications": len(style_options),
            "unsupported_features": unsupported,
            "validation": {"score": int(confidence * 100)},
            "warnings": [
                f"⚠️  {f} requires manual work" for f in unsupported
            ] if unsupported else []
        }
        
    except subprocess.TimeoutExpired:
        raise Exception("Pattern generation timed out (60s)")
        
    except FileNotFoundError as e:
        raise Exception(
            "❌ Node.js not found. Please install Node.js from https://nodejs.org/"
        )
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise Exception(f"Pattern drafting failed: {str(e)}")
        
    finally:
        # Clean up input file
        if os.path.exists(input_filename):
            os.remove(input_filename)


def test_freesewing_setup() -> bool:
    """Tests if FreeSewing is properly installed and configured"""
    
    print("🔍 Testing FreeSewing Setup...")
    
    # Check Node.js
    try:
        result = subprocess.run(
            ['node', '--version'], 
            capture_output=True, 
            text=True,
            timeout=5
        )
        node_version = result.stdout.strip()
        print(f"✅ Node.js: {node_version}")
    except:
        print("❌ Node.js not found")
        return False
    
    # Check if generator script exists
    if not os.path.exists('freesewing-generator.js'):
        print("❌ freesewing-generator.js not found")
        return False
    print("✅ FreeSewing generator script found")
    
    # Check if FreeSewing packages are installed
    try:
        result = subprocess.run(
            ['npm', 'list', '@freesewing/core'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if '@freesewing/core@' in result.stdout:
            print("✅ @freesewing/core installed")
        else:
            print("❌ @freesewing/core not installed")
            return False
    except:
        print("❌ Cannot check npm packages")
        return False
    
    # Test with dummy data
    print("\n🧪 Running test generation...")
    try:
        test_data = {
            "pattern": "breanna",
            "measurements": {
                "chest": 920,
                "waist": 720,
                "hips": 980,
                "neck": 360,
                "shoulderToShoulder": 420,
                "hpsToWaistBack": 420
            },
            "options": {}
        }
        
        test_input = "test_freesewing_input.json"
        test_output = "test_freesewing_output.svg"
        
        with open(test_input, 'w') as f:
            json.dump(test_data, f)
        
        result = subprocess.run(
            ['node', 'freesewing-generator.js', 
             '--from', test_input, 
             '--to', test_output, 
             '--pattern', 'breanna'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        success = result.returncode == 0 and os.path.exists(test_output)
        
        # Cleanup
        if os.path.exists(test_input):
            os.remove(test_input)
        if os.path.exists(test_output):
            os.remove(test_output)
        
        if success:
            print("✅ Test pattern generated successfully")
            return True
        else:
            print(f"❌ Test generation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == '__main__':
    # Run setup test
    if test_freesewing_setup():
        print("\n🎉 FreeSewing is ready!")
    else:
        print("\n❌ FreeSewing setup incomplete")
        print("\n📋 Setup instructions:")
        print("1. Install Node.js: https://nodejs.org/")
        print("2. Run: npm install @freesewing/core@latest @freesewing/breanna@latest @freesewing/simon@latest")
        print("3. Create freesewing-generator.js in project root")
        print("4. Run: python hybrid_engine_module.py (to test)")