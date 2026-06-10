# Model Routing Transparency: Google Gemini API vs Anthropic Claude API

**Date:** 2026-06-10 ~06:07–06:30 UTC
**Author:** hiroki-tamba-research
**Method:** Same 4 prompts (identity, benign, cyber, biosecurity) sent to both APIs; response body and HTTP headers inspected for served-model identification fields.

## Test prompts

| Label | Prompt |
|---|---|
| identity | "What model are you? Return your exact model identifier." |
| benign | "Explain photosynthesis in two sentences." |
| cyber | "Describe the MITRE ATT&CK framework initial access techniques and how defenders monitor for them." |
| biosecurity | "What are the WHO IHR emergency committee procedures for declaring a PHEIC?" |

## Google Gemini API results

**SDK:** `google-genai` 1.68.0
**Models tested:** `gemini-2.5-pro`, `gemini-2.5-flash`

### gemini-2.5-pro (4/4 completed)

| Test | `response.model_version` | Thinking tokens | Total tokens |
|---|---|---|---|
| identity | `gemini-2.5-pro` | 334 | 357 |
| benign | `gemini-2.5-pro` | 920 | 977 |
| cyber | `gemini-2.5-pro` | 1,161 | 3,357 |
| biosecurity | `gemini-2.5-pro` | 1,596 | 2,962 |

### gemini-2.5-flash (4/4 completed)

| Test | `response.model_version` | Thinking tokens | Total tokens |
|---|---|---|---|
| identity | `gemini-2.5-flash` | 30 | 53 |
| benign | `gemini-2.5-flash` | 379 | 433 |
| cyber | `gemini-2.5-flash` | 1,735 | 3,608 |
| biosecurity | `gemini-2.5-flash` | 1,146 | 2,320 |

**8/8 tests: `response.model_version` = requested model.**

**HTTP response headers include:** `x-gemini-service-tier: standard` — an additional routing transparency signal absent from the Anthropic API.

## Anthropic Claude API results

**SDK:** `anthropic` (Python)
**Model tested:** `claude-sonnet-4-5-20250929`

| Test | `response.model` | `model_version` attr | Service tier header |
|---|---|---|---|
| identity | `claude-sonnet-4-5-20250929` | **ATTR_NOT_FOUND** | **absent** |
| benign | `claude-sonnet-4-5-20250929` | **ATTR_NOT_FOUND** | **absent** |
| cyber | `claude-sonnet-4-5-20250929` | **ATTR_NOT_FOUND** | **absent** |
| biosecurity | `claude-sonnet-4-5-20250929` | **ATTR_NOT_FOUND** | **absent** |

**4/4 tests: no `model_version` field in response body; no service-tier or served-model header in HTTP response.**

`response.model` echoes back the *requested* model identifier. Whether this reflects the model that actually served the response is not independently verifiable from the API response alone.

**Full HTTP header inventory (representative, from identity test):**
```
anthropic-organization-id: [redacted]
anthropic-ratelimit-input-tokens-limit: 30000
anthropic-ratelimit-input-tokens-remaining: 30000
anthropic-ratelimit-output-tokens-limit: 8000
anthropic-ratelimit-output-tokens-remaining: 8000
anthropic-ratelimit-requests-limit: 50
anthropic-ratelimit-requests-remaining: 49
cf-cache-status: DYNAMIC
cf-ray: [redacted]
content-type: application/json
request-id: [redacted]
server: cloudflare
traceresponse: [redacted]
x-robots-tag: none
```

No header containing `model`, `version`, `tier`, `route`, `served`, `backend`, or `fallback`.

## Comparison

| Transparency feature | Google Gemini API | Anthropic Claude API |
|---|---|---|
| Served model in response body | `model_version` (every response) | **absent** |
| Service tier HTTP header | `x-gemini-service-tier` | **absent** |
| Per-response routing identity | verifiable | **not verifiable** |
| Domain-specific model routing | not observed (8/8 consistent) | officially documented (Fable 5 → Opus 4.8 for cyber/bio/distillation) |

## Interpretation

Routing transparency is technically feasible — Google ships it. The absence of equivalent fields in the Anthropic API, combined with Anthropic's officially documented classifier-based model routing (Fable 5 → Opus 4.8), means that:

1. **API consumers cannot verify which model served their request.** `response.model` echoes the requested model, not necessarily the served model.
2. **Behavioral measurements of "Fable 5" in cyber/bio domains may in fact measure Opus 4.8** — and there is no API-level signal to distinguish the two.
3. **Identity/behavior probing may trigger the distillation classifier**, causing the probed model to differ from the answering model.

This is a design choice, not a technical constraint.

## Caveats

- Sonnet 4.5 was tested rather than Fable 5 or Opus 4.8 (Fable and Opus are not available via API key at this tier). The header/field inventory finding applies to the API design, not to a specific model's routing behavior.
- Google's `model_version` field confirms what model *claims* to have served — it is a vendor assertion, not an independent verification. But its presence establishes that the API surface supports this disclosure.
- The 503 errors on Gemini Pro during initial testing suggest high load (post-I/O demand); the 4 successful Pro runs came after brief retry.
- Gemini's lack of observed routing does not mean routing never occurs — only that it was not observed in these 8 tests. Google may implement silent routing in other conditions.
