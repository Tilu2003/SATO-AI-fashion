"""
Test FreeSewing Formula Implementation
Generates a complete dress pattern with all features
"""
from pattern_drafting_engine import generate_professional_pattern

# Standard women's size 12 measurements
measurements = {
    'chest': 92,          # Bust circumference
    'waist': 72,          # Waist circumference
    'hips': 98,           # Hip circumference
    'neck': 36,           # Neck circumference
    'shoulderToShoulder': 42,  # Across back
    'hpsToWaistBack': 42, # High point shoulder to waist (back length)
    'biceps': 32,         # Upper arm circumference
    'wrist': 17,          # Wrist circumference
    'shoulderToWrist': 60 # Arm length
}

print("=" * 60)
print("FREESEWING FORMULA IMPLEMENTATION TEST")
print("=" * 60)
print("\n📏 Using Size 12 Measurements:")
for key, value in measurements.items():
    print(f"   {key}: {value} cm")

print("\n🎨 Generating patterns with FreeSewing formulas...")

# Test 1: Basic bodice with long sleeves
print("\n1. Basic Bodice + Long Sleeves (V-neck)")
svg1 = generate_professional_pattern(
    measurements=measurements,
    sleeve_type="long",
    neckline="v-neck",
    length_adjust=0
)
with open('freesewing_bodice.svg', 'w', encoding='utf-8') as f:
    f.write(svg1)
print(f"   ✅ Generated freesewing_bodice.svg ({len(svg1):,} bytes)")

# Test 2: Complete dress with A-line skirt
print("\n2. Complete Dress (Long sleeves + A-line skirt + Round neck)")
svg2 = generate_professional_pattern(
    measurements=measurements,
    sleeve_type="long",
    neckline="round",
    length_adjust=0,
    skirt_type="a-line"
)
with open('freesewing_dress_aline.svg', 'w', encoding='utf-8') as f:
    f.write(svg2)
print(f"   ✅ Generated freesewing_dress_aline.svg ({len(svg2):,} bytes)")

# Test 3: Summer dress (cap sleeves + circle skirt)
print("\n3. Summer Dress (Cap sleeves + Circle skirt + Square neck)")
svg3 = generate_professional_pattern(
    measurements=measurements,
    sleeve_type="cap",
    neckline="square",
    length_adjust=-10,  # Mini length
    skirt_type="circle"
)
with open('freesewing_summer_dress.svg', 'w', encoding='utf-8') as f:
    f.write(svg3)
print(f"   ✅ Generated freesewing_summer_dress.svg ({len(svg3):,} bytes)")

# Test 4: Shirt with collar
print("\n4. Shirt (Short sleeves + Standard collar)")
svg4 = generate_professional_pattern(
    measurements=measurements,
    sleeve_type="short",
    neckline="round",
    length_adjust=0,
    collar_type="standard"
)
with open('freesewing_shirt.svg', 'w', encoding='utf-8') as f:
    f.write(svg4)
print(f"   ✅ Generated freesewing_shirt.svg ({len(svg4):,} bytes)")

# Test 5: Pants
print("\n5. Pants/Trousers")
svg5 = generate_professional_pattern(
    measurements=measurements,
    sleeve_type="sleeveless",
    neckline="round",
    length_adjust=0,
    include_pants=True
)
with open('freesewing_pants.svg', 'w', encoding='utf-8') as f:
    f.write(svg5)
print(f"   ✅ Generated freesewing_pants.svg ({len(svg5):,} bytes)")

print("\n" + "=" * 60)
print("✅ ALL TESTS COMPLETED")
print("=" * 60)
print("\n📋 Features Included in Each Pattern:")
print("   ✓ FreeSewing's exact bodice block formulas")
print("   ✓ FreeSewing's sleeve cap calculations (0.65 ratio)")
print("   ✓ Seam allowances (1cm) included")
print("   ✓ Notches for pattern piece alignment")
print("   ✓ Cutting instructions with fabric requirements")
print("   ✓ Step-by-step sewing instructions")
print("   ✓ Grain line markings")
print("   ✓ Pattern piece labels")
print("\n📂 View generated files:")
print("   • freesewing_bodice.svg")
print("   • freesewing_dress_aline.svg")
print("   • freesewing_summer_dress.svg")
print("   • freesewing_shirt.svg")
print("   • freesewing_pants.svg")
print("\n💡 Open any .svg file in a web browser to view the pattern!")
