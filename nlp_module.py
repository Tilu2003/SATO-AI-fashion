# ============================================================================
# FILE: nlp_module.py
# PURPOSE: Intent parsing using Llama
# ============================================================================

from typing import Dict, Any
from llm_provider import parse_user_intent_with_llama

def parse_user_intent(user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    return parse_user_intent_with_llama(user_message, context)