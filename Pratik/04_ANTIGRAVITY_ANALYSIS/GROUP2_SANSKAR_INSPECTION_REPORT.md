# SANSKAR Runtime & Contract Inspection Report

**Role:** Group 2 Integration and Verification Engineer  
**Sprint:** VANA / PRAKRITI 1 KM Sprint — SANSKAR Integration  
**Date:** 14 August 2026  
**Final Status:** **READY TO IMPLEMENT** (No modification of existing SANSKAR core files required; integration is achievable entirely through a lightweight translation adapter).

---

## 1. Current Architecture

The existing SANSKAR runtime is a containerized Python service structured as follows:
*   **Web Framework:** FastAPI (defined in [`api.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/02_SANSKAR/Sanskar-Integration-main/api.py)), managed locally via Uvicorn.
*   **Pipeline Logic:** SANSKAR operates as a deterministic multi-stage execution chain:
    1.  **SANSKAR Engine ([`sanskar.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/02_SANSKAR/Sanskar-Integration-main/sanskar.py)):** Loads CSV dataset paths, performs feature generation, aggregates region metrics, computes composite scores, ranks candidates, simulates scenarios, and applies adaptive intelligence refinements.
    2.  **Core Decision Engine ([`core.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/02_SANSKAR/Sanskar-Integration-main/core.py)):** Evaluates rankings and maps scores to priority levels (Critical, High, Medium, Low).
    3.  **Enforcement Engine ([`enforcement.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/02_SANSKAR/Sanskar-Integration-main/enforcement.py)):** Translates decisions into operational directives and sets up external execution context checks.
    4.  **Causality & Integrity Tracker ([`tantra.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/02_SANSKAR/Sanskar-Integration-main/tantra.py) & [`canonical_serialization.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/02_SANSKAR/Sanskar-Integration-main/canonical_serialization.py)):** Performs trace continuity validation and computes SHA-256 hashes over the complete pipeline data domain to lock it for replay.
*   **Persistence & Observability:** Logs execution statuses locally to `observability.log` and appends completed hashes/verdicts to `truth_store.json`.
*   **Infrastructure:** Run is containerized via a lightweight [`Dockerfile`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/02_SANSKAR/Sanskar-Integration-main/Dockerfile) (using `python:3.11-slim`) and managed via [`docker-compose.yml`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/02_SANSKAR/Sanskar-Integration-main/docker-compose.yml).

---

## 2. Existing SANSKAR Input Contract

FastAPI exposes the `/signal` endpoint which expects a JSON payload matching the `SignalInput` Pydantic model:

*   **Request JSON Schema:**
    ```json
    {
      "trace_id": "string",
      "signal": {
        "dataset": "string"
      },
      "contract_version": "string (optional, default: 'v1')"
    }
    ```
*   **Required Fields:** `trace_id` (must be non-empty), `signal` (dictionary), and `signal.dataset` (must be a valid path to an agricultural crop yield CSV file).
*   **CSV Schema Requirements:** The file target of the `dataset` parameter **must** contain these exact headers:
    *   `Region` (String) — Represents the geographic candidate entity.
    *   `Rainfall_mm` (Float) — Used to compute `rainfall_score`.
    *   `Temperature_Celsius` (Float) — Used to compute `temp_score`.
    *   `Irrigation_Used` (Boolean/String: "True"/"False") — Used to compute `irrigation_score`.
    *   `Fertilizer_Used` (Boolean/String: "True"/"False") — Used to compute `fertilizer_score`.
    *   `Soil_Type` (String: "Loam", "Silt", "Clay", "Peaty", "Sandy", "Chalky") — Used to compute `soil_quality_score`.
    *   `Weather_Condition` (String: "Sunny", "Cloudy", "Rainy") — Used to compute `weather_score`.
    *   `Yield_tons_per_hectare` (Float) & `Days_to_Harvest` (Float) — Used to compute `yield_efficiency_score`.

---

## 3. Existing SANSKAR Output Contract

SANSKAR returns a structured JSON payload representing the trace history.

*   **Response Payload Structure:**
    ```json
    {
      "trace_id": "string",
      "pipeline_status": "SUCCESS",
      "input": { ... }, 
      "sanskar_output": {
        "trace_id": "string",
        "stage": "sanskar",
        "entities": [
          {
            "entity_id": "string",
            "score": "float (rounded)",
            "raw_score": "float (raw)",
            "tie_breaker": "float",
            "factors": [ ... ],
            "confidence": "float",
            "confidence_factors": { ... },
            "explanation": "string",
            "decision_state": "CONFIDENT/AMBIGUOUS/LOW_CONFIDENCE",
            "adaptive_refinement": { ... }
          }
        ],
        "ranking": ["string"],
        "comparative_explanation": { ... },
        "scenario_analysis": [ ... ],
        "downstream_decision": { ... },
        "contract_version": "v1"
      },
      "core_decision": { ... },
      "enforcement": { ... },
      "truth": {
        "verdict": "PIPELINE_COMPLETE",
        "selected_entity": "string",
        "selected_score": "float",
        "enforcement_action": "string",
        "enforcement_target": "string",
        "pipeline_hash": "string (sha256)",
        "chain_integrity": "string",
        "trace_continuity": "string",
        "trace_continuity_proof": { ... },
        "stages_completed": ["input", "sanskar", "core", "enforcement", "truth"],
        "contract_version": "v1",
        "hash_input": { ... }
      }
    }
    ```

---

## 4. Group 1 Observation Contract

As documented in [`schema.sql`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/01_SOURCE_ARTIFACTS/ANSH/schema.sql), Group 1's canonical relational database represents observations using normalization:
*   `observation`: `observation_id` (PK, TEXT), `dataset_id` (FK, TEXT), `geo_id` (FK, TEXT), `observation_date` (DATE), `species` (TEXT), `observation_type` (TEXT), `confidence` (TEXT).
*   `measurement`: `measurement_id` (PK, TEXT), `observation_id` (FK, TEXT), `metric_name` (TEXT), `value` (NUMERIC), `unit` (TEXT), `method` (TEXT), `original_value_text` (TEXT), `transform_applied` (TEXT).
*   `geography`: `geo_id` (PK, TEXT), `place_name` (TEXT), `lat`/`lon` (REAL coordinates), `crs` (TEXT), `notes` (TEXT).

### Real Observation Fixture
From the newly verified sewage/biodiversity paper ([`Scientific_Source_Registry_V0.1_FINAL_VERIFIED.xlsx`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/01_SOURCE_ARTIFACTS/SAKSHI/Scientific_Source_Registry_V0.1_FINAL_VERIFIED.xlsx) - sheet `2016 Paper Extraction`):
*   **Observation Source ID:** `TCM-LIT-WQ-2016-001` (Pachpande & Pejaver, 2016)
*   **Station I Observation:** Western bank, adjacent to Bhandup Pumping Station (19.1398° N, 72.9574° E).
    *   *Organic Carbon:* `2.85%` (original value text: `"2.85"`)
    *   *Sediment pH:* `7.48`
    *   *Chlorides:* `0.75%`
    *   *Polychaeta Density:* `1860 no./m²`
    *   *Gastropoda Density:* `2188.8 no./m²`
*   **Station II Observation:** Less disturbed creek station (19.1446° N, 72.9722° E).
    *   *Organic Carbon:* `1.98%`
    *   *Sediment pH:* `7.47`
    *   *Chlorides:* `0.95%`
    *   *Polychaeta Density:* `52.2 no./m²`
    *   *Gastropoda Density:* `4748.8 no./m²`

---

## 5. Scientific Context Contract

From Kaushlendra's context model ([`SCIENCE_CONTEXT_MODEL.md`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/01_SOURCE_ARTIFACTS/KAUSHLENDRA/SCIENCE_CONTEXT_MODEL.md)), scientific baseline conditions are structured as `ScientificContextRecord` profiles:

```json
{
  "context_id": "ctx-9876-abcd-1234",
  "parameter_name": "baseline_salinity",
  "parameter_value": {
    "min": 15.0,
    "max": 35.0,
    "mean": 28.5
  },
  "unit": "ppt",
  "temporal_validity": "2020-2023",
  "location_polygon": {
    "type": "Polygon",
    "coordinates": [[[72.95, 19.10], [72.98, 19.10], [72.98, 19.15], [72.95, 19.15], [72.95, 19.10]]]
  },
  "source_citation": "Thane Creek Environmental Assessment Report, MMRDA, 2023.",
  "source_url_doi": "https://mmrda.maharashtra.gov.in/reports/tc-2023",
  "confidence_score": 0.85,
  "validation_status": "VERIFIED"
}
```

---

## 6. Observation $\rightarrow$ Context $\rightarrow$ SANSKAR Mapping

To run observations through the **existing** SANSKAR scoring engine without mutating python files, we map Thane Creek benthos parameters to the agricultural input headers, writing the result to a temporary CSV payload.

### Parameter Translation Mapping

| SANSKAR Header | Thane Creek Benthos parameter | Mapping Translation Logic |
| :--- | :--- | :--- |
| **`Region`** | Station Name | `Station I` / `Station II` |
| **`Rainfall_mm`** | Chlorides (%) | Chloride value scaled (e.g. `0.75%` $\rightarrow$ `75.0` ; `0.95%` $\rightarrow$ `95.0`) |
| **`Temperature_Celsius`**| Sediment pH | Raw sediment pH (e.g., `7.48` $\rightarrow$ `7.48`) |
| **`Irrigation_Used`** | Wastewater Exposure | `True` (continuous wastewater inflow) / `False` (undisturbed) |
| **`Fertilizer_Used`** | Nutrient Accumulation | `True` (sewage discharge) / `False` (clean station) |
| **`Soil_Type`** | Substrate Texture Class | Maps sand/silt/clay dominance to closest SANSKAR class (e.g., `Silt` $\rightarrow$ `Silt`, `Clay` $\rightarrow$ `Clay`) |
| **`Weather_Condition`** | Temporal Seasonality | Mapped from observation period (e.g., September $\rightarrow$ `Rainy`, April $\rightarrow$ `Sunny`) |
| **`Yield_tons_per_hectare`**| Sediment Organic Carbon (%)| Direct map of organic carbon percentages (e.g., `2.85%` $\rightarrow$ `2.85`) |
| **`Days_to_Harvest`** | Study Duration | Direct study duration in months (e.g., `18` months $\rightarrow$ `18`) |

---

## 7. Existing Endpoints

Verifying SANSKAR's [`api.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/02_SANSKAR/Sanskar-Integration-main/api.py), the active routes are:
1.  **`GET /health`** $\rightarrow$ Health status check.
2.  **`POST /signal`** $\rightarrow$ Main intake pipeline.
3.  **`POST /replay`** $\rightarrow$ Replay verification, checking the hash continuity.
4.  **`GET /trace/{trace_id}`** $\rightarrow$ Query in-memory trace map.
5.  **`GET /ranking`** $\rightarrow$ Returns the latest ranking array and entity outputs.

*Note: The intermediate endpoints `/context/resolve` and `/sanskar/signal` proposed by Pritesh do not exist in the SANSKAR codebase. They must be handled by a translation adapter.*

---

## 8. Runtime / Docker Dependencies

*   **Port Mapping:** Exposed on container port **8000** (mapped `8000:8000` in host).
*   **Networking:** Default bridge network (runs isolated, cannot be resolved dynamically by other containers without custom networks).
*   **Environment Mismatch:** SANSKAR runs internally on port `8000`, but Pritesh's runtime integration document configures `SANSKAR_SERVICE_URL` as `http://localhost:8001`. This creates a port conflict.
*   **Volume Mounts:** Mounts local host paths `./truth_store.json` and `./observability.log` into `/app` path of the container.

---

## 9. MasterDB Status

There is **no live network connection** configured for a production PostgreSQL instance in the workspace. All database queries run against local stand-in SQLite databases (`vana_demo_corrected.db` / `vana_demo.db`).

---

## 10. Existing Components We Can Reuse

*   The Pydantic inputs and FastAPI app architecture in `api.py`.
*   The scoring engine, adaptive refinements, and scenario simulations in `sanskar.py`.
*   The complete trace security and verification routines in `tantra.py` and `canonical_serialization.py`.
*   The verified scientific observations for the 2016 sewage paper in Sakshi's verified sheet.
*   The `ScientificContextRecord` model defined in Kaushlendra's context model.

---

## 11. Actual Gaps

1.  **JSON-to-CSV Translation Adapter:** Missing a module to fetch JSON observations + context records, translate parameters using the mapping table, write a temporary CSV file, and call `POST /signal`.
2.  **Port Alignment:** Conflict between SANSKAR's port `8000` and the configured port `8001` in the VANA runtime.
3.  **Docker Networking:** SANSKAR's compose file does not attach the container to the shared VANA bridge network, preventing container-to-container calls.
4.  **Mock Context Service:** Missing an API endpoint to map observation IDs to corresponding scientific context polygons and DOIs.

---

## 12. Exact Files That Must Change

1.  **`02_SANSKAR/Sanskar-Integration-main/docker-compose.yml`:**
    *   Expose port `8000` and link to the shared `vana-net` network.
2.  **`02_SANSKAR/Sanskar-Integration-main/.env.example`:**
    *   Add variables `SANSKAR_SERVICE_URL=http://sanskar:8000` and `VANA_NETWORK=vana-net`.
3.  **Create `02_SANSKAR/Sanskar-Integration-main/adapter_layer/sanskar_adapter.py`:**
    *   A new python adapter carrying out the translation mapping.

---

## 13. Proposed Minimal Implementation Plan

1.  **Network Setup:** Add a common bridge network `vana-net` in SANSKAR's `docker-compose.yml` to allow the Node.js / Python VANA node to resolve the `sanskar` host.
2.  **Adapter Design:** Implement `sanskar_adapter.py` inside SANSKAR's `adapter_layer`. This adapter will:
    *   Accept structured JSON payloads (Observation + Context).
    *   Transform observations from Station I and Station II into SANSKAR's agricultural CSV format.
    *   Write the data to a temporary file in SANSKAR's runtime directory.
    *   Pass the temporary CSV path to the `/signal` endpoint.
3.  **Verify Flow:** Launch the container and run a curl request against `/signal` to verify that the benthos metrics are successfully scored and logged in the trace registry.

---

## 14. One E2E Test Plan

### Test Target: Verify Thane Creek Benthos Contextualisation
1.  **Pre-requisite:** SANSKAR container is active on port 8000.
2.  **Step 1:** The adapter transforms Station I and Station II metrics from paper `TCM-LIT-WQ-2016-001` into a temporary CSV file `temp_tc_benthos.csv` with agricultural headers.
3.  **Step 2:** Send a POST request to `http://localhost:8000/signal` with payload:
    ```json
    {
      "trace_id": "TCM-LIT-WQ-2016-001-TRACE-001",
      "signal": {
        "dataset": "temp_tc_benthos.csv",
        "observation_id": "TCM-LIT-WQ-2016-001",
        "citation": "Pachpande, S. & Pejaver, M. (2016)",
        "original_confidence": "HIGH"
      },
      "contract_version": "v1"
    }
    ```
4.  **Step 3 (Assertion):** Verify the HTTP status code is 200 and `"pipeline_status"` is `"SUCCESS"`.
5.  **Step 4 (Assertion):** Verify that `"sanskar_output.ranking"` lists `["Station I", "Station II"]` or vice versa, demonstrating that the benthos observations are successfully processed and ranked by SANSKAR.
6.  **Step 5 (Assertion):** Verify that a row is successfully appended to `truth_store.json` containing the computed trace ID hash.
7.  **Step 6 (Assertion):** Send a POST request to `/replay` with `{ "trace_id": "TCM-LIT-WQ-2016-001-TRACE-001" }` and assert that SANSKAR returns status `SUCCESS` and matches the original pipeline hash, proving deterministic replay verification.
