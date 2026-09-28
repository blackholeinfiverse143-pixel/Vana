# VANA Group 1 → Group 2 Runtime Integration Documentation

This document describes the runtime execution details of the Group 1 VANA MasterDB API integration with the Group 2 SANSKAR contextualisation adapter.

---

## 1. Group 1 LIVE API & Capability
*   **Service Name:** VANA MasterDB Observation API
*   **Capability ID:** `group1-observation-api`
*   **Base URL:** `http://163.128.209.18:8013`
*   **Endpoints:**
    *   `GET /health`: Health verification check.
    *   `GET /observations/{observation_id}`: Canonical observation retrieval.
    *   `POST /observations`: Observation insertion.
*   **Target Canonical Observation:** `TC-Z03-F02-LIDAR-OBS001`
*   **Target Coordinate Bounding Polygon:** Longitude `72.93` to `73.02`, Latitude `19.00` to `19.15`.
*   **Runtime Base:** PostgreSQL 16 + PostGIS 3.4

---

## 2. API Schema Discrepancy & Mapping Rules

### Group 1 JSON Schema (Incoming payload)
```json
{
  "trace_id": "VANA-xxxxxxxxxxxx",
  "observation_id": "string",
  "status": "string",
  "observation": {
    "observation_id": "string",
    "observed_at": "string (YYYY-MM-DD HH:MM:SS+00:00)",
    "geo_location": {
      "latitude": 19.1288,
      "longitude": 72.9421,
      "place_name": "string"
    },
    "measurements": [
      {
        "metric_name": "string",
        "value": 4.7,
        "unit": "string",
        "method": "string"
      }
    ],
    "is_synthetic": false
  }
}
```

### Group 2 JSON Schema (Expected adapter input)
```json
{
  "trace_id": "string (matches (TRACE|VANA)-[a-zA-Z0-9]{12})",
  "observation": {
    "observation_id": "string",
    "status": "SYNTHETIC_TEST | VERIFIED",
    "measurement": {
      "parameter": "string",
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
  }
}
```

### Schema Mapping Translation Rules
1.  **Trace ID:** `trace_id` is copied.
2.  **Observation ID:** `observation.observation_id` is copied.
3.  **Timestamp:** Normalizes `observation.observed_at` by replacing space characters with `"T"` and timezone offsets with `"Z"` (e.g. `"2026-08-13 09:14:22+00:00"` $\rightarrow$ `"2026-08-13T09:14:22Z"`).
4.  **Coordinates:** Maps `latitude`/`longitude` inside `geo_location` to `lat`/`lon` inside `location`.
5.  **Measurement:** Flattens the first item of `measurements` list into `measurement` object, copying metric names, values, units, and methods.
6.  **Validation Status:** Maps boolean `is_synthetic` to status string: `is_synthetic == True` $\rightarrow$ `"SYNTHETIC_TEST"`, `is_synthetic == False` $\rightarrow$ `"VERIFIED"`.

---

## 3. Execution Pipeline & Error Handling
Orchestration is handled by `fetch_and_generate_context` inside [`sanskar_adapter.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/adapter/sanskar_adapter.py):

```
LIVE GROUP 1 API
        ↓
Group1ApiClient.get_observation(obs_id) -> Handles HTTP 404, Connection timeouts, malformed JSON
        ↓
map_group1_to_group2(payload) -> Validates structural presence, normalized coordinates, and measurements
        ↓
SanskarContextAdapter.resolve_context(payload) -> Performs parameter bounds checking, spatial/temporal validity
        ↓
Contextual envelope result
```

---

## 4. Integrity and Scientific Safety Rules

### GAP-to-Abstention Constraint
If the resolved validation status is `GAP` (meaning no verified scientific context baseline is registered for that coordinate or parameter), the adapter forces a governed abstention state:
*   The output envelope's `action_request` key is set to `None` (omitted in downstream execution).
*   No baseline canopy height ranges or references are fabricated.
*   This prevents unverified data from silently transforming into executable directives.

### Trace ID Compatibility
Trace ID validation has been updated to accept both standard trace ID formats:
*   `TRACE-[a-zA-Z0-9]{12}` (legacy format)
*   `VANA-[a-zA-Z0-9]{12}` (live API format)

### DOI Role Separation
To guarantee provenance, DOIs must never be mixed or collapsed:
*   **ACADEMIC SCIENCE CLAIM:** `10.1016/j.rsma.2023.103207` (ScienceDirect baseline)
*   **SPATIAL BOUNDARY METADATA:** `10.5281/zenodo.6894273` (Global Mangrove Watch extent)
*   Any attempt to map the spatial dataset DOI to the canopy height baseline attributes raises a validation `ValueError`.

---

## 5. Test Results Summary
*   **Tests Run:** 36
*   **Passed:** 36
*   **Failed:** 0
*   **Coverage:** Includes client mocks (404, malformed, connection timeout), mapper validations, trace pattern assertions, GAP safety checks, and spatial/temporal bounds checks.

---

## 6. Live Verification Results
Executing `run_final_validation.py` targeting the live Group 1 API yields:
*   **Endpoint queried:** `http://163.128.209.18:8013/observations/TC-Z03-F02-LIDAR-OBS001`
*   **Parsed values:** Observation `TC-Z03-F02-LIDAR-OBS001`, timestamp `2026-08-13T09:14:22Z`, location `19.1288, 72.9421`, measurements value `4.7` and unit `"m"`.
*   **Evaluation Status:** `SUCCESS`
*   **Context status:** `ALLOW` (observation is within baseline range `3.5 m - 6.5 m` and passes bounding checks).
*   **Action Request:** Formulated successfully with deterministic ID `req-2ba74c5c-1ed3-5696-9e9d-39a89ffd9780`.

---

## 7. Runtime Classification
*   **Group 1 MasterDB Observation API:** **LIVE / VERIFIED** (Pulls from active PostgreSQL 16 server).
*   **Group 2 Validation Adapter:** **LOCAL** (Resolves evaluations using local baseline rules and checks).
*   **SANSKAR Core Engine:** **OFFLINE / BLOCKED** (FastAPI and Postgres MasterDB are unmapped and disconnected).
