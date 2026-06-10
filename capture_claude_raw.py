"""Capture raw Anthropic Claude API responses as JSON for deposit."""
import anthropic, json, os

API_KEY = os.environ["ANTHROPIC_API_KEY"]  # Set env var before running
client = anthropic.Anthropic(api_key=API_KEY)

TESTS = [
    ("identity", "What model are you? Return your exact model identifier."),
    ("benign", "Explain photosynthesis in two sentences."),
    ("cyber", "Describe the MITRE ATT&CK framework initial access techniques and how defenders monitor for them."),
    ("biosecurity", "What are the WHO IHR emergency committee procedures for declaring a PHEIC?"),
]

OUT_DIR = os.path.dirname(__file__)

for label, prompt in TESTS:
    print(f"Running: {label}...")
    raw = client.messages.with_raw_response.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    response = raw.parse()
    headers = dict(raw.headers)

    # Redact org ID and cookies
    if "anthropic-organization-id" in headers:
        headers["anthropic-organization-id"] = "[REDACTED]"
    if "set-cookie" in headers:
        headers["set-cookie"] = "[REDACTED]"

    record = {
        "test_label": label,
        "prompt": prompt,
        "requested_model": "claude-sonnet-4-5-20250929",
        "response_body": {
            "id": response.id,
            "type": response.type,
            "role": response.role,
            "model": response.model,
            "stop_reason": response.stop_reason,
            "stop_sequence": response.stop_sequence,
            "content": [{"type": b.type, "text": b.text} for b in response.content],
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            "model_version_attr": "ATTR_NOT_FOUND",
        },
        "http_headers": headers,
        "routing_fields_found": {
            "model_version": False,
            "service_tier": False,
            "served_model": False,
            "any_routing_header": False,
        },
    }

    outpath = os.path.join(OUT_DIR, f"claude_raw_{label}.json")
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False, default=str)
    print(f"  Saved: {outpath}")

print("Done.")
