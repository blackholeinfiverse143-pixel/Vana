# Group 2 Integration Audit Report

This document audits the available deliverables for the VANA / PRAKRITI 1 KM Sprint (Group 2 - Samachar / Scientific Data Foundation and Group 1 - VANA/MasterDB Foundation).

## Deliverables Inventory and Status

| File | Owner | Purpose | Evidence | Dependencies | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [`schema.sql`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/schema.sql) | Kavy (Group 1 Lead) | Relational database DDL schema for VANA MasterDB. | 8 tables (`schema_version`, `source`, `dataset`, `geography`, `observation`, `measurement`, `processing_run`, `provenance`) + indexes. | PostGIS extension, Postgres database, EPSG:4326 | **VERIFIED** |
| [`demo_pipeline.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/demo_pipeline.py) | Kavy (Group 1 Lead) | Python script acting as a proof-of-concept for database operations (schema, ingestion, query, idempotency, rejection, backup). | Ingests 1 study, retrieves, checks idempotency, and tests backup/restore. | SQLite (stand-in for Postgres), `schema.sql` table structure, python libraries (`sqlite3`, `json`, `hashlib`) | **PARTIAL** |
| [`evidence_output.txt`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/evidence_output.txt) | Kavy (Group 1 Lead) | Console log output from executing `demo_pipeline.py`. | Execution logs for schema creation, ingestion, retrieval, idempotency test, constraint check, and backup restore. | Successful run of `demo_pipeline.py` | **VERIFIED** |
| [`GROUP1_EOD_REPORT.md`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/GROUP1_EOD_REPORT.md) | Kavy (Group 1 Lead) | End-of-day status report of Group 1 (Foundation/MasterDB). | Outlines achievements, honesty flags, blockers, and next actions. | `schema.sql`, `demo_pipeline.py` | **VERIFIED** |
| [`Scientific_Source_Registry_V0.1.xlsx`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/Scientific_Source_Registry_V0.1.xlsx) | Sakshi (Scientific Literature Lead) | Scientific literature sources and observation records. | 13 sources and 19 observations documented in Excel sheets. | Authoritative papers, physical publications | **PARTIAL** |
| [`SAMACHAR_PROCESSING_MANIFEST.md`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/SAMACHAR_PROCESSING_MANIFEST.md) | Pritesh (Samachar Processing Lead) | Samachar pipeline definition, normalisation rules, and record template. | Documented pipeline stages, unit/date/location normalisation rules, duplication conflict rules. | Source registries, target MasterDB units | **PARTIAL** |
| [`THANE_CREEK_MANGROVE_BASELINE_V0.1.json`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/THANE_CREEK_MANGROVE_BASELINE_V0.1.json) | Pritesh (Samachar Processing Lead) | Structured baseline record for Thane Creek Flamingo Sanctuary mangrove extent. | Single JSON record claiming 8.96 sq km of mangrove extent. | Source `SRC_GOVT_MFD_001` (unregistered), Samachar run | **PARTIAL** |
| [`thane_creek_gis_dataset.md`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/thane_creek_gis_dataset.md) | Kaushal (Earth Observation / GIS Lead) | Earth Observation/GIS data baseline profile. | Metadata profile of Global Mangrove Watch (GMW) dataset (Zenodo DOI, temporal range, CRS). | Global Mangrove Watch dataset, EPSG:4326 | **VERIFIED** |
| [`VIJAY_QA_REVIEW.md`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/VIJAY_QA_REVIEW.md) | Vijay (Observation QA Lead) | Independent QA and provenance verification notes. | Summarized findings and exact list of corrections needed. | Sakshi & Pritesh deliverables | **VERIFIED** |

---

## Detailed Audit Findings

### 1. Inconsistencies and Contradictions
*   **Idempotency Failure:** The `demo_pipeline.py` script contains a critical logical bug in its idempotency test. The first insertion of the allometry measurement is hardcoded with `measurement_id = 'MEAS-THANECREEK-AGB-ALLOM-01'`. The idempotent test calculates a deterministic ID `MEAS-a1b2c3d4e5f6` based on a content hash and attempts to insert it. Because these two IDs do not match, the second insertion succeeds, resulting in a duplicate measurement row in the database. The row count goes from 1 to 2 (as verified in `evidence_output.txt`), which contradicts the claim that idempotency was proven.
*   **Source Registry vs Ingestion Mismatch:**
    *   `demo_pipeline.py` references source `SRC-THANECREEK-2023-CARBONSTOCK-01`, but `Scientific_Source_Registry_V0.1.xlsx` defines this source as `TCM-LIT-CARB-2023-001`.
    *   `demo_pipeline.py` ingests values of `84.83` and `111.31` Mg/ha for `above_ground_biomass`. However, the observations sheet in the Excel registry lists these values as `116.58` and `127.89` Mg C ha⁻¹ for `Mean total carbon stock`.
*   **Baseline JSON Source Gap:** The baseline record in `THANE_CREEK_MANGROVE_BASELINE_V0.1.json` relies on source `SRC_GOVT_MFD_001` (Maharashtra Forest Department & ISRO Mangrove Cell Report 2020), which is completely absent from the source registry Excel spreadsheet.
*   **Schema vs payload Mismatch:** The schema in `schema.sql` does not support several fields present in the baseline JSON (`THANE_CREEK_MANGROVE_BASELINE_V0.1.json`) and the manifest template:
    *   The SQL schema has no `record_id` (uses `observation_id` as primary key).
    *   The SQL schema has no `location_precision` column in `geography` or `observation`.
    *   The SQL schema has no array column for `transformations_applied` in the `provenance` or `processing_run` tables (only a `derivation_note` text field in `provenance`, and a `transform_applied` text field in `measurement`).
    *   The SQL schema has no `validation_status` column in `observation` or `measurement`.

### 2. Missing Information
*   **VM/Postgres Connectivity:** There is no configuration or network path in the environment to connect to the VM/Postgres database. All runs are restricted to local stand-in databases.
*   **GIS Polygons:** `thane_creek_gis_dataset.md` documents dataset metadata but does not provide actual spatial boundary shapefiles or GeoJSON polygons for the sanctuary or the mangroves.
*   **Unconfirmed Literature Gaps:** The literature registry contains multiple crucial leads (e.g. Sheetalji's PhD thesis, Borkar 2004, Athalye 1988) marked as `CLAIM ONLY` or `BIBLIOGRAPHIC LEAD`, with no verified PDFs or full text available.
