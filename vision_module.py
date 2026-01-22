# ============================================================================
# FILE: vision_module.py
# PURPOSE: Wrapper for Gemini vision analysis
# ============================================================================

from typing import Dict, Any
from llm_provider import analyze_garment_with_gemini

def analyze_garment(image_path: str, user_text: str) -> Dict[str, Any]:
    return analyze_garment_with_gemini(image_path, user_text)