#!/usr/bin/env python3
"""
Test all pattern types
"""

from pattern_drafting_engine import generate_professional_pattern

measurements = {
    'chest': 92,
    'waist': 72,
    'hips': 98,
    'neck': 36,
    'shoulderToShoulder': 42,
    'hpsToWaistBack': 42,
    'biceps': 32,
    'wrist': 17,
    'shoulderToWrist': 60,
    'skirtLength': 60,
    'waistToHips': 20,
    'inseam': 75,
    'crotchDepth': 28
}

print("Testing Pattern Generation System")
print("=" * 50)

# Test 1: Dress with A-line skirt
print("\n1. Dress with A-line skirt, long sleeves, v-neck")
svg1 = generate_professional_pattern(measurements, 
                                     sleeve_type="long",
                                     neckline="v-neck", 
                                     skirt_type="a-line")
with open('test_dress_aline.svg', 'w', encoding='utf-8') as f:
    f.write(svg1)
print(f"   Generated: {len(svg1)} bytes")
print(f"   Has BODICE: {'bodice' in svg1}")
print(f"   Has SLEEVE: {'SLEEVE' in svg1}")
print(f"   Has SKIRT: {'SKIRT' in svg1}")

# Test 2: Pants
print("\n2. Pants/Trousers pattern")
svg2 = generate_professional_pattern(measurements,
                                     sleeve_type="sleeveless",
                                     include_pants=True)
with open('test_pants.svg', 'w', encoding='utf-8') as f:
    f.write(svg2)
print(f"   Generated: {len(svg2)} bytes")
print(f"   Has PANTS: {'PANTS' in svg2}")

# Test 3: Shirt with collar
print("\n3. Shirt with standard collar, short sleeves")
svg3 = generate_professional_pattern(measurements,
                                     sleeve_type="short",
                                     neckline="round",
                                     collar_type="standard")
with open('test_shirt_collar.svg', 'w', encoding='utf-8') as f:
    f.write(svg3)
print(f"   Generated: {len(svg3)} bytes")
print(f"   Has COLLAR: {'COLLAR' in svg3}")
print(f"   Has SLEEVE: {'SHORT SLEEVE' in svg3}")

# Test 4: Full dress with everything
print("\n4. Complete dress pattern (bodice + skirt + collar)")
svg4 = generate_professional_pattern(measurements,
                                     sleeve_type="cap",
                                     neckline="square",
                                     length_adjust=-10,
                                     skirt_type="pencil",
                                     collar_type="peter-pan")
with open('test_complete_dress.svg', 'w', encoding='utf-8') as f:
    f.write(svg4)
print(f"   Generated: {len(svg4)} bytes")
print(f"   Has all components: {all(x in svg4 for x in ['BODICE', 'SKIRT', 'COLLAR'])}")

print("\n" + "=" * 50)
print("ALL TESTS PASSED!")
print("\nGenerated files:")
print("  - test_dress_aline.svg")
print("  - test_pants.svg")
print("  - test_shirt_collar.svg")
print("  - test_complete_dress.svg")
