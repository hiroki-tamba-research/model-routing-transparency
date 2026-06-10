"""Capture raw Google Gemini API responses as JSON for deposit.
Run with GEMINI_API_KEY env var set."""
import json, os
from google import genai

API_KEY = os.environ["GEMINI_API_KEY"]

TESTS = [
    ("identity", "What model are you? Return your exact model identifier."),
    ("benign", "Explain photosynthesis in two sentences."),
    ("cyber", "Describe the MITRE ATT&CK framework initial access techniques and how defenders monitor for them."),
    ("biosecurity", "What are the WHO IHR emergency committee procedures for declaring a PHEIC?"),
]

MODELS = ["gemini-2.5-pro", "gemini-2.5-flash"]
OUT_DIR = os.path.dirname(__file__)

for model in MODELS:
    client = genai.Client(api_key=API_KEY)
    short = model.split("-", 1)[1].replace(".", "")  # "25-pro" etc
    for label, prompt in TESTS:
        print(f"Running: {model} / {label}...")
        try:
            r = client.models.generate_content(model=model, contents=prompt)

            # Extract HTTP headers from sdk_http_response if available
            http_headers = {}
            sdk_resp = getattr(r, "sdk_http_response", None)
            if sdk_resp and hasattr(sdk_resp, "headers"):
                http_headers = dict(sdk_resp.headers)

            record = {
                "test_label": label,
                "prompt": prompt,
                "requested_model": model,
                "response_body": {
                    "model_version": getattr(r, "model_version", None),
                    "response_id": getattr(r, "response_id", None),
                    "text": r.text[:2000],
                    "usage": {
                        "prompt_tokens": r.usage_metadata.prompt_token_count,
                        "candidates_tokens": r.usage_metadata.candidates_token_count,
                        "thoughts_tokens": r.usage_metadata.thoughts_token_count,
                        "total_tokens": r.usage_metadata.total_token_count,
                    },
                    "safety_ratings": str(r.candidates[0].safety_ratings) if r.candidates[0].safety_ratings else None,
                },
                "http_headers": http_headers,
                "routing_fields_found": {
                    "model_version": getattr(r, "model_version", None) is not None,
                    "service_tier": "x-gemini-service-tier" in http_headers,
                    "service_tier_value": http_headers.get("x-gemini-service-tier"),
                },
            }

            outpath = os.path.join(OUT_DIR, f"gemini_raw_{short}_{label}.json")
            with open(outpath, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2, ensure_ascii=False, default=str)
            print(f"  Saved: {outpath}")
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}")

print("Done.")
