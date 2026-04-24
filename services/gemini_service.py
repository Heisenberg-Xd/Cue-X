from config import GEMINI_API_KEY

gemini_client = None
GEMINI_MODELS = ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-3-flash-preview', 'gemini-flash-latest']

if GEMINI_API_KEY:
    try:
        from google import genai as _genai
        gemini_client = _genai.Client(api_key=GEMINI_API_KEY)
        print("[OK] Gemini AI (google-genai) loaded successfully")
    except ImportError:
        print("[WARN] google-genai not installed. Run: pip install google-genai")
    except Exception as e:
        print(f"[WARN] Gemini load failed: {e}")
else:
    print("[WARN] GEMINI_API_KEY not set -- chat and AI summary will use fallback mode")

def gemini_generate(prompt: str) -> str:
    """Call Gemini, auto-fallback across model list on quota errors."""
    if not gemini_client:
        raise RuntimeError("Gemini client not initialised")
    last_err = None
    for model in GEMINI_MODELS:
        try:
            resp = gemini_client.models.generate_content(model=model, contents=prompt)
            return resp.text.strip()
        except Exception as e:
            last_err = e
            if '429' not in str(e) and 'RESOURCE_EXHAUSTED' not in str(e):
                raise   # Non-quota error — don't retry other models
            print(f"[WARN] {model} quota hit, trying next model...")
    raise RuntimeError(f"All Gemini models quota-exhausted: {last_err}")
