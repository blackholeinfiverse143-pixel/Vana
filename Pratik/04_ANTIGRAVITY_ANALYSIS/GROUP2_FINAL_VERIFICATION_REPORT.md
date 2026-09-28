# Group 2 Final Verification Report

**Role:** Group 2 Integration and Verification Engineer  
**Sprint:** VANA / PRAKRITI 1 KM Sprint — Thane Creek Mangrove Baseline  
**Date:** 13 August 2026  
**Final Acceptance Status:** **PARTIAL / BLOCKED** (Real VM PostgreSQL Integration) | **VERIFIED** (Corrected Local SQLite Pipeline)

---

## 1. Executive Summary

This report delivers the final integration and verification audit for Group 2 (SAMACHAR / Scientific Data Foundation) and its integration with Group 1 (VANA/MasterDB Foundation). 

Using the authoritative government/ISRO data for the **Thane Creek Flamingo Sanctuary (TCFS)** mangrove area (**8.96 sq km**), we traced this real record through the complete acceptance chain. 

The original pipeline deliverables were **blocked** from completion due to critical schema mismatches, missing source registry records, database constraint violations, and a logical bug in the idempotency deduplication script. By engineering corrected copies of the baseline JSON ([`THANE_CREEK_MANGROVE_BASELINE_V0.1_CORRECTED.json`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/THANE_CREEK_MANGROVE_BASELINE_V0.1_CORRECTED.json)) and creating a corrected pipeline script ([`demo_pipeline_corrected.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/demo_pipeline_corrected.py)), we successfully demonstrated the entire acceptance chain **locally** against a relational database stand-in. 

However, because the network route to the VM hosting the real PostgreSQL instance remains unavailable, the final integration step to VM Postgres cannot be completed.

---

## 2. Team Deliverables Status

| Deliverable | Owner | Audit Status | Key Findings |
| :--- | :--- | :--- | :--- |
| **`schema.sql`** | Kavy (Group 1) | **VERIFIED** | Correctly defines relational structure, but lacks fields for date/location precision and validation status. Requires PostGIS. |
| **`demo_pipeline.py`** | Kavy (Group 1) | **PARTIAL** | Functional SQLite POC, but fails idempotency (duplicates rows) and ignores the baseline JSON. |
| **`evidence_output.txt`** | Kavy (Group 1) | **VERIFIED** | Accurate execution log of the buggy demo pipeline. |
| **`GROUP1_EOD_REPORT.md`** | Kavy (Group 1) | **VERIFIED** | Outlines integration blockers and VM database access constraints. |
| **`Scientific_Source_Registry_V0.1.xlsx`** | Sakshi (Group 2) | **PARTIAL** | Missing registry entries for the baseline government source (`SRC_GOVT_MFD_001`). Bibliographic gaps exist. |
| **`SAMACHAR_PROCESSING_MANIFEST.md`** | Pritesh (Group 2) | **PARTIAL** | Clear processing rules, but target carbon units are scientifically incorrect (`t/ha` instead of `t C/ha`) and lack versioned rules. |
| **`THANE_CREEK_MANGROVE_BASELINE_V0.1.json`** | Pritesh (Group 2) | **PARTIAL** | Formats baseline data, but violates SQL schema constraints (missing source ID, invalid columns, null geometry). |
| **`thane_creek_gis_dataset.md`** | Kaushal (Group 2) | **VERIFIED** | Accurate metadata profile for Global Mangrove Watch. No spatial boundary files are attached. |
| **`VIJAY_QA_REVIEW.md`** | Vijay (Group 2) | **VERIFIED** | Independent QA notes identifying major gaps in date/location precision. |

---

## 3. Source Registry Status
*   **Audit Status:** **PARTIAL**
*   **Findings:** The 13 registered literature sources are real and bibliographically verified. However, observations for 5 sources (including Goldin Quadros's PhD thesis) are missing or incomplete in the extraction sheet.
*   **Core Gap:** The primary government report (`SRC_GOVT_MFD_001`) from which the baseline record of 8.96 sq km was drawn is **not registered** in the Excel spreadsheet, creating an orphan reference.

## 4. GIS Dataset Status
*   **Audit Status:** **VERIFIED** (Metadata) | **MISSING** (Spatial Geometries)
*   **Findings:** The Global Mangrove Watch (GMW) v3.0 dataset profile is highly detailed, correct in its CRS (EPSG:4326), and temporal baseline. No actual GIS files (shapefiles/GeoJSON) were delivered in the workspace.
*   **Scientific Compliance:** Adheres strictly to the rule separating physical observation (mangrove extent) from interpretation (mangrove health).

## 5. Samachar Processing Status
*   **Audit Status:** **PARTIAL**
*   **Findings:** The recommended staging flow (`Source → Raw/Staging → Structured → Normalised → QA → MasterDB`) was bypassed. The target units for carbon stock in the manifest were written as `t/ha` instead of `t C/ha`, which violates the rule to preserve carbon meaning.

## 6. Scientific QA Status
*   **Audit Status:** **PARTIAL**
*   **Findings:** Gaps remain regarding the verification of Sheetalji's PhD thesis (currently marked `CLAIM ONLY`) and older intertidal theses which are bibliographically cited but not located.

## 7. MasterDB Schema Mapping
*   **Audit Status:** **FAILED** (Original JSON) | **VERIFIED** (Corrected JSON)
*   **Findings:** The original baseline JSON payload has fields (`record_id`, `validation_status`, `location_precision`, `transformations_applied` as array) that do not exist in `schema.sql`. It also lacks coordinates or geometry, which fails the `NOT NULL` PostGIS constraint on the database's `geography.geom` column.

---

## 8. Actual Ingestion and Retrieval Results

### A. The Original Pipeline Ingestion (Singh et al. 2023 Record)
*   **Ingestion Status:** **FAILED / BUGGED**
*   **Deduplication/Idempotency:** **FAILED**. The original `demo_pipeline.py` script attempts to test idempotency, but because the first insert uses a manual ID and the second uses a hashed ID, the script writes a duplicate row. The row count goes from 1 to 2, failing the idempotency contract.
*   **Target Database:** Local SQLite stand-in (`vana_demo.db`).
*   **Postgres VM Ingestion:** **BLOCKED** due to network route isolation.

### B. The Corrected Pipeline Ingestion (Sanctuary Baseline Record)
*   **Ingestion Status:** **VERIFIED**
*   **Deduplication/Idempotency:** **VERIFIED (SUCCESS)**. By using a deterministic, consistent ID (`MEAS-TCFS-EXTENT-2020-01`), the corrected script does not write duplicate rows. Count remains at 1.
*   **Verification Query Results (Local SQLite `vana_demo_corrected.db`):**
    *   *Observation ID:* `OBS_TCFS_001_SAMACHAR_RUN_20260812_01` (Precision: `YYYY`)
    *   *Measurement ID:* `MEAS-TCFS-EXTENT-2020-01`
    *   *Original/Raw Value:* `8.96 sq km`
    *   *Normalised Value:* `8.96` `sq km`
    *   *Source ID:* `SRC_GOVT_MFD_001` (`Maharashtra Forest Department & ISRO Mangrove Cell Report (2020)`)
    *   *Run ID:* `RUN_20260812_01` (Operator: `Pritesh`)
    *   *Derivation Note:* `Extracted from Maharashtra Forest Department & ISRO Mangrove Cell Report (2020)...`
    *   *Validation Status:* `UNCERTAIN` (mapped through `dataset.status` as `dataset_id = DS_GOVT_MFD_001`)

---

## 9. Provenance Verification
Every quantitative value in the corrected run was successfully joined back to its source reference, pipeline run, operator, and raw value. The database successfully trace-queries the origin of the 8.96 sq km record to the government report with a confidence level of `UNCERTAIN` due to the lack of a verified document PDF.

---

## 10. Evidence Index

1.  **Original Ingestion Output:** [`evidence_output.txt`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/evidence_output.txt) (Confirms duplicate row insertion error).
2.  **Corrected Baseline JSON:** [`THANE_CREEK_MANGROVE_BASELINE_V0.1_CORRECTED.json`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/THANE_CREEK_MANGROVE_BASELINE_V0.1_CORRECTED.json).
3.  **Corrected Pipeline Script:** [`demo_pipeline_corrected.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/demo_pipeline_corrected.py).
4.  **Corrected Run Log:** Captured in terminal run. Proves successful schema creation with date precision, ingestion, retrieval join, idempotency success, and constraint rejection.

---

## 11. Blockers

1.  **Database Connection Blocker:** There is no route or configuration to reach the real VM hosting the PostgreSQL instance.
2.  **Schema Mismatches (Database Layer):** `schema.sql` lacks columns for `date_precision`, `location_precision`, and `validation_status` which are required by the Samachar processing rules.
3.  **PostGIS Constraint Blocker:** The `geography.geom` column in `schema.sql` has a `NOT NULL` constraint. The baseline JSON does not have geometries, which prevents database insertion.
4.  **Source Registry Gaps:** The government report (`SRC_GOVT_MFD_001`) and multiple theses are missing actual PDFs or verified text, marking them as `CLAIM ONLY`.
5.  **Samachar Endpoint Block:** The external Samachar endpoint was unreachable during the sprint, preventing live automated processing.

---

## 12. Final Acceptance Status

*   **Overall Pipeline Status:** **PARTIAL**
*   **Stopping Point:** The pipeline was successfully completed and verified **locally** against a stand-in database using corrected schemas and data payloads. The pipeline is **blocked** from final VM Postgres deployment.

---

## 13. Pratik Action List
*Actions requiring Pratik or the team to resolve, ordered by criticality:*

1.  **Resolve VM Database Access (Critical):** Network paths and credentials must be established to connect the ingestion scripts to the real `MASTERDB_DATABASE_URL` PostgreSQL instance.
2.  **Update DB Schema (High):** Apply the schema migration to add `date_precision TEXT CHECK (date_precision IN ('YYYY', 'YYYY-MM', 'YYYY-MM-DD'))` to the `observation` table, and register `SRC_GOVT_MFD_001` in the `source` table.
3.  **Relax PostGIS Constraints or Provide Geometries (High):** Either modify the `geography` table DDL to allow nullable geometries (`geom GEOMETRY(Geometry, 4326) NULL`) or ensure Kaushal provides spatial polygons (shapefiles/GeoJSON) for all baseline locations.
4.  **Correct Carbon Units in Manifest (Medium):** Modify [`SAMACHAR_PROCESSING_MANIFEST.md`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/SAMACHAR_PROCESSING_MANIFEST.md) unit mappings to use `t C/ha` instead of `t/ha` for carbon stocks.
5.  **Source Retrieval (Medium):** Retrieve the full text PDF for `SRC_GOVT_MFD_001` (Maharashtra Forest Department & ISRO Mangrove Cell Report 2020) and Sheetalji's PhD thesis to move status from `CLAIM ONLY` to `VERIFIED`.

---

## 14. Vijay Verification Checklist
*Checklist for Vijay to independently reproduce the final verification claims:*

- [ ] **1. Clean Stand-in Run:** Confirm that `vana_demo_corrected.db` does not exist, then run `python demo_pipeline_corrected.py` in the terminal.
- [ ] **2. Schema Initialization:** Verify that tables are created and `schema_version` is initialized to version `0.1` with description `"Initial VANA foundation with date_precision support"`.
- [ ] **3. Ingestion and In-Memory Integrity:** Open the database using a SQLite client (or check terminal stdout) and confirm that a row exists in `measurement` with ID `MEAS-TCFS-EXTENT-2020-01` and value `8.96`.
- [ ] **4. Retrieval Join Verification:** Confirm that the retrieval query outputs a single join record containing the exact raw value `"8.96 sq km"`, normalized value `8.96`, and links to source `SRC_GOVT_MFD_001`.
- [ ] **5. Date Precision Check:** Verify that the observation record has `date_precision = 'YYYY'` and `observation_date = '2020-01-01'`.
- [ ] **6. Idempotency Assertion:** Verify that step [4] outputs `before = 1, after = 1`, proving that no duplicate measurement was written on re-ingestion.
- [ ] **7. Constraint Rejection Check:** Confirm that step [5] outputs `CHECK constraint failed: date_precision...`, proving that invalid precision inputs are rejected.
- [ ] **8. DB File Verification:** Locate the output files `vana_demo_corrected.db` in the workspace to confirm file creation.
