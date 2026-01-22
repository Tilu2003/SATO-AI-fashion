#!/usr/bin/env python3
"""
Test pattern generation with proper measurements
"""

from hybrid_engine_module import generate_pattern_hybrid

# Test data
master_plan = {
    'category': 'dress',
    'subcategory': 'mini_dress',
    'design_elements': ['deep_v_neck', 'tie_shoulder_straps', 'empire_waist', 'tiered_skirt'],
    'style_features': ['casual', 'summer'],
    'silhouette': 'fitted_bodice_flared_skirt',
    'length': 'mini',
    'fabric': 'eyelet_cotton'
}

measurements = {
    'chestCircumference': 92,  # cm
    'waistCircumference': 72,  # cm
    'hipCircumference': 98,  # cm
    'neckCircumference': 36,  # cm
    'hpsToWaistBack': 42,  # cm
    'hpsToWaistFront': 40,  # cm
    'garmentLength': 90  # cm (mini dress)
}

fit_preferences = {
    'overall_fit': 'standard'
}

complexity = {
    'level': 'moderate',
    'score': 60
}

print("=" * 70)
print("🧪 TESTING PATTERN GENERATION")
print("=" * 70)
print(f"\n📋 Master Plan: {master_plan['subcategory']}")
print(f"📏 Measurements: {len(measurements)} provided")
print(f"🎯 Fit: {fit_preferences['overall_fit']}")

try:
    result = generate_pattern_hybrid(master_plan, measurements, fit_preferences, complexity)
    
    print("\n" + "=" * 70)
    print("✅ PATTERN GENERATION SUCCESSFUL")
    print("=" * 70)
    print(f"📁 File: {result['pattern_file']}")
    print(f"🎨 Pattern: {result['pattern_used']}")
    print(f"✨ Confidence: {result.get('confidence_score', 0):.0%}")
    
    if result.get('unsupported_features'):
        print(f"\n⚠️  Unsupported features: {', '.join(result['unsupported_features'])}")
    
    # Check file size
    import os
    if os.path.exists(result['pattern_file']):
        size = os.path.getsize(result['pattern_file'])
        print(f"📊 File size: {size:,} bytes")
        
        # Quick check if SVG has proper dimensions
        with open(result['pattern_file'], 'r') as f:
            content = f.read(500)
            if 'width="0mm"' in content or 'height="0mm"' in content:
                print("❌ WARNING: SVG has 0mm dimensions!")
            else:
                print("✅ SVG has proper dimensions")
    else:
        print(f"❌ File not found: {result['pattern_file']}")
        
except Exception as e:
    print("\n" + "=" * 70)
    print("❌ PATTERN GENERATION FAILED")
    print("=" * 70)
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
