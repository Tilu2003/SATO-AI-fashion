# ============================================================================
# FILE: master_tailor_module.py
# PURPOSE: Production planning using Llama
# ============================================================================

from typing import Dict, Any
from llm_provider import get_master_plan_with_llama

def get_master_plan(vision_analysis: Dict[str, Any]) -> Dict[str, Any]:
    return get_master_plan_with_llama(vision_analysis)

def assess_complexity(master_plan: Dict[str, Any]) -> Dict[str, Any]:
    subcategory = master_plan.get('subcategory', '').lower()
    if any(x in subcategory for x in ['gown', 'tailored', 'structured']):
        return {"level": "very_complex", "score": 90}
    if any(x in subcategory for x in ['pleated', 'draped']):
        return {"level": "moderate", "score": 60}
    return {"level": "standard", "score": 40}