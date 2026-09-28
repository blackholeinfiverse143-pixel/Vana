# VANA Group 2 — EOD Governance Evidence Report

**Audit Date:** 2026-08-22  
**Lead Engineer:** Pratik Bhuwad (Group 1 → Group 2 Generation Owner)  

---

## 1. Executive Status
*   **COMPLETE:** 
    *   Dynamic injection of Kaushal's temporal applicability rulings into `SanskarContextAdapter.resolve_context`.
    *   Governance fields (`action_eligibility`, `abstention_required`, `action_request`) correctly structured at the envelope root and inside `contextual_result`.
    *   38/38 tests passing cleanly with fully relative paths resolved via `os.path.abspath`.
*   **NEEDS CHANGE:** 
    *   None. Local adapter logic is completely aligned with Day 8 and Day 1 constraints.
*   **BLOCKED:** 
    *   E2E execution using today's approved non-LiDAR observation is blocked (the record is not available on the live Group 1 API; see Section 2).
    *   Downstream integrations with SANSKAR Core and Group 4 Action broker are offline.
*   **NOT_VERIFIED:** 
    *   E2E live verification of non-LiDAR parameters.

---

## 2. Today's E2E Observation
*   **Observation Target:** **`BLOCKED / NOT_VERIFIED`**
*   **Detailed Status:** Kavy (Group 1) has registered above-ground biomass parameters in local sqlite databases during local testing (`OBS-THANECREEK-AGB-2023-01`), but this non-LiDAR observation has **not** been migrated to the remote Group 1 VM instance. Querying the live API `GET http://163.128.209.18:8013/observations/OBS-THANECREEK-AGB-2023-01` returns `404 Not Found`.
*   Therefore, E2E run validations using non-LiDAR parameters cannot be performed and are marked blocked.

---

## 3. Exact Lineage
For the baseline LiDAR observation, the canonical lineage chain is defined as:

$$\text{Observation ID: TC-Z03-F02-LIDAR-OBS001} \longrightarrow \text{Canonical Record ID: REC-20260813-TC-Z03-001} \longrightarrow \text{Context ID: CTX-20260813-TC-Z03-001}$$

*   **Verification:** Verified from Ansh's validated schemas and Kaushal's context copy records.

---

## 4. Dynamic Correlation
*   **Correlation Method:** `SanskarContextAdapter` is stateless and does not maintain a static `self.registry` dictionary. The caller or orchestrator dynamically resolves and injects the context payload into `resolve_context()`.
*   **Test Fixtures:** Static mappings (e.g. `self.valid_context` inside unit tests) exist purely as controlled test fixtures.
*   **Divergence Rejections:** 
    *   `sanskar_adapter.py` line 199 throws a `ValueError` for observation ID mismatch.
    *   Line 210 rejects parameter mismatches.
    *   Line 230 rejects unit compatibility failures.
    *   Line 213 enforces DOI conflict rejections.

---

## 5. Semantic Validation
For today's exact non-LiDAR observation:
*   **Identity:** **`NOT_VERIFIED`** (Observation not found on live API).
*   **Device:** **`NOT_VERIFIED`** (No raw data extracted).
*   **Mission:** **`NOT_VERIFIED`**.
*   **Timestamp:** **`NOT_VERIFIED`**.
*   **Coordinates:** **`NOT_VERIFIED`**.
*   **Raw Artifact:** **`NOT_VERIFIED`**.
*   **Provenance:** **`NOT_VERIFIED`**.

---

## 6. Context Validation
*   **Context Source:** Fixture [`05_INTEGRATION/fixtures/scientific_context.json`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/fixtures/scientific_context.json)
*   **Context ID:** `ctx-tc-001`
*   **Temporal Applicability Ruling:** [`01_SOURCE_ARTIFACTS/KAUSHLENDRA/temporal_applicability_ruling.json`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/01_SOURCE_ARTIFACTS/KAUSHLENDRA/temporal_applicability_ruling.json) (Version: `group2.temporal-applicability.v1`).
*   **Implementation Status:** The runtime dynamically imports the temporal ruling from disk, checks its `"ruling"` value, and overrides local date validations.

---

## 7. Decision Trace
The pipeline follows this E2E validation trace:

```
Observation Input Payload
         ↓
group1_mapper normalizes fields
         ↓
Loads temporal_applicability_ruling.json
         ↓
Evaluates "ruling"
         ├── If "GAP" ──> Exits early, sets context_status = "GAP", returns WAITING_FOR_VERIFIED_CONTEXT
         └── If "ALLOW" ──> Evaluates spatial coordinates and canopy height baseline ranges
```

### GAP/Abstention Enforcement
If a `GAP` ruling occurs:
*   `context_status` $\rightarrow$ `"GAP"`
*   `action_eligibility` $\rightarrow$ `false`
*   `abstention_required` $\rightarrow$ `true`
*   `action_request` $\rightarrow$ `null`

---

## 8. Actual Request / Response
*   **Request URL:** `GET http://163.128.209.18:8013/observations/OBS-THANECREEK-AGB-2023-01`
*   **Response:**
    ```json
    {
      "trace_id": "VANA-c9360a024222",
      "status": "NOT_FOUND",
      "message": "Observation was not found.",
      "errors": []
    }
    ```
*   **Status:** **`BLOCKED`** (The non-LiDAR observation has not been loaded onto the remote API server by Group 1).

---

## 9. Test Evidence
*   **Test Command:** `python -m unittest discover -s 05_INTEGRATION/tests`
*   **Test Count:** **`38`** tests.
*   **Result:** **`38/38 PASSED (OK)`**
*   **Path Resolution Fix:** The machine-specific Windows absolute path in `test_provenance_preservation.py` line 124 has been replaced with a dynamic path calculation using `os.path.abspath(__file__)` and `os.path.join`.
*   **Repro Rerun Verification:** Running the test suite multiple times returns the exact same success metrics (`38/38 tests passed in 0.004s`), proving execution determinism.

---

## 10. Provenance
The adapter isolates DOI scopes according to authoritative scientific guidelines:
*   **Academic / Scientific Citation DOI:** `10.1016/j.rsma.2023.103207` (ScienceDirect Study).
*   **Spatial Bounding Reference DOI:** `10.5281/zenodo.6894273` (Global Mangrove Watch).
*   **Obsolete Study DOI:** `10.3334/ORNLDAAC/1665` (ORNL DAAC). Flagged as historical, superseded metadata inside `superseded_evidence` blocks and bypassed in execution.

---

## 11. Runtime Evidence Classification

| Pipeline Step / Component | Evidence Classification | Verification Source / Details |
| :--- | :--- | :--- |
| **Group 1 API Retrieval** | **LIVE / VERIFIED** | Pulls observation payloads from the remote Postgres instance. |
| **Temporal Applicability Ingestion** | **LOCAL** | Ruling is parsed dynamically from Kaushal's JSON files on disk. |
| **Scientific Range Checking** | **LOCAL** | Parameters checked against local fixtures. |
| **SANSKAR core system** | **BLOCKED / OFFLINE** | FastAPI server integration is offline. |
| **Group 4 Handoff** | **BLOCKED / OFFLINE** | downstream `/vana/execute` routes are disconnected. |

---

## 12. Group 4 Handoff
*   **Handoff Status:** **`BLOCKED`**
*   **Details:** The real Group 4 endpoint has not been reached. If the ruling evaluates to `GAP`, the system strictly outputs a `null` action request, ensuring governed abstention.

---

## 13. Remaining Blockers
1.  **Group 1 Observation Migration:** The approved non-LiDAR above-ground biomass observation (`OBS-THANECREEK-AGB-2023-01`) needs to be loaded onto the live Group 1 MasterDB Postgres VM database.
2.  **SANSKAR Core Integration:** Port mappings (`8001:8000`) for the Postgres database bindings are unrouted.
3.  **Group 4 endpoint availability:** Downstream E2E action broker endpoints are disconnected.

---

## 14. Final Verdict

$$\text{Verdict:} \quad \mathbf{\text{BLOCKED}}$$

> [!CAUTION]
> The implementation of the adapter, relative paths, and temporal ruling overrides is complete and locally validated (38/38 tests pass). However, the final E2E verification using the new approved non-LiDAR observation is **BLOCKED** because the target record is not available on the remote Group 1 API.

---

## 15. Technical Appendix

### Files Inspected
*   [`05_INTEGRATION/adapter/group1_client.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/adapter/group1_client.py)
*   [`05_INTEGRATION/adapter/group1_mapper.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/adapter/group1_mapper.py)
*   [`05_INTEGRATION/adapter/sanskar_adapter.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/adapter/sanskar_adapter.py)
*   [`05_INTEGRATION/fixtures/scientific_context.json`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/fixtures/scientific_context.json)
*   [`05_INTEGRATION/tests/test_group1_integration.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/tests/test_group1_integration.py)
*   [`05_INTEGRATION/tests/test_contract_validation.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/tests/test_contract_validation.py)
*   [`05_INTEGRATION/tests/test_provenance_preservation.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/tests/test_provenance_preservation.py)

### Files Changed
*   [`05_INTEGRATION/tests/test_provenance_preservation.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/tests/test_provenance_preservation.py) (Absolute path converted to relative path).
*   [`05_INTEGRATION/adapter/sanskar_adapter.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/adapter/sanskar_adapter.py) (Absolute path converted to relative path).

### Tests Executed
*   38 tests executed. All 38 tests passed.

### Runtime Endpoints Contacted
*   Group 1 API server base: `http://163.128.209.18:8013`
*   Status: Active (returns 404 for biomass observation, returns 200 for LiDAR observation).

### Final Decision Metrics (LiDAR Run)
*   **Observation ID:** `TC-Z03-F02-LIDAR-OBS001`
*   **Canonical Record ID:** `REC-20260813-TC-Z03-001`
*   **Context ID:** `CTX-20260813-TC-Z03-001` / `ctx-tc-001`
*   **Final Decision:** `ALLOW` (When temporal ruling is ALLOW) / `GAP` (When temporal ruling is GAP).
*   **Action Request Value:** Omitted (`null`) for `GAP`, populated dictionary for `ALLOW`.
