# Samachar Processing Corrections Required

This report audits the Samachar processing deliverables—specifically [`SAMACHAR_PROCESSING_MANIFEST.md`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/SAMACHAR_PROCESSING_MANIFEST.md) and [`THANE_CREEK_MANGROVE_BASELINE_V0.1.json`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/THANE_CREEK_MANGROVE_BASELINE_V0.1.json)—against the required QA rules and integration constraints.

---

## 1. Compliance Audit of Pritesh/Vijay Corrections

| ID | Correction Rule | Status | Findings / Gaps |
| :--- | :--- | :--- | :--- |
| **A** | `raw_value` exists and preserves the original value. | **FAILED** | The baseline JSON has no field for raw extracted values (e.g., preserving "8.96 sq km" or "896 ha" as text). |
| **B** | `normalised_value` is separate from `raw_value`. | **FAILED** | Only `indicator_value` is present; there is no split between raw and normalised numerical fields. |
| **C** | `transformation_rule_id` is versioned. | **FAILED** | The JSON uses generic text labels (`UNIT_NORMALISATION_RETAINED_SQKM`) instead of versioned rule IDs (e.g. `RULE_UNIT_HA_TO_SQKM_V1.0`). |
| **D** | `date_precision` exists. | **FAILED** | The baseline JSON has no `date_precision` field, and synthetically represents a year-only date ("2020") as "2020-01-01". |
| **E** | Coordinates are not invented. | **PASSED** | Coordinates are kept null (not present in JSON), which matches the source text. |
| **F** | CRS is explicitly represented. | **FAILED** | There is no CRS field inside the baseline JSON payload or metadata block. |
| **G** | Carbon units are correct (e.g. `t C/ha`). | **FAILED** | The manifest (`SAMACHAR_PROCESSING_MANIFEST.md`) lists the target unit for carbon stock as `t/ha` (Tons per Hectare) instead of `t C/ha`, which violates the rule to preserve carbon meaning. |
| **H** | Source page/table/section evidence is retained. | **FAILED** | No evidence reference field exists in the baseline JSON to point to a specific page or table in the report. |
| **I** | `processing_run_id` exists. | **PASSED** | Present as `provenance.processing_run_id` in the JSON. |
| **J** | `source_id` links to the source registry. | **FAILED** | The baseline JSON uses `SRC_GOVT_MFD_001`, which is not registered in the Excel registry sheet. |
| **K** | QA status exists. | **PASSED** | Present as `validation_status` in the JSON (though missing in the SQL database schema). |
| **L** | Transformation history is preserved. | **PARTIAL** | Represented as a flat text array without detail (no timestamps, rule versions, or parameters). |

---

## 2. Field-Level JSON Corrections Required

To align [`THANE_CREEK_MANGROVE_BASELINE_V0.1.json`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/THANE_CREEK_MANGROVE_BASELINE_V0.1.json) with the VANA MasterDB schema and the required scientific/QA precision, the JSON schema must be refactored. 

### Target Field Refactoring Map

*   **`record_id`** $\rightarrow$ Rename to **`observation_id`** or separate into **`observation_id`** and **`measurement_id`** to match the relational database schema.
*   **`provenance`** $\rightarrow$ Restructure to map directly to the `provenance` table.
    *   Add **`source_id`** inside provenance.
    *   Add **`derivation_note`** containing the history and details of transformations.
*   **`observation`** $\rightarrow$ Separate into `geography`, `observation`, and `measurement` properties:
    *   Add **`raw_value_text`** inside measurement (e.g., `"8.96 sq km"`).
    *   Add **`value`** (numeric) and **`unit`** (text).
    *   Add **`date_precision`** inside observation (e.g., `"YYYY"`).
    *   Add **`evidence_page`** and **`evidence_table`** inside provenance or observation.
    *   Add **`geom`** or **`lat`/`lon`** inside geography (kept null if unavailable, but schema-ready).
    *   Add **`crs`** inside geography (e.g., `"EPSG:4326"`).

---

## 3. Manifest Correction Required

In [`SAMACHAR_PROCESSING_MANIFEST.md`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/SAMACHAR_PROCESSING_MANIFEST.md), Section 2.1 (Unit Normalisation):
*   **Current entry:**
    `| Carbon Stock | Mg C ha⁻¹ | Tons per Hectare (t/ha) | 1 Mg = 1 Metric Ton. Semantic consistency checked. |`
*   **Correction needed:**
    `| Carbon Stock | Mg C ha⁻¹ | Tons of Carbon per Hectare (t C/ha) | 1 Mg = 1 Metric Ton. Semantic consistency checked. Preserve carbon meaning. |`
*   **Reason:** Generic `t/ha` represents biomass stock, not carbon stock. Retaining `t C/ha` or `Mg C ha⁻¹` is scientifically mandatory to prevent severe calculation errors in Prakriti's intelligence layers.
