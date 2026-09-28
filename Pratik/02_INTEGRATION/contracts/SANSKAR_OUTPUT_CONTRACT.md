# SANSKAR Output Contract Documentation

This document describes SANSKAR's existing output contracts as derived from SANSKAR's FastAPI codebase ([`api.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/02_SANSKAR/Sanskar-Integration-main/api.py)).

---

## 1. POST /signal Response

When a payload is processed successfully by the `/signal` endpoint, the response returns the complete execution trace containing output sections for SANSKAR features, core decision, enforcement directives, and truth validation:

### Endpoint Details
*   **Endpoint:** `/signal`
*   **HTTP Method:** `POST`
*   **Response JSON Shape:**
```json
{
  "trace_id": "string",
  "pipeline_status": "SUCCESS",
  "input": {
    "trace_id": "string",
    "signal": {
      "dataset": "string"
    },
    "contract_version": "v1"
  },
  "sanskar_output": {
    "trace_id": "string",
    "stage": "sanskar",
    "entities": [
      {
        "entity_id": "string (Region)",
        "score": 0.0,
        "raw_score": 0.0,
        "tie_breaker": 0.0,
        "factors": [ ... ],
        "confidence": 0.0,
        "confidence_factors": { ... },
        "explanation": "string",
        "decision_state": "CONFIDENT/AMBIGUOUS/LOW_CONFIDENCE",
        "adjusted_score": 0.0,
        "adjusted_confidence": 0.0,
        "adaptive_refinement": { ... }
      }
    ],
    "ranking": ["string (Region)"],
    "comparative_explanation": { ... },
    "scenario_analysis": [ ... ],
    "downstream_decision": { ... },
    "contract_version": "v1"
  },
  "core_decision": {
    "trace_id": "string",
    "stage": "core",
    "decision": "string",
    "selected_entity": "string (Region)",
    "selected_score": 0.0,
    "selected_confidence": 0.0,
    "selected_decision_state": "string",
    "priority": "critical/high/medium/low",
    "priority_reason": "string",
    "selection_criteria": "highest_ranked_region_selected",
    "logic": "highest_ranked_region_selected",
    "all_candidates": [ ... ],
    "margin_over_runner_up": 0.0,
    "runner_up": "string",
    "reasoning": "string",
    "downstream_recommendation": { ... },
    "contract_version": "v1"
  },
  "enforcement": {
    "trace_id": "string",
    "stage": "enforcement",
    "action": "string",
    "target": "string (Region)",
    "enforcement_type": "string",
    "priority": "string",
    "decision_state": "string",
    "urgency": "immediate/current_cycle/next_cycle/passive",
    "enforcement_score": 0.0,
    "directives": [
      {
        "directive_id": "string",
        "action": "string",
        "target": "string",
        "description": "string",
        "status": "pending",
        "acknowledged": false,
        "ack_timestamp": null,
        "execution_status": "PENDING"
      }
    ],
    "enforcement_rationale": "string",
    "core_reasoning_reference": "string",
    "acknowledgment": { ... },
    "external_execution_verification": { ... },
    "governance": { ... },
    "contract_version": "v1"
  },
  "truth": {
    "verdict": "PIPELINE_COMPLETE",
    "selected_entity": "string (Region)",
    "selected_score": 0.0,
    "enforcement_action": "string",
    "enforcement_target": "string (Region)",
    "pipeline_hash": "string (sha256)",
    "chain_integrity": "VERIFIED -- SHA-256 hash computed over full chain",
    "trace_continuity": "PASS — trace_id identical across all stages",
    "trace_continuity_proof": { ... },
    "stages_completed": ["input", "sanskar", "core", "enforcement", "truth"],
    "contract_version": "v1",
    "hash_input": { ... }
  },
  "contract_version": "v1"
}
```

*   **Trace/Hash Fields:** `pipeline_hash` (calculated canonical chain hash in the `truth` section) and `trace_continuity_proof` (captures the `trace_id` comparison across execution stages).

---

## 2. GET /trace/{trace_id}

Returns the stored transaction log matching the requested `trace_id` from in-memory trace map.

*   **Endpoint:** `/trace/{trace_id}`
*   **HTTP Method:** `GET`
*   **Response JSON Shape:** Matches the successful trace payload from `POST /signal` or returns a structured `failure` payload.

---

## 3. GET /health

*   **Endpoint:** `/health`
*   **HTTP Method:** `GET`
*   **Response JSON Shape:**
```json
{
  "status": "healthy",
  "service": "sanskar",
  "contract_version": "v1"
}
```

---

## 4. GET /ranking

*   **Endpoint:** `/ranking`
*   **HTTP Method:** `GET`
*   **Response JSON Shape:**
```json
{
  "ranking": ["string (Region)"],
  "entities": [
    {
      "entity_id": "string (Region)",
      "score": 0.0,
      "confidence": 0.0,
      "decision_state": "CONFIDENT/AMBIGUOUS/LOW_CONFIDENCE"
    }
  ],
  "contract_version": "v1"
}
```

---

## 5. POST /replay Response

*   **Endpoint:** `/replay`
*   **HTTP Method:** `POST`
*   **Response JSON Shape:** Original transaction trace if hash verification succeeds, otherwise:
```json
{
  "trace_id": "string",
  "pipeline_status": "FAILED",
  "contract_version": "v1",
  "error": {
    "type": "ReplayHashMismatch",
    "code": "REPLAY_HASH_MISMATCH",
    "expected": "string (original sha256)",
    "actual": "string (replayed sha256)"
  }
}
```
