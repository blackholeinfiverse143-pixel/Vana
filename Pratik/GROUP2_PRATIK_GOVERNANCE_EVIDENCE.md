# VANA Group 2 — Pratik Governance Evidence & Integration Closure

**Audit Reference Date:** 2026-08-21  
**Lead Engineer:** Pratik Bhuwad (Group 1 → Group 2 Context Generation Owner)  
**Target Observation:** `TC-Z03-F02-LIDAR-OBS001`  

---

## 1. Executive Summary
This document serves as the single authoritative index of evidence for the VANA Group 2 (Thane Creek Mangrove Ecosystem) integration. It maps the schema conversion pipeline, validates semantic and provenance constraints, verifies the ingestion of the live Group 1 Observation API, and audits the integration adapter against the authoritative Temporal Applicability rulings. 

It provides Vijay and the Governance Review Committee with concrete code references, execution results, and status verifications to prove the compliance of the integration without requiring manual inspection of individual repository source files.

---

## 2. Current Canonical Decision
The authoritative canonical decision state for the target observation **`TC-Z03-F02-LIDAR-OBS001`** is:

$$\text{GAP} \longrightarrow \text{ABSTAIN}$$

### Root Governance Fields
*   `context_status`: `"GAP"` (represented in the result status as `"WAITING_FOR_VERIFIED_CONTEXT"`)
*   `action_eligibility`: `false`
*   `abstention_required`: `true`
*   `action_request`: `null`

> [!IMPORTANT]
> The runtime pipeline forces this governed abstention path to prevent unverified context from silently promoting into active execution requests. `ALLOW` is strictly forbidden unless all authoritative validation criteria are successfully met and the external ruling is explicitly `ALLOW`.

---

## 3. Scope and Ownership
The VANA integration divides responsibilities to maintain loose coupling:
*   **Pratik (Owner):** Group 1 observation retrieval, JSON schema mapping, spatial/temporal/semantic context correlation, and validation adapter execution.
*   **Vijay / Pritesh (External):** SANSKAR core container environment, PostGIS MasterDB server hosting, and network port mappings.
*   **Mohit / Karan (External):** Group 4 Action Request broker routing and `/vana/execute` endpoint contract lifecycle.

---

## 4. Source Files / Evidence Index

| File / Artifact | Purpose | Status | Location Path |
| :--- | :--- | :--- | :--- |
| `group1_client.py` | Pulls raw canonical observation JSON from MasterDB API | **LIVE / VERIFIED** | [`05_INTEGRATION/adapter/group1_client.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/adapter/group1_client.py) |
| `group1_mapper.py` | Maps Group 1 API schema to Group 2 adapter input schema | **VERIFIED** | [`05_INTEGRATION/adapter/group1_mapper.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/adapter/group1_mapper.py) |
| `sanskar_adapter.py` | Performs context matching, temporal ruling evaluation, and constructs final envelopes | **VERIFIED** | [`05_INTEGRATION/adapter/sanskar_adapter.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/adapter/sanskar_adapter.py) |
| `scientific_context.json` | Local context fixture containing baseline canopy heights and bounding coordinates | **VERIFIED** | [`05_INTEGRATION/fixtures/scientific_context.json`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/fixtures/scientific_context.json) |
| `test_group1_integration.py` | Integration tests verifying mapping, timeouts, 404s, and GAP overrides | **VERIFIED (PASS)** | [`05_INTEGRATION/tests/test_group1_integration.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/tests/test_group1_integration.py) |
| `test_contract_validation.py` | Contract tests checking parameter matching, unit compatibility, and schema integrity | **VERIFIED (PASS)** | [`05_INTEGRATION/tests/test_contract_validation.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/tests/test_contract_validation.py) |
| `test_provenance_preservation.py` | Asserts immutability of primary input and tracks provenance field preservation | **VERIFIED (PASS)** | [`05_INTEGRATION/tests/test_provenance_preservation.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/tests/test_provenance_preservation.py) |
| `GROUP1_TO_GROUP2_RUNTIME.md` | Documents runtime API schemas, endpoints, and error handling behaviors | **VERIFIED** | [`05_INTEGRATION/GROUP1_TO_GROUP2_RUNTIME.md`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/GROUP1_TO_GROUP2_RUNTIME.md) |
| `DAY1_GROUP1_GROUP2_IMPLEMENTATION_STATUS.md` | Maps Day-1 implementation milestones and checklist verifications | **VERIFIED** | [`08_ANTIGRAVITY_ANALYSIS/DAY1_GROUP1_GROUP2_IMPLEMENTATION_STATUS.md`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/08_ANTIGRAVITY_ANALYSIS/DAY1_GROUP1_GROUP2_IMPLEMENTATION_STATUS.md) |
| `TC-Z03-F02-LIDAR-OBS001.json` | Kaushal's latest verified baseline context definition | **VERIFIED** | [`01_SOURCE_ARTIFACTS/KAUSHLENDRA/TC-Z03-F02-LIDAR-OBS001.json`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/01_SOURCE_ARTIFACTS/KAUSHLENDRA/TC-Z03-F02-LIDAR-OBS001.json) |
| `temporal_applicability_ruling.json` | Authoritative temporal decision matrix indicating observation window validity | **VERIFIED** | [`01_SOURCE_ARTIFACTS/KAUSHLENDRA/temporal_applicability_ruling.json`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/01_SOURCE_ARTIFACTS/KAUSHLENDRA/temporal_applicability_ruling.json) |

---

## 5. Group 1 → Group 2 Retrieval
Ingestion of the live API pulls the canonical record directly:
*   **Service Endpoint:** `http://163.128.209.18:8013/observations/TC-Z03-F02-LIDAR-OBS001`
*   **HTTP Retrieval:** Performed by `Group1ApiClient` using standard connection timeouts.
*   **Observed Values Ingested:**
    *   `observation_id`: `"TC-Z03-F02-LIDAR-OBS001"`
    *   `observed_at`: `"2026-08-13 09:14:22+00:00"` (Mapped to `timestamp`: `"2026-08-13T09:14:22Z"`)
    *   `geo_location`: `latitude: 19.1288`, `longitude: 72.9421` (Mapped to `location.lat`, `location.lon`)
    *   `measurements`: value `4.7`, unit `"m"`, parameter `"canopy_height"` (Mapped to flat Group 2 measurement block)

---

## 6. Group 2 Context Correlation
The mapped observation payload is evaluated against Kaushal's active scientific context fixture:
*   **Observation Target:** `TC-Z03-F02-LIDAR-OBS001`
*   **Mapped Context ID:** `ctx-tc-001`
*   **Traceability Chain:**
    $$\text{Observation ID: TC-Z03-F02-LIDAR-OBS001} \longrightarrow \text{Context ID: ctx-tc-001} \longrightarrow \text{Final Result Envelope}$$

---

## 7. Semantic & Provenance Validation
Below is the status matrix of the validation checks assigned by Aakash sir to detect data divergence:

| Divergence Check | Status | Verification Evidence / Reference |
| :--- | :--- | :--- |
| **Observation identity** | **PASS** | `sanskar_adapter.py` lines 197–200 rejects mismatched observation IDs. |
| **Group 1 canonical_record_id** | **NOT VERIFIED** | Field is not currently exposed in the active schema mappings. |
| **Group 2 context_id** | **PASS** | Unit tests verify matching to active fixture `ctx-tc-001`. |
| **device_id continuity** | **NOT VERIFIED** | The `device_id` field is present in Group 1 metadata but is bypassed by the adapter. |
| **mission_id continuity** | **NOT VERIFIED** | The `mission_id` field is present in Group 1 metadata but is bypassed by the adapter. |
| **timestamp semantic equality** | **PASS** | Normalization logic converts timezone offsets to UTC and parses years correctly for temporal bounds checks. |
| **coordinate preservation** | **PASS** | Coordinates are parsed without precision loss and checked against bounding polygon box coordinates. |
| **measurement/value/unit** | **PASS** | Checks parameter naming matches (e.g. `canopy_height`) and rejects incompatible units (e.g. `cm` vs `m`). |
| **raw_artifacts continuity** | **NOT VERIFIED** | Artifact hashes are present in Group 1 payload but are not mapped or validated by Group 2. |
| **provenance/source divergence** | **PASS** | Provenance details (`source_doi`, `citation`, `confidence_score`) are successfully validated. |
| **duplicates/idempotency** | **NOT VERIFIED** | The context resolution adapter runs as a stateless process; database constraints are TBD. |
| **missing Group 1 lineage** | **NOT VERIFIED** | Needs downstream implementation. |
| **mismatched lineage** | **NOT VERIFIED** | Needs downstream implementation. |

---

## 8. Authoritative Temporal Applicability
The adapter implements strict temporal authority validation:
*   **Ruling Artifact Path:** [`01_SOURCE_ARTIFACTS/KAUSHLENDRA/temporal_applicability_ruling.json`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/01_SOURCE_ARTIFACTS/KAUSHLENDRA/temporal_applicability_ruling.json)
*   **Ruling Evaluation:** If the ruling file contains `"ruling": "GAP"`, the adapter overrides local evaluation and forces the `GAP` decision state.
*   **Local Override Safety:** The local `2020-2028` date calculation cannot upgrade a temporal ruling of `GAP`. The adapter evaluates the ruling status *before* verifying polygon boundaries or baseline height ranges.
*   **Bypass Prevention:**
    Inside `sanskar_adapter.py` `resolve_context()`, `is_context_gap` is checked at the entry of the execution loop. If the ruling is missing or is set to `"GAP"`, the function initiates an **early return** of the GAP envelope, preventing any local calculations from producing an `ALLOW` decision.

---

## 9. Provenance / DOI Roles
The repository separates the two authoritative DOIs to protect scientific integrity:
*   **Scientific Citation DOI:** `10.1016/j.rsma.2023.103207`
    *   *Role:* Academic evidence backing Thane Creek mangrove biomass and canopy height baselines.
*   **Spatial Reference DOI:** `10.5281/zenodo.6894273`
    *   *Role:* Geographic spatial extent definitions from the Global Mangrove Watch v3.0 database.
*   **Obsolete DOI:** `10.3334/ORNLDAAC/1665` (ORNL DAAC)
    *   *Role:* Completely retired and marked as superseded. It exists only under historical metadata references inside `superseded_evidence` blocks and is never utilized in runtime evaluations.

---

## 10. Decision-Path Trace
The runtime pipeline processes observations as follows:

```
Incoming Group 1 Observation (TC-Z03-F02-LIDAR-OBS001)
                   ↓
Group1ApiClient.get_observation() retrieves payload
                   ↓
map_group1_to_group2() normalizes schema and timestamps
                   ↓
SanskarContextAdapter.resolve_context(payload, temporal_ruling)
                   ↓
Reads temporal_applicability_ruling.json
                   ↓
  [ruling is GAP or Missing?]
         ├── Yes ──> Exits early, returns WAITING_FOR_VERIFIED_CONTEXT (GAP)
         └── No  ──> Performs spatial bounding box & height baseline validation
                   ↓
Generates Envelope (Injects action_eligibility, abstention_required, and action_request)
```

---

## 11. Governance Output Contract
When the pipeline detects a `GAP` status, the resolved envelope enforces these values:

```json
{
  "contextual_result": {
    "status": "WAITING_FOR_VERIFIED_CONTEXT",
    "action_eligibility": false,
    "abstention_required": true
  },
  "action_request": null,
  "action_eligibility": false,
  "abstention_required": true
}
```

---

## 12. Test Evidence
*   **Total Tests Run:** 38
*   **Total Tests Passed:** 38
*   **Test Suite Entry:** `python -m unittest discover -s 05_INTEGRATION/tests`

### Essential Test Cases

| Test Case Name | Target File | Purpose / Verification Objective |
| :--- | :--- | :--- |
| `test_authoritative_gap_overrides_local_validation` | `test_group1_integration.py` | Proves that a `GAP` temporal ruling overrides local range validations and forces an abstention envelope. |
| `test_no_authoritative_ruling_defaults_to_gap` | `test_group1_integration.py` | Ensures that omitting the temporal ruling defaults the adapter to a `GAP` block. |
| `test_two_doi_role_separation_and_rejection` | `test_group1_integration.py` | Asserts that spatial DOIs cannot be substituted for scientific context. |
| `test_provenance_and_immutability` | `test_provenance_preservation.py` | Verifies that the adapter execution does not mutate incoming observation structures. |
| `test_parameter_mismatch_rejection` | `test_contract_validation.py` | Validates that mismatched observation metrics (e.g. soil pH) are rejected with a ValueError. |

---

## 13. Live / Local / Shared / Blocked Status

| Subsystem Component | Environment Status | Notes |
| :--- | :--- | :--- |
| **Group 1 Observation API** | **LIVE / VERIFIED** | Pulls observation payloads from the remote Postgres/PostGIS instance. |
| **Group 2 Ingestion Client** | **LIVE / VERIFIED** | Network requests to the Group 1 API successfully execute and parse. |
| **Group 2 Context Adapter** | **LOCAL** | Execution runs successfully inside the local Python runtime environment. |
| **SANSKAR core system** | **BLOCKED / OFFLINE** | Port mappings and agricultural core bindings remain unmapped. |
| **Group 4 Broker Integration** | **BLOCKED / OFFLINE** | Downstream `/vana/execute` routing remains unintegrated. |

---

## 14. External Blockers
1.  **Group 4 Integration:** Mohit / Karan have not exposed the E2E Action Request receiver.
2.  **Infrastructure Bindings:** Dev server subnet port mappings (`8001:8000`) for the Postgres MasterDB are unrouted.

---

## 15. Known Gaps / TBD
*   **Divergence Checks:** Validation of `device_id`, `mission_id`, and `raw_artifacts` metadata are not yet mapped or asserted inside the adapter.
*   **Idempotency & Auditing:** The context generation client is stateless and does not record prior transactions in an audit ledger.

---

## 16. Governance Readiness Verdict

$$\text{Verdict:} \quad \mathbf{\text{NOT VERIFIED}}$$

> [!CAUTION]
> While the temporal ruling injection and local validation logic are fully implemented and passing all 38 test assertions, E2E live contract validation remains **NOT VERIFIED** due to missing `device_id`/`mission_id` divergence checks and the offline status of the SANSKAR core engine.

---

## 17. Handover Instructions
Vijay can consume this file as the primary audit document.
*   All tests are defined in: [`05_INTEGRATION/tests/`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/tests/)
*   The adapter orchestrator is defined in: [`05_INTEGRATION/adapter/sanskar_adapter.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/adapter/sanskar_adapter.py)
*   The raw mapping rules are stored in: [`05_INTEGRATION/adapter/group1_mapper.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/adapter/group1_mapper.py)
