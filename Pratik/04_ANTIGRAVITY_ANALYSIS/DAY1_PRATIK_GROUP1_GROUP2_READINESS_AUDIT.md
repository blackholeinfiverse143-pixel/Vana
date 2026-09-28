# VANA Group 2 — Day 1 of 2: Group 1 → Group 2 Readiness & Implementation Audit

## 1. Executive Summary
This report presents a readiness and implementation audit for the integration of the live Group 1 VANA MasterDB API with the Group 2 SANSKAR validation adapter. 

Our audit confirms that the Group 1 MasterDB API is now **LIVE / VERIFIED** at `http://163.128.209.18:8013`, and we have successfully retrieved the canonical observation `TC-Z03-F02-LIDAR-OBS001` directly from the live boundary. However, the Group 1 response schema is structurally incompatible with our current Group 2 input contract. Additionally, a critical defect has been identified in our Day-8 adapter: it outputs an `action_request` payload even for `GAP` scientific contexts, violating Sakshi's new GAP-to-abstention safety rule. 

Pratik must implement a retrieval client and translation mapper to bridge the API boundary, and update the adapter to omit Action Requests for GAP contexts, while awaiting Group 4's final runtime endpoint registration.

---

## 2. Previous Day-8 Status
*   **Adapter:** Resolved context and mapped payload locally based on mock dictionary inputs.
*   **Action Request:** Implemented a mock Action Request generator producing a payload format including `context_status` and `requested_action` of `ALLOW`, `ADAPT`, or `GAP`.
*   **Test Status:** 16/16 unit tests passing successfully using a local synthetic fixture.
*   **Runtime status:** Classified as **LOCAL** since both Group 1 and SANSKAR were mocked or offline.

---

## 3. New Group 1 LIVE Status
*   **API Base URL:** `http://163.128.209.18:8013`
*   **Status:** **LIVE / VERIFIED**
*   **Endpoints:**
    *   `GET /health`: Returns healthy status (`"status": "healthy"`, `"service": "VANA MasterDB Observation API"`).
    *   `GET /observations/{observation_id}`: Resolves observation metadata.
*   **Postgres Version:** PostgreSQL 16 + PostGIS 3.4

---

## 4. Canonical Observation Verification
Direct HTTP retrieval of `TC-Z03-F02-LIDAR-OBS001` returns the following verified values:
*   **Observation ID:** `TC-Z03-F02-LIDAR-OBS001` (Inside nested observation block)
*   **Timestamp:** `2026-08-13 09:14:22+00:00` (Equivalent to `2026-08-13T09:14:22Z` UTC)
*   **Coordinates:** Latitude `19.1288`, Longitude `72.9421`
*   **Parameter:** `canopy_height`
*   **Value:** `4.7`
*   **Unit:** `m`
*   **Method:** `aerial`
*   **Status:** `RETRIEVED` (at root payload level)

All values match our canonical target observation coordinates, timestamp, and measurement values exactly.

---

## 5. Real API Schema Compatibility
There are structural discrepancies between the Group 1 response and the Group 2 validation input schema:

| Attribute | Group 1 Real API Response | Group 2 Adapter Input | Difference |
| :--- | :--- | :--- | :--- |
| **Observation Wrapper** | Nested as `response.observation` | Root key `payload.observation` | Structural nest |
| **Timestamp** | `observation.observed_at` | `observation.timestamp` | Field name mismatch |
| **Location** | `observation.geo_location: {latitude, longitude}` | `observation.location: {lat, lon}` | Nested key names mismatch |
| **Measurements** | `observation.measurements` (JSON List) | `observation.measurement` (JSON Object) | List vs Object mismatch |
| **Status** | `is_synthetic: false` | `observation.status` (SYNTHETIC_TEST / VERIFIED) | Data type and field name mismatch |

*Conclusion:* An input transformation/mapping layer is required before passing the API payload to [`sanskar_adapter.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/adapter/sanskar_adapter.py).

---

## 6. Group 1 Retrieval Integration Status
*   **Direct Access:** Verified. The API is reachable from our environment and responds with HTTP 200.
*   **Client Adapter:** **MISSING** (No HTTP client exists in our codebase to fetch observations).
*   **Schema Compatibility:** **RED** (Needs translation mapping).
*   **Blockers:** None on retrieval; the API boundary is fully open.

---

## 7. Group 2 Context Generation Path
*   **Adapter Entrypoint:** [`sanskar_adapter.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/adapter/sanskar_adapter.py) $\rightarrow$ `resolve_context(payload: Dict[str, Any])`.
*   **Data Consumption:** Consumes payload arguments passed to it. It does not fetch live records or connect to databases itself.
*   **Direct Consumption of Group 1 Payload:** Incompatible. Passing Group 1 JSON directly will fail basic contract validations.

---

## 8. Determinism Audit
*   **Adapter Execution:** Fully deterministic.
*   **ID Generation:** `action_request_id` uses namespace-based deterministic UUID generation (`uuid.uuid5`) keyed on trace ID and observation ID.
*   **Trace Consistency:** Maintained. Re-executing the adapter over identical inputs yields identical outputs.

---

## 9. Failure-Path Audit
*   **Group 1 Observation Not Found (404):** **MISSING** (No client logic to catch 404).
*   **Malformed Observation (Invalid JSON):** **MISSING** (No client validation of malformed inputs).
*   **Invalid Measurement:** **GREEN** (Raises `ValueError` in adapter).
*   **Unsupported Parameter:** **GREEN** (Raises `ValueError` in adapter).
*   **Missing Scientific Evidence:** **GREEN** (Raises `ValueError` on empty citations).
*   **GAP Scientific Context:** **GREEN** (Adapter isolates missing baselines with `WAITING_FOR_VERIFIED_CONTEXT` status).
*   **Stale Temporal Context:** **GREEN** (Returns `temporal_match = False` and sets status to `ADAPT`).
*   **Invalid DOI:** **GREEN** (Rejects incorrect DOIs for canopy/biomass claims).
*   **Spatial Mismatch:** **GREEN** (Returns `spatial_match = False` and sets status to `ADAPT`).
*   **Provenance/Identity Mismatches:** **GREEN** (Enforces correct mappings and raises exceptions).

---

## 10. GAP → Action Safety Audit
*   **GAP to Action Defect:** **RED**
*   *Details:* Currently, if `scientific_context` is marked as a GAP, the adapter creates an `action_request` block in the result envelope with `"context_status": "GAP"` and `"requested_action": "GAP"`. 
*   *Conflict:* This violates Sakshi's new contract rule: **GAP must represent an abstention/refusal to execute and must not contain any Action Request payload** (which could otherwise cause downstream systems to attempt execution).
*   *Correction required:* The `action_request` key must be completely omitted or set to `null` in the result envelope when `context_status = "GAP"`.

---

## 11. Scientific Evidence Compatibility
*   **Status:** **GREEN**
*   **DOIs:** Canopy studies are mapped to `10.1016/j.rsma.2023.103207` (ScienceDirect), and spatial extent checks are mapped to `10.5281/zenodo.6894273`. No conflicting DOIs are present in active fixtures.

---

## 12. Temporal Applicability Compatibility
*   **Status:** **GREEN**
*   **Observed At:** `2026-08-13` falls within the baseline validity range `2020-2026`, returning `temporal_match = true`.

---

## 13. Group 4 Contract Audit
*   **Authoritative Contract:** **RED / MISSING**
*   *Details:* No authoritative `/vana/execute` contract or API registrations exist in our workspace.
*   *Local Format Validity:* The current Action Request JSON layout in our adapter is a mock format and must not be treated as final until Karan/Mohit provide the API spec.

---

## 14. SANSKAR Runtime Audit
*   **Service Port:** Port `8000` is offline.
*   **Contextualisation Endpoint:** SANSKAR core has no environmental contextualisation handler. All evaluations must continue to run externally in the validation adapter.
*   **SQLite/Local Classification:** **LOCAL** (Stand-in databases and mock network boundaries are active).

---

## 15. MasterDB Runtime Audit
*   **Database Connectivity:** SQLite `vana_demo_corrected.db` runs locally. The shared PostgreSQL database remains isolated.

---

## 16. Exact Pratik Implementation Gaps
*   **Gap 1:** Missing HTTP client class (`Group1ApiClient`) to request the live observation endpoint.
*   **Gap 2:** Missing schema mapper (`map_group1_to_group2`) to translate Group 1's API JSON response into Group 2's validation adapter input format.
*   **Gap 3:** Defective Action Request generation on GAP context (needs to nullify/omit `"action_request"` for GAP).

---

## 17. External Blockers by Owner
*   **Group 4 (Karan/Mohit):** Expose `/vana/execute` endpoint and provide Action Request JSON schema mapping.
*   **Pritesh / Vijay:** Start SANSKAR FastAPI server, configure container port `8001:8000`, and deploy PostgreSQL database in the VPC.

---

## 18. Recommended Execution Order
1.  **Implement Client:** Create a client and translation mapper to pull and translate live Group 1 observation data.
2.  **Fix GAP Safety:** Update the adapter logic to omit `action_request` in GAP states.
3.  **Refactor Tests:** Add client integration tests and update assertions for GAP-to-abstention behavior.
4.  **Handoff:** Deliver validated JSON results to Group 4 once their contract is frozen.

---

## 19. Day-1 Acceptance Checklist
*   [ ] Live observation successfully fetched from `http://163.128.209.18:8013`.
*   [ ] Translated payload aligns with Group 2 input schema.
*   [ ] GAP contexts do not generate Action Request blocks (abstention).
*   [ ] Immutability, provenance, and canonical identity are preserved.
*   [ ] All local integration tests pass.

---

## 20. Final Readiness Verdict
**`AMBER`**
(Ready to implement local client and mapping layers; blocked externally on Group 4 Action Request integration).

---

## Final Question Answer

> *"Given that Group 1 is now LIVE/VERIFIED and Scientific Evidence is frozen, what exactly must Pratik implement next to make the real Group 1 canonical observation flow deterministically into Group 2 context, while preserving identity/provenance and ensuring GAP cannot become an executable Action Request?"*

**Pratik must implement:**
1.  A retrieval client (`Group1ApiClient` in `05_INTEGRATION/adapter/group1_client.py`) that performs a GET request to the live URL `http://163.128.209.18:8013/observations/{observation_id}` and handles response errors (e.g. 404, malformed responses).
2.  A schema mapper (`map_group1_to_group2`) that normalizes the retrieved Group 1 response structure (extracting `observed_at`, `geo_location`, `measurements[0]`, and `is_synthetic`) into a Group 2 contract payload, preserving coordinates, timestamps, parameters, and units.
3.  An update to [`sanskar_adapter.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/05_INTEGRATION/adapter/sanskar_adapter.py) where the `action_request` block is set to `None` (or completely omitted) when `context_status == "GAP"`, satisfying the GAP-to-abstention constraint.
