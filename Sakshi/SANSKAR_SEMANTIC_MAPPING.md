# SANSKAR_SEMANTIC_MAPPING

**Owner:** Sakshi Thakur — Group 2  
**Workstream:** SANSKAR Semantic Integration  
**E2E Fixture:** `TC-Z03-F02-LIDAR-OBS001`  
**Status:** Semantic mapping implemented; automated acceptance tests CI-verified; live runtime E2E pending runtime contract confirmation.

## 1. Purpose

Define the semantic relationship between the canonical VANA observation, Scientific Context, SANSKAR, and the resulting contextual result.

### Acceptance rule

Every contextual result must remain traceable to:

1. the original VANA `observation_id`; and
2. the scientific evidence used to contextualise it through `source_id` and/or citation.

## 2. Semantic Flow

```text
Canonical Observation
 ├─ observation_id
 ├─ location
 ├─ timestamp
 └─ measurement
       +
Scientific Context
 ├─ parameter
 ├─ source/source_id
 ├─ citation
 ├─ confidence
 └─ quality
       ↓
    SANSKAR
       ↓
 Contextual Result
 ├─ original observation_id
 ├─ preserved observation
 ├─ scientific provenance
 ├─ contextual result
 └─ trace
```

## 3. Field Mapping

| Domain | Input Field | Result Field | Rule |
|---|---|---|---|
| Observation | `observation_id` | `observation.observation_id` | Preserve unchanged |
| Observation | `parameter` | `observation.parameter` | Preserve unchanged |
| Observation | `value` | `observation.value` | Preserve unchanged |
| Observation | `unit` | `observation.unit` | Preserve unchanged |
| Observation | `timestamp` | `observation.timestamp` | Preserve source observation time |
| Observation | `location` | `observation.location` | Preserve coordinates unchanged |
| Observation | `geo_id` | `observation.geo_id` | Preserve when present |
| Provenance | `source_id` | `provenance.source_id` | Preserve source identity |
| Provenance | `citation` | `provenance.citation` | Preserve; never invent |
| Provenance | `verification_status` | `provenance.verification_status` | Preserve explicit status |
| Context | `confidence` | `provenance.confidence` | Keep separate from quality |
| Context | `quality` | `provenance.quality` | Keep separate from confidence |
| Context | `uncertainty` | `provenance.uncertainty` | Preserve; null if unavailable |
| SANSKAR | derived assessment | `contextual_result` | Derived only |
| SANSKAR | trace information | `trace` | Separate from source observation |

## 4. Immutable Source-Owned Fields

SANSKAR/contextualisation must not mutate:

- `observation_id`
- observation parameter
- measurement/value
- unit
- observation timestamp/date
- location / coordinates
- `geo_id`
- source identity
- citation
- source verification status
- confidence
- quality
- uncertainty

If processing time is required, it must be a separate field such as `processed_at`.

## 5. E2E Fixture

### Observation

```text
observation_id = TC-Z03-F02-LIDAR-OBS001
parameter      = canopy_height
value          = 4.7
unit           = m
timestamp      = 2026-08-13T09:14:22Z
location       = {lat: 19.1288, lon: 72.9421}
quality_status = VALIDATED
```

### Verified Scientific Context

```text
parameter_name      = expected_canopy_height
reference_value     = 4.8 m
range               = 3.5–6.5 m
confidence_score    = 0.85
validation_status   = VERIFIED
source              = ScienceDirect / Elsevier (2023)
DOI                 = 10.1016/j.rsma.2023.103207
```

**Critical rule:** the scientific reference `4.8 m` must never overwrite the observed measurement `4.7 m`.

## 6. Preservation Acceptance Tests

The contextual result must satisfy:

```text
result.observation.observation_id == input.observation.observation_id
result.observation.location        == input.observation.location
result.observation.timestamp       == input.observation.timestamp
result.observation.value            == input.observation.value
result.observation.parameter       == input.observation.parameter
result.observation.unit             == input.observation.unit
```

## 7. Provenance Acceptance Test

The result must retain both:

```text
Original observation
    observation_id
        +
Scientific evidence
    source_id / citation
```

Confidence and quality remain independent fields.

## 8. GAP / UNKNOWN / NOT_VERIFIED

These states represent evidence/context state and must not be converted into negative scientific conclusions.

- `GAP` = required context is unavailable.
- `UNKNOWN` = information/applicability is not established.
- `NOT_VERIFIED` = information exists or is expected but is not verified.

## 9. Contextual Result

Derived fields remain separate:

```json
{
  "contextual_result": {
    "parameter_evaluated": "canopy_height",
    "reference_value": 4.8,
    "deviation": null,
    "anomaly_detected": null,
    "assessment": "..."
  },
  "trace": {
    "trace_id": "..."
  }
}
```

The exact runtime fields are subject to the authoritative SANSKAR runtime contract.

## 10. Current Status

| Item | Status |
|---|---|
| Observation → Context mapping | PASS |
| E2E semantic tests | PASS — 9/9 locally |
| GitHub Actions semantic tests | PASS |
| Provenance preservation test | PASS |
| Scientific Context | VERIFIED |
| SANSKAR semantic input/output mapping | READY |
| Cross-group semantic dependency | Substantially closed |
| Live Group 1 endpoint/trace confirmation | PENDING |
| Authoritative Group 4 runtime I/O contract | PENDING |
| Live SANSKAR E2E | PENDING |

## 11. Ownership Boundary

Group 2 owns the semantic mapping. Group 4 should align its Action Request/runtime implementation to this semantic mapping and document any additional runtime-specific fields separately rather than creating a competing semantic contract.

## 12. Acceptance

Semantic integration is accepted when the live contextual result proves:

1. original `observation_id` is unchanged;
2. location, timestamp, measurement, parameter and unit are unchanged;
3. scientific source/citation is traceable;
4. confidence and quality remain separate;
5. contextual result is traceable to both observation and scientific evidence;
6. derived SANSKAR fields do not overwrite source-owned fields.
