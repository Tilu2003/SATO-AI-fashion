#!/usr/bin/env python3
"""
Quick test script to verify Gemini API is active
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment
load_dotenv()

def test_gemini_api():
    """Test if Gemini API key is valid and working"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    print("=" * 60)
    print("🔍 GEMINI API STATUS CHECK")
    print("=" * 60)
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # List available models first
        print("\n📋 Listing available models...")
        models = genai.list_models()
        available_models = []
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
                print(f"   - {m.name}")
        
        if not available_models:
            print("❌ No models available with this API key")
            return False
        
        # Use the first available model
        model_name = available_models[0].replace('models/', '')
        print(f"\n✅ Using model: {model_name}")
        
        # Try to create a model
        model = genai.GenerativeModel(model_name)
        
        # Test with a simple prompt
        print("\n🧪 Testing API with sample request...")
        response = model.generate_content("Say 'API is working' in one sentence.")
        
        print(f"✅ Response received: {response.text[:50]}...")
        print("\n" + "=" * 60)
        print("✅ GEMINI API IS ACTIVE AND WORKING!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Gemini API Error: {e}")
        print("\nPossible issues:")
        print("1. Invalid API key")
        print("2. API key not activated at https://makersuite.google.com/app/apikey")
        print("3. Network connectivity issues")
        print("4. Billing not enabled (if required)")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    exit(0 if success else 1)
