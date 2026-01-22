# ============================================================================
# FILE: adaptive_translator.py
# PURPOSE: Translates style features to FreeSewing parameters
# ============================================================================

from typing import Dict, Any
from llm_provider import translate_with_llama

FREESEWING_PARAMETER_CATALOG = {
    "breanna": {
        "description": "Women's bodice block (dresses, tops, blouses)",
        "available_options": {
            "chestEase": {"type": "percentage", "default": 0.05, "range": [0, 0.3]},
            "waistEase": {"type": "percentage", "default": 0.05, "range": [0, 0.3]},
            "lengthBonus": {"type": "percentage", "default": 0, "range": [-0.4, 0.8]},
            "sleeveLengthBonus": {"type": "percentage", "default": 0, "range": [-0.5, 0.3]},
            "sleevecapEase": {"type": "percentage", "default": 0, "range": [0, 0.15]},
            "bicepsEase": {"type": "percentage", "default": 0.1, "range": [0, 0.3]}
        }
    },
    "bella": {
        "description": "Women's bodice block with more customization",
        "available_options": {
            "chestEase": {"type": "percentage", "default": 0.05, "range": [0, 0.3]},
            "waistEase": {"type": "percentage", "default": 0.05, "range": [0, 0.3]},
            "bustSpanEase": {"type": "percentage", "default": 0, "range": [-0.05, 0.1]},
            "lengthBonus": {"type": "percentage", "default": 0, "range": [-0.3, 0.6]}
        }
    },
    "sandy": {
        "description": "Circle skirt pattern (skirts, dress bottoms)",
        "available_options": {
            "waistEase": {"type": "percentage", "default": 0.05, "range": [0, 0.2]},
            "lengthBonus": {"type": "percentage", "default": 0, "range": [-0.3, 0.8]},
            "fullness": {"type": "percentage", "default": 1.0, "range": [0.5, 2.0]}
        }
    },
    "wahid": {
        "description": "Classic waistcoat/vest pattern",
        "available_options": {
            "chestEase": {"type": "percentage", "default": 0.08, "range": [0.02, 0.25]},
            "waistEase": {"type": "percentage", "default": 0.05, "range": [0, 0.2]},
            "lengthBonus": {"type": "percentage", "default": 0, "range": [-0.15, 0.3]}
        }
    },
    "charlie": {
        "description": "Chinos/pants pattern (for dress bottoms)",
        "available_options": {
            "waistEase": {"type": "percentage", "default": 0.05, "range": [0, 0.2]},
            "seatEase": {"type": "percentage", "default": 0.05, "range": [0, 0.15]},
            "lengthBonus": {"type": "percentage", "default": 0, "range": [-0.2, 0.3]}
        }
    },
    "simon": {
        "description": "Men's shirt block (collared shirts)",
        "available_options": {
            "chestEase": {"type": "percentage", "default": 0.1, "range": [0.02, 0.3]},
            "lengthBonus": {"type": "percentage", "default": 0, "range": [-0.3, 0.5]},
            "sleeveLengthBonus": {"type": "percentage", "default": 0, "range": [-0.4, 0.2]}
        }
    }
}

def translate_with_llm(vision_data: Dict[str, Any], fit_prefs: Dict[str, Any], pattern_name: str) -> Dict[str, Any]:
    """Uses Llama to translate design features and fit preferences to FreeSewing parameters"""
    
    pattern_catalog = FREESEWING_PARAMETER_CATALOG.get(pattern_name, {})
    if not pattern_catalog:
        return {"options": {}, "reasoning": {}, "unsupported_features": ["unknown_pattern"], "confidence_score": 0.0}
    
    result = translate_with_llama(vision_data, fit_prefs, pattern_catalog)
    
    # Validate and constrain parameters to safety ranges
    validated_options = {}
    for param, value in result.get("options", {}).items():
        if param in pattern_catalog.get("available_options", {}):
            param_spec = pattern_catalog["available_options"][param]
            min_val, max_val = param_spec["range"]
            
            try:
                float_value = float(value)
                # Clamp the value between min and max range
                validated_options[param] = max(min_val, min(max_val, float_value))
            except (ValueError, TypeError):
                # Ignore invalid values, stick to defaults if necessary
                print(f"⚠️ Translator returned invalid value for {param}: {value}")
    
    result["options"] = validated_options
    return result

def select_optimal_pattern(vision_data: Dict[str, Any]) -> str:
    """Selects best FreeSewing pattern for ANY garment with comprehensive fallback"""
    subcategory = vision_data.get('subcategory', '').lower()
    garment_type = vision_data.get('garment_type', '').lower()
    style_features = [str(f).lower() for f in vision_data.get('style_features', [])]
    design_features = [str(f).lower() for f in vision_data.get('design_features', [])]
    
    # Combine all text for keyword matching
    all_text = f"{subcategory} {garment_type} {' '.join(style_features)} {' '.join(design_features)}"
    
    print(f"🔍 Pattern selection analyzing: {subcategory}")
    print(f"   Features: {style_features[:3]}...")
    
    # Priority 1: Specific pattern keywords
    if any(x in all_text for x in ['skirt', 'maxi', 'midi', 'a-line', 'flared', 'circle', 'tiered']):
        print("   ✅ Selected: SANDY (skirt/flared pattern)")
        return "sandy"
    
    # Priority 2: Fitted/tailored dresses
    elif any(x in all_text for x in ['fitted', 'bodycon', 'pencil', 'sheath', 'tailored', 'structured']):
        print("   ✅ Selected: BELLA (fitted bodice)")
        return "bella"
    
    # Priority 3: Casual/standard dresses (MOST COMMON)
    elif any(x in all_text for x in ['dress', 'blouse', 'top', 'mini', 'casual', 'sundress', 'day dress', 'cocktail', 'shift']):
        print("   ✅ Selected: BREANNA (standard dress/top)")
        return "breanna"
    
    # Priority 4: Men's shirts
    elif any(x in all_text for x in ['shirt', 'button-up', 'collared']):
        print("   ✅ Selected: SIMON (shirt pattern)")
        return "simon"
    
    # Priority 5: Vests/waistcoats
    elif any(x in all_text for x in ['vest', 'waistcoat', 'sleeveless jacket']):
        print("   ✅ Selected: WAHID (vest pattern)")
        return "wahid"
    
    # Priority 6: Pants/trousers (rare for dresses, but handle it)
    elif any(x in all_text for x in ['pant', 'trouser', 'chino']):
        print("   ✅ Selected: CHARLIE (pants pattern)")
        return "charlie"
    
    # UNIVERSAL FALLBACK: If nothing matches, use breanna (most versatile)
    print("   ⚠️  No specific match - using BREANNA (universal fallback)")
    print(f"   📝 Garment type: {garment_type or 'unknown'}")
    return "breanna"  # Breanna works for 90% of women's garments