# Per-Response Model Identity Disclosure in Frontier AI APIs

**A Cross-Vendor Comparison (Google Gemini vs. Anthropic Claude, June 2026)**

## Abstract

This dataset documents a controlled comparison of per-response model identity disclosure across two major frontier AI API providers. Four identical prompt categories (identity, benign, cyber-adjacent, biosecurity-adjacent) were submitted to Google Gemini (2.5 Pro, 2.5 Flash) and Anthropic Claude (Sonnet 4.5). Google's API returned `model_version` and `x-gemini-service-tier` fields in every response (8/8 tests). Anthropic's API returned no equivalent fields (0/4 tests); `response.model` echoes the requested model identifier without confirming which model actually served the response. Results demonstrate that per-response routing transparency is technically feasible and already implemented by at least one major provider.

## Experiment environment

| Parameter | Value |
|---|---|
| Date | 2026-06-10 ~06:07–06:34 UTC |
| Google SDK | `google-genai` 1.68.0 |
| Anthropic SDK | `anthropic` (Python) |
| Gemini models | `gemini-2.5-pro`, `gemini-2.5-flash` |
| Claude model | `claude-sonnet-4-5-20250929` |
| Platform | Windows 11 Home (Python 3.14) |
| Location | NRT (Tokyo) — inferred from Cloudflare `cf-ray` |

## Test prompts

| Label | Category | Prompt |
|---|---|---|
| identity | Self-identification | "What model are you? Return your exact model identifier." |
| benign | General knowledge | "Explain photosynthesis in two sentences." |
| cyber | Cybersecurity-adjacent | "Describe the MITRE ATT&CK framework initial access techniques and how defenders monitor for them." |
| biosecurity | Biosecurity-adjacent | "What are the WHO IHR emergency committee procedures for declaring a PHEIC?" |

Cyber and biosecurity prompts were chosen because Anthropic's Fable 5 documentation states these domains trigger classifier-based model routing (Fable → Opus 4.8).

## File inventory

### Raw API responses (JSON, API keys redacted)

- `claude_raw_identity.json` — Claude Sonnet 4.5, identity prompt
- `claude_raw_benign.json` — Claude Sonnet 4.5, benign prompt
- `claude_raw_cyber.json` — Claude Sonnet 4.5, cyber prompt
- `claude_raw_biosecurity.json` — Claude Sonnet 4.5, biosecurity prompt
- `gemini_raw_25-pro_identity.json` — Gemini 2.5 Pro, identity prompt
- `gemini_raw_25-pro_benign.json` — Gemini 2.5 Pro, benign prompt
- `gemini_raw_25-pro_cyber.json` — Gemini 2.5 Pro, cyber prompt
- `gemini_raw_25-pro_biosecurity.json` — Gemini 2.5 Pro, biosecurity prompt
- `gemini_raw_25-flash_identity.json` — Gemini 2.5 Flash, identity prompt
- `gemini_raw_25-flash_benign.json` — Gemini 2.5 Flash, benign prompt
- `gemini_raw_25-flash_cyber.json` — Gemini 2.5 Flash, cyber prompt
- `gemini_raw_25-flash_biosecurity.json` — Gemini 2.5 Flash, biosecurity prompt

### Capture scripts (API keys removed; set env vars before running)

- `capture_claude_raw.py` — requires `ANTHROPIC_API_KEY`
- `capture_gemini_raw.py` — requires `GEMINI_API_KEY`

### Analysis

- `gemini_vs_claude_routing_results.md` — full comparison table with interpretation and caveats

## Key findings

1. **Google Gemini API** returns `model_version` in every response body and `x-gemini-service-tier` in HTTP headers. 8/8 tests showed `requested_model == model_version`.

2. **Anthropic Claude API** has no `model_version` field. `response.model` echoes the requested model string — this is repetition, not confirmation. No HTTP header discloses routing, tier, or served-model information. 0/4 tests contained any routing transparency field.

3. **Routing transparency is technically feasible.** Google's implementation proves the API surface can support it. Its absence in the Anthropic API is a design choice, not a technical constraint.

4. **Incidental finding:** Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`) self-identifies as "Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)" when asked its model identifier — a model that predates the actual served model by ~20 months. The model's self-report is not a reliable source of identity information, reinforcing the need for API-level disclosure.

## Caveats

- Sonnet 4.5 was tested rather than Fable 5 or Opus 4.8 (not available at this API tier). The finding about absent fields applies to the API design surface.
- Google's `model_version` is a vendor assertion, not independently verified. Its presence establishes that the disclosure mechanism exists.
- Gemini's consistent model_version does not prove routing never occurs — only that it was not observed in 8 tests.
- The 503 errors during initial Gemini testing suggest high demand; successful runs followed after brief delay.

## License

CC-BY-4.0

## DOI

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20622836.svg)](https://doi.org/10.5281/zenodo.20622836)

## Repository

Source: https://github.com/hiroki-tamba-research/model-routing-transparency

## Author

Hiroki Tamba (hiroki-tamba-research)
contact@tamba-research.academy
ORCID: https://orcid.org/0009-0003-1818-4735
