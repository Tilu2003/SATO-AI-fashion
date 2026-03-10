User uploads garment photo
        ↓
[Stage 1] Gemini Vision Analysis  →  garment type, features, style
        ↓
[Stage 1] OpenCV Proportion Extraction  →  chest/waist/hip ratios
        ↓
[Stage 2] Measurement Form  →  user submits their body measurements
        ↓
[Stage 3] Fit Questions  →  conversational preference collection
        ↓
[Stage 4] Pattern Generation  →  SVG sewing pattern (Aldrich formulas)
        ↓
[Stage 5] Download  →  user gets their custom pattern SVG
```

### Key Modules


| `api_server.py` ---> Flask app, 5-stage flow orchestration |
| `vision_module.py` --->  Wraps Gemini Vision API |
| `garment_extraction.py` ---> OpenCV proportion extraction |
| `llm_provider.py` --->  Gemini + Ollama/Llama LLM clients |
| `measurement_form_generator.py` --->  Dynamic form generation per garment type |
| `fit_system_module.py` --->  Conversational fit-preference collector |
| `hybrid_engine_module.py` --->  Pattern generation orchestration |
| `pattern_drafting_engine.py` --->  Winifred Aldrich formula SVG drafter |
| `proportion_pattern_generator.py` --->  CV-enhanced pattern generation |
| `validation_module.py` --->  Pattern quality scoring |
| `tutorial_module.py` --->  Sewing tutorial links |
| `upload_handler.py` --->  Secure image upload handling |
