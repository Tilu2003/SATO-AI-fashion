"""
Test Computer Vision Garment Extraction
"""

import os
import sys
from PIL import Image
import cv2
import numpy as np

# Test if OpenCV is working
print("=" * 60)
print("Testing Computer Vision Setup")
print("=" * 60)

# 1. Check imports
print("\n1. Checking imports...")
try:
    import cv2
    print(f"   ✅ OpenCV version: {cv2.__version__}")
except ImportError as e:
    print(f"   ❌ OpenCV import failed: {e}")
    sys.exit(1)

try:
    import numpy as np
    print(f"   ✅ NumPy version: {np.__version__}")
except ImportError as e:
    print(f"   ❌ NumPy import failed: {e}")
    sys.exit(1)

try:
    from PIL import Image
    print(f"   ✅ Pillow version: {Image.__version__}")
except ImportError as e:
    print(f"   ❌ Pillow import failed: {e}")
    sys.exit(1)

# 2. Check our modules
print("\n2. Checking custom modules...")
try:
    from garment_extraction import GarmentProportionExtractor, match_proportions_to_formulas
    print("   ✅ garment_extraction.py imported")
except ImportError as e:
    print(f"   ❌ garment_extraction.py import failed: {e}")
    sys.exit(1)

try:
    from proportion_pattern_generator import ProportionBasedPatternGenerator
    print("   ✅ proportion_pattern_generator.py imported")
except ImportError as e:
    print(f"   ❌ proportion_pattern_generator.py import failed: {e}")
    sys.exit(1)

# 3. Test with sample image
print("\n3. Testing CV extraction...")

# Create a simple test image (dress silhouette)
test_image = np.ones((600, 400, 3), dtype=np.uint8) * 255  # White background

# Draw a simple dress shape
dress_points = np.array([
    [150, 100],   # Left shoulder
    [250, 100],   # Right shoulder
    [250, 200],   # Right underarm
    [240, 300],   # Right waist
    [280, 500],   # Right hem
    [200, 500],   # Center hem
    [120, 500],   # Left hem
    [160, 300],   # Left waist
    [150, 200],   # Left underarm
], dtype=np.int32)

cv2.fillPoly(test_image, [dress_points], (100, 100, 100))  # Gray dress

# Save test image
test_path = "test_garment.png"
cv2.imwrite(test_path, test_image)
print(f"   ✅ Created test image: {test_path}")

# Test extraction
try:
    # Mock analysis
    mock_analysis = {
        "garment_type": "dress",
        "features": ["sleeveless", "A-line"]
    }
    
    extractor = GarmentProportionExtractor(test_path, mock_analysis)
    print("   ✅ GarmentProportionExtractor created")
    
    # Try extracting outline
    mask = extractor.extract_garment_outline()
    print(f"   ✅ Garment outline extracted (mask shape: {mask.shape})")
    
    # Try detecting key points (doesn't need mask parameter)
    key_points = extractor.detect_key_points()
    print(f"   ✅ Key points detected: {len(key_points)} points")
    
    # Try calculating proportions
    temp_measurements = {"chest": 90}
    proportions = extractor.calculate_proportions(key_points, temp_measurements)
    print(f"   ✅ Proportions calculated: {list(proportions.keys())}")
    
    # Try formula adjustments
    adjustments = match_proportions_to_formulas(proportions, "dress")
    print(f"   ✅ Formula adjustments: {list(adjustments.get('adjustments', {}).keys())}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nExtracted Proportions:")
    for key, value in proportions.items():
        if isinstance(value, float):
            print(f"  - {key}: {value:.2f}")
        else:
            print(f"  - {key}: {value}")
    
    print("\nFormula Adjustments:")
    for key, value in adjustments.get('adjustments', {}).items():
        print(f"  - {key}: {value}")
    
    # Clean up
    os.remove(test_path)
    print(f"\n🧹 Cleaned up test file")
    
except Exception as e:
    print(f"   ❌ CV extraction test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🎉 Computer Vision system is ready!")
print("The server will now extract proportions from uploaded garment photos.")
