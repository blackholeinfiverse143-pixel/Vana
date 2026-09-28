# Group 2 Contextualisation Contract Documentation

This document defines the Group 2 Contextualisation Contract used for integrating Thane Creek Mangrove observations with scientific context baselines.

> [!IMPORTANT]  
> **SANSKAR currently exposes no domain-agnostic environmental contextualisation endpoint.**  
> The current SANSKAR `/signal` endpoint is strictly agricultural/domain-specific and is NOT a scientifically valid Thane Creek contextualisation contract. The SANSKAR core model is coupled to crop yields and agricultural scoring parameters. Any attempt to map environmental data into SANSKAR's agricultural schema violates VANA's semantic integrity constraints. 
> 
> Therefore, this contract defines the domain-appropriate **external validation and contextualisation payload** processed outside SANSKAR core.

---

## 1. Input Contract Payload Schema

The integration layer expects a machine-readable payload combining the canonical observation with the scientific baseline context. The adapter supports two variants of the context record schema:

### Payload Wrapper
```json
{
  "trace_id": "string (format: TRACE-xxxxxxxxxxxx)",
  "observation": {
    "observation_id": "string",
    "status": "SYNTHETIC_TEST | VERIFIED",
    "measurement": {
      "parameter": "string (e.g. canopy_height / salinity / organic_carbon)",
      "value": "number",
      "unit": "string",
      "method": "string"
    },
    "location": {
      "lat": "number",
      "lon": "number",
      "place_name": "string"
    },
    "timestamp": "string (ISO 8601 UTC)"
  },
  "scientific_context": {
    "context_id": "string (UUID)",
    ...
  }
}
```

### Scientific Context Variant A (Ansh's Approved Layout)
```json
{
  "context_id": "string (UUID)",
  "parameter": "string (e.g. expected_canopy_height)",
  "value": {
    "min": "number",
    "max": "number",
    "mean": "number"
  },
  "unit": "string",
  "location_polygon": {
    "type": "Polygon",
    "coordinates": [[[ "number", "number" ]]]
  },
  "temporal_validity": "string (e.g. 2020-2023)",
  "source_id": "string",
  "citation": "string",
  "verification_status": "VERIFIED | PENDING | NOT_VERIFIED | GAP",
  "confidence_score": "number (0.0 to 1.0)",
  "quality": "string",
  "uncertainty": "string"
}
```

### Scientific Context Variant B (Kaushlendra's Updated Layout)
```json
{
  "context_id": "string (UUID)",
  "observation_id": "string",
  "parameter_name": "string (e.g. expected_canopy_height)",
  "parameter_value": {
    "value": "number (mean)",
    "range": ["number (min)", "number (max)"],
    "unit": "string (m)"
  },
  "valid_from": null,
  "valid_to": null,
  "location_polygon": {
    "type": "Polygon",
    "coordinates": [[[ "number", "number" ]]]
  },
  "source_citation": "string (citation reference)",
  "source_url": null,
  "source_doi": "string (source DOI / identifier)",
  "confidence_score": "number (0.0 to 1.0)",
  "validation_status": "VERIFIED | PENDING | NOT_VERIFIED | GAP",
  "validation_evidence": "string"
}
```

---

## 2. Output Contract Payload Schema (Result Envelope)

The result envelope encapsulates all fields into distinct nested blocks conforming to Sakshi's semantic mapping layout:

### Structure Schema
```json
{
  "observation": {
    "observation_id": "string",
    "parameter": "string",
    "value": "number",
    "unit": "string",
    "timestamp": "string (ISO 8601 UTC)",
    "location": {
      "lat": "number",
      "lon": "number"
    }
  },
  "provenance": {
    "source_id": "string",
    "citation": "string",
    "verification_status": "string",
    "source_url": "string | null",
    "confidence": "number",
    "quality": "string | null",
    "uncertainty": "string | null"
  },
  "scientific_context": {
    "context_id": "string",
    "parameter_name": "string",
    "validation_status": "string"
  },
  "contextual_result": {
    "status": "string (SUCCESS | WAITING_FOR_VERIFIED_CONTEXT)",
    "parameter_evaluated": "string",
    "reference_value": "number | null",
    "deviation": "string | null",
    "anomaly_detected": "boolean | null",
    "assessment": "string | null",
    "spatial_match": "boolean",
    "temporal_match": "boolean"
  },
  "trace": {
    "trace_id": "string"
  },
  "observation_mutated": false
}
```

---

## 3. Validation & Integration Boundaries

1.  **Immutability:** The input `observation` structure must remain completely identical before and after processing.
2.  **Citation Requirement:** The context record **must** include a non-empty citation string. If the citation is missing or empty, the transaction must be rejected.
3.  **Parameter Compatibility:** The evaluated observation parameter must match the baseline context parameter (e.g., `canopy_height` must match a context parameter for expected canopy height, not salinity). If parameters mismatch, the request must be rejected.
4.  **Unit Compatibility:** Observation and context units must be identical (e.g. `m` vs `m`). If they mismatch, the request must be rejected.
5.  **Spatial Alignment:** The observation coordinates (`lat`/`lon`) must fall within the bounding box/polygon specified by `location_polygon`.
6.  **Temporal Validity:** The observation date must match the range specified in `temporal_validity`.
7.  **Missing Context Handling:** If Kaushlendra's context record is not yet available (marked as a `GAP`), the validation must explicitly report `"WAITING_FOR_VERIFIED_CONTEXT"` in the contextual result.
8.  **Verified Status Check:** If the observation is marked as `"SYNTHETIC_TEST"`, the output must preserve this status and cannot treat it as verified. Lower-confidence or gap states cannot silently become `VERIFIED`.
