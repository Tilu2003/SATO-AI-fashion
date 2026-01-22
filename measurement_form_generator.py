# ============================================================================
# FILE: measurement_form_generator.py
# PURPOSE: Dynamic form generation and validation based on garment features
# ============================================================================

from typing import Dict, Any, List

MEASUREMENT_DEFINITIONS = {
    "highBust": {
        "name": "High Bust",
        "description": "Around chest at armpit level, above bust",
        "unit": "cm",
        "typical_range": [75, 110],
        "why": "For armhole placement",
        "measurement_guide": "Wrap tape horizontally under armpits",
        "validation_min": 60,
        "validation_max": 140
    },
    "chestCircumference": {
        "name": "Bust/Chest",
        "description": "Around fullest part of bust",
        "unit": "cm",
        "typical_range": [80, 120],
        "why": "For bodice width",
        "measurement_guide": "Tape around fullest part, parallel to floor",
        "validation_min": 65,
        "validation_max": 150
    },
    "underbust": {
        "name": "Under Bust",
        "description": "Under bust at ribcage",
        "unit": "cm",
        "typical_range": [65, 95],
        "why": "For empire waist placement",
        "measurement_guide": "Tape around ribcage below bust",
        "validation_min": 55,
        "validation_max": 120
    },
    "waistCircumference": {
        "name": "Waist",
        "description": "At natural waist",
        "unit": "cm",
        "typical_range": [60, 100],
        "why": "For waist fit",
        "measurement_guide": "Tie string, measure where it sits naturally",
        "validation_min": 50,
        "validation_max": 130
    },
    "hipCircumference": {
        "name": "Hips",
        "description": "Around fullest part of hips",
        "unit": "cm",
        "typical_range": [85, 125],
        "why": "For lower body fit",
        "measurement_guide": "Tape around widest part of hips/buttocks",
        "validation_min": 70,
        "validation_max": 160
    },
    "shoulderToShoulder": {
        "name": "Shoulder Width",
        "description": "Shoulder point to shoulder point",
        "unit": "cm",
        "typical_range": [35, 48],
        "why": "For shoulder seams",
        "measurement_guide": "Across back between shoulder bones",
        "validation_min": 30,
        "validation_max": 55
    },
    "neckCircumference": {
        "name": "Neck",
        "description": "Around base of neck",
        "unit": "cm",
        "typical_range": [32, 42],
        "why": "For collar fit",
        "measurement_guide": "Loosely around neck base",
        "validation_min": 28,
        "validation_max": 50
    },
    "hpsToWaistBack": {
        "name": "Back Length",
        "description": "Neck base to waist",
        "unit": "cm",
        "typical_range": [38, 48],
        "why": "For bodice length",
        "measurement_guide": "From prominent vertebra down to waist",
        "validation_min": 30,
        "validation_max": 60
    },
    "hpsToWaistFront": {
        "name": "Front Length",
        "description": "Shoulder/neck over bust to waist",
        "unit": "cm",
        "typical_range": [40, 52],
        "why": "For bust dart placement",
        "measurement_guide": "From shoulder, over bust, to waist",
        "validation_min": 32,
        "validation_max": 65
    },
    "shoulderToWrist": {
        "name": "Arm Length",
        "description": "Shoulder to wrist",
        "unit": "cm",
        "typical_range": [55, 70],
        "why": "For sleeve length",
        "measurement_guide": "Arm slightly bent, shoulder to wrist bone",
        "validation_min": 45,
        "validation_max": 80
    },
    "wristCircumference": {
        "name": "Wrist",
        "description": "Around wrist bone",
        "unit": "cm",
        "typical_range": [14, 20],
        "why": "For cuff fit",
        "measurement_guide": "Tape around wrist at bone",
        "validation_min": 12,
        "validation_max": 25
    },
    "bicepsCircumference": {
        "name": "Upper Arm",
        "description": "Around fullest part of upper arm",
        "unit": "cm",
        "typical_range": [25, 40],
        "why": "For sleeve width",
        "measurement_guide": "Around bicep at fullest, arm relaxed",
        "validation_min": 20,
        "validation_max": 50
    },
    "garmentLength": {
        "name": "Garment Length",
        "description": "Shoulder to desired hem",
        "unit": "cm",
        "typical_range": [50, 120],
        "why": "For overall length",
        "measurement_guide": "From shoulder to where you want hem",
        "validation_min": 30,
        "validation_max": 180
    },
    "inseam": {
        "name": "Inseam",
        "description": "Crotch to ankle",
        "unit": "cm",
        "typical_range": [70, 90],
        "why": "For pant leg length",
        "measurement_guide": "Inner leg from crotch to ankle",
        "validation_min": 55,
        "validation_max": 100
    },
    "crotchDepth": {
        "name": "Crotch Depth",
        "description": "Waist to chair when sitting",
        "unit": "cm",
        "typical_range": [25, 35],
        "why": "For trouser rise",
        "measurement_guide": "Sit, measure waist to chair surface",
        "validation_min": 20,
        "validation_max": 45
    },
    "thighCircumference": {
        "name": "Thigh",
        "description": "Around fullest part of thigh",
        "unit": "cm",
        "typical_range": [45, 70],
        "why": "For leg width",
        "measurement_guide": "Around thigh at fullest point",
        "validation_min": 35,
        "validation_max": 85
    }
}

def get_measurements_for_garment(subcategory: str, style_features: List[str]) -> Dict[str, Any]:
    """Generates dynamic form based on garment type and features"""
    subcategory = subcategory.lower()
    features = [f.lower() for f in style_features]
    required_measurements = []
    
    print(f"🔍 Determining measurements for: {subcategory}")
    print(f"🏷️  Style features: {features}")
    
    # DRESSES & BLOUSES
    if any(x in subcategory for x in ['dress', 'frock', 'gown', 'blouse', 'top']):
        # Start with absolute minimum measurements for any dress
        required_measurements.extend([
            "chestCircumference",  # Bust - ALWAYS needed
            "waistCircumference",  # Waist - ALWAYS needed
        ])
        
        # Add length measurements - ALWAYS needed
        required_measurements.extend([
            "hpsToWaistBack",      # Back length
            "hpsToWaistFront",     # Front length  
            "garmentLength"        # Total length
        ])
        
        # HIPS: Only if dress has a skirt portion, flared, or fitted lower body
        if any(x in subcategory for x in ['a_line', 'flared', 'fit', 'skirt', 'maxi', 'midi', 'mini']) or \
           any(x in ' '.join(features) for x in ['flared', 'fitted', 'a-line', 'skirt', 'tier', 'full']):
            required_measurements.append("hipCircumference")
        
        # SLEEVES: Only add if explicitly mentioned (NOT shoulder ties/straps)
        sleeve_keywords = ['sleeve', 'long sleeve', 'short sleeve', 'puff sleeve', 
                          'bell sleeve', 'cap sleeve', 'three quarter', 'full sleeve',
                          'raglan', 'dolman', 'bishop', 'flutter sleeve', 'poet sleeve']
        
        has_sleeves = any(keyword in ' '.join(features).lower() for keyword in sleeve_keywords)
        
        print(f"🔍 Sleeve check: looking for {sleeve_keywords} in {features}")
        print(f"🔍 Has sleeves: {has_sleeves}")
        
        # ONLY add sleeve measurements if explicitly has sleeves
        if has_sleeves:
            required_measurements.extend([
                "shoulderToShoulder",
                "shoulderToWrist", 
                "bicepsCircumference"
            ])
            
            # Add wrist ONLY for long sleeves
            if any(x in ' '.join(features).lower() for x in ['long sleeve', 'full sleeve', 'long-sleeve']):
                required_measurements.append("wristCircumference")
            
            print(f"✅ Added sleeve measurements")
        else:
            print(f"✅ Sleeveless - skipping arm measurements")
        
        # NECK: Only for deep V-neck, plunge, or high neck styles
        if any(x in ' '.join(features).lower() for x in ['v_neck', 'v-neck', 'v neck', 'plunge', 'deep neck', 'deep_v']):
            required_measurements.append("neckCircumference")
            print(f"✅ Added neck measurement for neckline")
        
        # UNDERBUST: Only for empire waist, fitted bodice, or corset styles
        if any(x in ' '.join(features).lower() for x in ['empire', 'corset', 'bodycon', 'fitted bodice', 'tight']):
            required_measurements.append("underbust")
            print(f"✅ Added underbust for fitted/empire style")
        
        print(f"✅ Final measurements for this dress: {required_measurements}")
    
    # TROUSERS/PANTS
    elif any(x in subcategory for x in ['trousers', 'pants', 'slacks']):
        required_measurements.extend([
            "waistCircumference", "hipCircumference", "crotchDepth",
            "inseam", "thighCircumference"
        ])
    
    # SHIRTS
    elif 'shirt' in subcategory:
        required_measurements.extend([
            "chestCircumference", "neckCircumference", "shoulderToShoulder",
            "shoulderToWrist", "wristCircumference", "hpsToWaistBack"
        ])
    
    # Build form fields
    form_fields = []
    seen = set()
    for key in required_measurements:
        if key not in seen and key in MEASUREMENT_DEFINITIONS:
            field_data = MEASUREMENT_DEFINITIONS[key].copy()
            field_data["key"] = key
            field_data["required"] = True
            form_fields.append(field_data)
            seen.add(key)
    
    return {
        "form_fields": form_fields,
        "total_count": len(form_fields),
        "garment_info": {"subcategory": subcategory, "detected_features": features}
    }

def validate_measurements(measurements: Dict[str, float], form_config: Dict[str, Any]) -> Dict[str, Any]:
    """Validates submitted measurements"""
    errors = []
    warnings = []
    validated = {}
    
    for field in form_config["form_fields"]:
        key = field["key"]
        value = measurements.get(key)
        
        if field["required"] and (value is None or value == ""):
            errors.append(f"{field['name']} is required")
            continue
        
        if value is None or value == "":
            continue
        
        try:
            value = float(value)
        except (ValueError, TypeError):
            errors.append(f"{field['name']} must be a number")
            continue
        
        if value < field["validation_min"]:
            errors.append(f"{field['name']} too small (min {field['validation_min']} cm)")
        elif value > field["validation_max"]:
            errors.append(f"{field['name']} too large (max {field['validation_max']} cm)")
        else:
            typical_min, typical_max = field["typical_range"]
            if value < typical_min or value > typical_max:
                warnings.append(f"{field['name']} ({value} cm) outside typical range ({typical_min}-{typical_max} cm)")
        
        validated[key] = value
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "validated_measurements": validated
    }