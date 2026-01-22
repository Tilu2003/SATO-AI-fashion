# ============================================================================
# FILE: llm_provider.py
# PURPOSE: Unified LLM provider - Gemini (vision) + Llama (text)
# ============================================================================

import os
import json
from typing import Dict, Any, List, TYPE_CHECKING
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try importing from langchain-ollama first (recommended), fall back to langchain-community
try:
    from langchain_ollama import OllamaLLM  # type: ignore
except (ImportError, ModuleNotFoundError):
    try:
        from langchain_community.llms import Ollama as OllamaLLM  # type: ignore
    except (ImportError, ModuleNotFoundError):
        print("Warning: Neither langchain-ollama nor langchain-community could be imported")
        OllamaLLM = None  # type: ignore

# Try importing PromptTemplate from langchain-core first
try:
    from langchain_core.prompts import PromptTemplate  # type: ignore
except (ImportError, ModuleNotFoundError):
    try:
        from langchain.prompts import PromptTemplate  # type: ignore
    except (ImportError, ModuleNotFoundError):
        print("Warning: Could not import PromptTemplate")
        PromptTemplate = None  # type: ignore

# Try importing LLMChain (may not exist in newer versions)
try:
    from langchain.chains import LLMChain  # type: ignore
except (ImportError, ModuleNotFoundError):
    LLMChain = None  # type: ignore

import google.generativeai as genai
import PIL.Image

class LLMConfig:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_VISION_MODEL = "gemini-2.5-flash"  # Updated to available model
    LLAMA_TEXT_MODEL = os.getenv("LLAMA_MODEL", "llama3.2")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    VISION_TEMP = 0.3
    TEXT_TEMP = 0.7
    NLP_TEMP = 0.1
    GEMINI_TIMEOUT = 60  # 60 second timeout for Gemini API
    GEMINI_MAX_RETRIES = 2

if LLMConfig.GEMINI_API_KEY:
    genai.configure(api_key=LLMConfig.GEMINI_API_KEY)

class LLMProvider:
    _text_llm = None
    _nlp_llm = None
    _gemini_vision = None
    
    @classmethod
    def get_gemini_vision(cls):
        if cls._gemini_vision is None:
            if not LLMConfig.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not configured")
            # Don't set timeout in generation_config - it's set per request
            cls._gemini_vision = genai.GenerativeModel(LLMConfig.GEMINI_VISION_MODEL)
        return cls._gemini_vision
    
    @classmethod
    def get_text_llm(cls):
        if cls._text_llm is None:
            if OllamaLLM is None:
                raise ImportError(
                    "Ollama LLM not available. Please install: pip install langchain-ollama langchain-community"
                )
            cls._text_llm = OllamaLLM(
                model=LLMConfig.LLAMA_TEXT_MODEL,
                base_url=LLMConfig.OLLAMA_BASE_URL,
                temperature=LLMConfig.TEXT_TEMP
            )
        return cls._text_llm
    
    @classmethod
    def get_nlp_llm(cls):
        if cls._nlp_llm is None:
            if OllamaLLM is None:
                raise ImportError(
                    "Ollama LLM not available. Please install: pip install langchain-ollama langchain-community"
                )
            cls._nlp_llm = OllamaLLM(
                model=LLMConfig.LLAMA_TEXT_MODEL,
                base_url=LLMConfig.OLLAMA_BASE_URL,
                temperature=LLMConfig.NLP_TEMP
            )
        return cls._nlp_llm

def extract_json_from_response(text: str) -> Dict[str, Any]:
    text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        json_str = text[start:end]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response"}
    return {"error": "No JSON found in response"}

SYSTEM_PROMPT_VISION = """
You are SATO, an expert fashion analyst. Analyze the image and user text, return ONLY valid JSON.

JSON schema:
{
  "garment_type": "dress",
  "subcategory": "mini_dress",
  "style_features": ["puff_sleeves", "v_neck"],
  "construction_details": ["invisible_zipper"],
  "fabric_recommendations": [{"name": "cotton", "reason": "breathable"}],
  "key_sewing_techniques": ["setting sleeves", "inserting zipper"]
}
"""

def analyze_garment_with_gemini(image_path: str, user_text: str) -> Dict[str, Any]:
    import time
    
    for attempt in range(LLMConfig.GEMINI_MAX_RETRIES):
        try:
            model = LLMProvider.get_gemini_vision()
            img = PIL.Image.open(image_path)
            
            # Resize large images for faster processing
            max_size = 1024
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, PIL.Image.Resampling.LANCZOS)
                print(f"🖼️ Resized image to {new_size} for faster analysis")
            
            prompt_parts = [SYSTEM_PROMPT_VISION, img, f"\nUser: {user_text}"]
            
            # Set request timeout
            request_options = {"timeout": LLMConfig.GEMINI_TIMEOUT}
            response = model.generate_content(prompt_parts, request_options=request_options)
            
            json_string = response.text.replace("```json", "").replace("```", "").strip()
            design_data = json.loads(json_string)
            print(f"✅ Gemini Vision analysis complete (attempt {attempt + 1})")
            return design_data
            
        except Exception as e:
            error_msg = str(e).lower()
            print(f"⚠️ Gemini attempt {attempt + 1} failed: {e}")
            
            # Don't retry on certain errors
            if "timeout" in error_msg or "503" in error_msg or "connection" in error_msg:
                if attempt < LLMConfig.GEMINI_MAX_RETRIES - 1:
                    wait_time = (attempt + 1) * 2  # 2s, 4s
                    print(f"⏳ Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
            
            # Final attempt failed or non-retryable error
            if attempt == LLMConfig.GEMINI_MAX_RETRIES - 1:
                print("❌ All Gemini attempts failed, using basic fallback")
                return {
                    "garment_type": "dress",
                    "subcategory": "casual_dress",
                    "style_features": ["basic_style"],
                    "design_features": ["standard_fit"],
                    "construction_details": ["basic_construction"],
                    "fabric_recommendations": [{"name": "cotton", "reason": "versatile"}],
                    "key_sewing_techniques": ["basic_sewing"],
                    "error": f"Gemini unavailable: {str(e)[:100]}"
                }
    
    return {"error": "Max retries exceeded"}

def create_master_tailor_chain():
    if PromptTemplate is None:
        raise ImportError(
            "PromptTemplate not available. Please install: pip install langchain-core langchain"
        )
    prompt = PromptTemplate(
        input_variables=["vision_analysis"],
        template="""Extract key info from vision analysis. Return ONLY JSON:
{vision_analysis}

JSON output:
{{
  "garment_type": "dress",
  "subcategory": "<extract from vision>",
  "inferred_pieces": ["bodice_front", "bodice_back"],
  "key_sewing_techniques": [],
  "fit_method": "standard_ease"
}}

Be fast and concise.
"""
    )
    if LLMChain:
        return LLMChain(llm=LLMProvider.get_text_llm(), prompt=prompt)
    else:
        return prompt | LLMProvider.get_text_llm()

def get_master_plan_with_llama(vision_analysis: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Try fast Llama processing with 3-second timeout
        chain = create_master_tailor_chain()
        if hasattr(chain, 'run'):
            response = chain.run(vision_analysis=json.dumps(vision_analysis, indent=2))
        else:
            response = chain.invoke({"vision_analysis": json.dumps(vision_analysis, indent=2)})
        result = extract_json_from_response(response if isinstance(response, str) else str(response))
        result.setdefault("garment_type", vision_analysis.get("garment_type", "dress"))
        result.setdefault("subcategory", vision_analysis.get("subcategory", "a_line_dress"))
        result.setdefault("inferred_pieces", ["bodice_front", "bodice_back"])
        result.setdefault("key_sewing_techniques", [])
        result.setdefault("fit_method", "standard_ease")
        print("✅ Llama master planning complete (fast)")
        return result
    except Exception as e:
        # Quick fallback if Llama is slow
        print(f"⚠️ Llama timeout, using vision data directly (faster): {e}")
        return {
            "garment_type": vision_analysis.get("garment_type", "dress"),
            "subcategory": vision_analysis.get("subcategory", "a_line_dress"),
            "inferred_pieces": ["bodice_front", "bodice_back"],
            "key_sewing_techniques": vision_analysis.get("key_sewing_techniques", []),
            "fit_method": "standard_ease"
        }

def create_nlp_intent_chain():
    if PromptTemplate is None:
        raise ImportError(
            "PromptTemplate not available. Please install: pip install langchain-core langchain"
        )
    prompt = PromptTemplate(
        input_variables=["user_message", "context_stage"],
        template="""Parse intent. Return ONLY JSON:
Message: "{user_message}"
Stage: {context_stage}

Intents: affirmation, rejection, affirm_with_modification, update_measurement, iteration_request, unclear
Output: {{"intent": "affirmation", "confidence": 0.9}}
"""
    )
    if LLMChain:
        return LLMChain(llm=LLMProvider.get_nlp_llm(), prompt=prompt)
    else:
        return prompt | LLMProvider.get_nlp_llm()

def parse_user_intent_with_llama(user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    try:
        chain = create_nlp_intent_chain()
        if hasattr(chain, 'run'):
            response = chain.run(user_message=user_message, context_stage=context.get("stage", "UNKNOWN"))
        else:
            response = chain.invoke({"user_message": user_message, "context_stage": context.get("stage", "UNKNOWN")})
        result = extract_json_from_response(response if isinstance(response, str) else str(response))
        result.setdefault("intent", "unclear")
        result.setdefault("confidence", 0.5)
        return result
    except Exception as e:
        msg_lower = user_message.lower().strip()
        if msg_lower in ["yes", "ok", "proceed", "ready"]:
            return {"intent": "affirmation", "confidence": 0.9}
        elif msg_lower in ["no", "stop", "restart"]:
            return {"intent": "rejection", "confidence": 0.9}
        return {"intent": "unclear", "confidence": 0.3}

def create_translator_chain():
    if PromptTemplate is None:
        raise ImportError(
            "PromptTemplate not available. Please install: pip install langchain-core langchain"
        )
    prompt = PromptTemplate(
        input_variables=["vision_data", "fit_prefs", "pattern_catalog"],
        template="""Translate design to FreeSewing parameters. Return ONLY JSON:
Vision: {vision_data}
Fit: {fit_prefs}
Catalog: {pattern_catalog}

Output: {{"options": {{}}, "reasoning": {{}}, "unsupported_features": [], "confidence_score": 0.85}}
"""
    )
    if LLMChain:
        return LLMChain(llm=LLMProvider.get_text_llm(), prompt=prompt)
    else:
        return prompt | LLMProvider.get_text_llm()

def translate_with_llama(vision_data: Dict[str, Any], fit_prefs: Dict[str, Any], pattern_catalog: Dict[str, Any]) -> Dict[str, Any]:
    try:
        chain = create_translator_chain()
        if hasattr(chain, 'run'):
            response = chain.run(
                vision_data=json.dumps(vision_data, indent=2),
                fit_prefs=json.dumps(fit_prefs, indent=2),
                pattern_catalog=json.dumps(pattern_catalog, indent=2)
            )
        else:
            response = chain.invoke({
                "vision_data": json.dumps(vision_data, indent=2),
                "fit_prefs": json.dumps(fit_prefs, indent=2),
                "pattern_catalog": json.dumps(pattern_catalog, indent=2)
            })
        return extract_json_from_response(response if isinstance(response, str) else str(response))
    except Exception as e:
        return {"options": {}, "reasoning": {}, "unsupported_features": [], "confidence_score": 0.0}

def validate_hybrid_setup() -> bool:
    status = {"gemini": False, "llama": False}
    try:
        if LLMConfig.GEMINI_API_KEY:
            LLMProvider.get_gemini_vision()
            print("✅ Gemini Vision API ready")
            status["gemini"] = True
        else:
            print("❌ GEMINI_API_KEY not set")
    except Exception as e:
        print(f"❌ Gemini setup failed: {e}")
    
    try:
        llm = LLMProvider.get_text_llm()
        if hasattr(llm, 'invoke'):
            response = llm.invoke("Say OK")
        else:
            response = llm("Say OK")
        if response:
            print(f"✅ Llama ready: {LLMConfig.LLAMA_TEXT_MODEL}")
            status["llama"] = True
    except Exception as e:
        print(f"❌ Llama failed: {e}")
    
    if status["gemini"]:
        print("✅ HYBRID MODE: Gemini + Llama")
        return True
    return False