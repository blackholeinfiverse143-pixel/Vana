# Evidence Audit Report

This document audits the claims made in [`GROUP1_EOD_REPORT.md`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/GROUP1_EOD_REPORT.md) and [`evidence_output.txt`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/evidence_output.txt) to verify what has actually been demonstrated and what remains unverified or blocked.

---

## 1. Claims Audit and Classification

### Claim 1: Schema created successfully (`schema.sql`)
*   *Stated Evidence:* `schema.sql` file contains complete DDL statements.
*   *Audit Status:* 
    *   **VERIFIED (local SQLite stand-in):** Table structure successfully initialized in `vana_demo.db`.
    *   **BLOCKED (real VM Postgres):** Has not been run against the target VM/Postgres database due to network path limitations.
*   *Verdict:* **PARTIAL**

### Claim 2: Ingestion of one real Thane Creek mangrove record
*   *Stated Evidence:* `demo_pipeline.py` inserts above-ground biomass measurements from a 2023 study.
*   *Audit Status:* 
    *   **VERIFIED (local SQLite stand-in):** The hardcoded measurements were inserted.
    *   **BLOCKED (real VM Postgres):** Ingestion was not performed on the target Postgres.
*   *Verdict:* **PARTIAL**

### Claim 3: Ingestion of the Thane Creek baseline JSON
*   *Stated Evidence:* Pritesh/Samachar processing claims the first baseline record is ready and parsed.
*   *Audit Status:* **CLAIM ONLY** (and false). The baseline JSON file [`THANE_CREEK_MANGROVE_BASELINE_V0.1.json`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/THANE_CREEK_MANGROVE_BASELINE_V0.1.json) is **never read or loaded** by `demo_pipeline.py`. The script relies entirely on a different hardcoded record.
*   *Verdict:* **CLAIM ONLY**

### Claim 4: Retrieval and provenance trace proven
*   *Stated Evidence:* Step [3] in `evidence_output.txt` shows a join query returning biomass values and their source details.
*   *Audit Status:* 
    *   **VERIFIED (local SQLite stand-in):** SQL join query executed successfully.
    *   **BLOCKED (real VM Postgres):** No queries run on target database.
*   *Verdict:* **PARTIAL**

### Claim 5: Idempotency (deduplication) proven
*   *Stated Evidence:* Step [4] of `demo_pipeline.py` attempts to insert the same record twice.
*   *Audit Status:* **CLAIM ONLY (and FAILED in practice)**. 
    *   The console output in `evidence_output.txt` shows: `inserted same record twice -> row count went from 1 to 2`. 
    *   This proves that a duplicate record **was** written to the database. The test failed because the first insert used a manual ID (`MEAS-THANECREEK-AGB-ALLOM-01`) and the re-ingest loop generated a content-hash ID (`MEAS-a1b2c3d4e5f6`), bypassing the SQLite `WHERE NOT EXISTS` check.
*   *Verdict:* **CLAIM ONLY (FAILED)**

### Claim 6: Invalid-record rejection proven
*   *Stated Evidence:* Step [5] of `demo_pipeline.py` attempts to write a null value and captures a `NOT NULL` constraint error.
*   *Audit Status:* **VERIFIED (local SQLite stand-in)**. SQLite rejected the invalid row with error `NOT NULL constraint failed: measurement.value`.
*   *Verdict:* **VERIFIED (local)**

### Claim 7: Backup/restore round-trip proven
*   *Stated Evidence:* Step [6] of `demo_pipeline.py` copies the DB file, deletes the original, copies it back, and checks row counts.
*   *Audit Status:* **VERIFIED (local file operations)**. The file copy succeeded. Note that this does not test database backup utility commands (`pg_dump`/`pg_restore`) which will be used in production Postgres.
*   *Verdict:* **VERIFIED (local)**

### Claim 8: Samachar pipeline integration
*   *Stated Evidence:* Group 1 report claims Samachar pipeline was not used because of integration block.
*   *Audit Status:* **BLOCKED**. The Samachar architecture (`bhiv-SVACS`) is configured for image/OCR/vessel data, and the text-normalization endpoint was unreachable.
*   *Verdict:* **BLOCKED**

---

## 2. Summary Table of Verified vs. Blocked Stages

| Pipeline Leg | Status | Blockers / Gaps |
| :--- | :--- | :--- |
| **Source Registry** | **PARTIAL** | Bibliographic gaps (unlocated PDFs); mismatch between registry IDs and demo pipeline IDs. |
| **Samachar Processing** | **BLOCKED** | Software mismatch (OCR vs Text); endpoint unreachable. Manual extraction used. |
| **Structured JSON** | **PARTIAL** | Baseline JSON exists, but is not ingested; source `SRC_GOVT_MFD_001` is not in the source registry. |
| **MasterDB Ingestion** | **BLOCKED** | Network route to VM Postgres is missing; schema validation fails on null PostGIS geometries. |
| **Retrieval** | **PARTIAL** | Retrieval works on local SQLite; not tested on Postgres. |
