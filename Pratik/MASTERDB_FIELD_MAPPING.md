# MasterDB Field Mapping Report

This document maps the structured baseline JSON fields from [`THANE_CREEK_MANGROVE_BASELINE_V0.1.json`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/THANE_CREEK_MANGROVE_BASELINE_V0.1.json) to the relational database schema defined in [`schema.sql`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/schema.sql). It flags schema mismatches, missing columns, and foreign key constraint failures.

---

## 1. Field Mapping Table

| Scientific/JSON Field | MasterDB Field | Required? | Mapping | Evidence / Constraint Check |
| :--- | :--- | :--- | :--- | :--- |
| **`record_id`** | `observation.observation_id` | **Yes** | Direct text map. | Primary Key for `observation` table. |
| **`source_id`** | `source.source_id` | **Yes** | Foreign Key reference across multiple tables. | **CRITICAL FAILURE:** `SRC_GOVT_MFD_001` is not registered in the `source` table. Ingestion will fail foreign key constraint checks. |
| **`source_reference`** | `source.title` or `source.citation` | **Yes** (title is NOT NULL) | Belongs to `source` table; no direct column in `observation`. | Mismatch: JSON represents source metadata inline rather than normalized. |
| **`provenance.processing_run_id`** | `processing_run.run_id` / `provenance.run_id` | **Yes** (provenance.run_id is FK) | References the `processing_run` table. | The run ID must exist in the `processing_run` table prior to inserting the provenance trace. |
| **`provenance.transformations_applied`** | `measurement.transform_applied` or `provenance.derivation_note` | **No** (schema fields are nullable) | Mismatch: JSON provides a JSON array of strings (`["UNIT_NORMALISATION_RETAINED_SQKM", ...]`); schema expects a single `TEXT` column. | Must be converted/joined to a single string (e.g. via `", ".join()`) before ingestion. |
| **`provenance.extraction_operator`** | `processing_run.actor` | **Yes** (`actor` is NOT NULL) | Maps to the run execution record. | Documents who performed the pipeline execution. |
| **`observation.indicator_name`** | `measurement.metric_name` | **Yes** | Maps to the quantitative measurement metadata. | Links the observation to the actual quantitative metric. |
| **`observation.indicator_value`** | `measurement.value` | **Yes** | Direct conversion to `NUMERIC`. | Represents the quantitative value. |
| **`observation.indicator_unit`** | `measurement.unit` | **Yes** | Direct mapping to `TEXT`. | Represents the unit (e.g., `'sq km'`, `'t C/ha'`). |
| **`observation.observation_date`** | `observation.observation_date` | **No** | ISO string parsed into a `DATE`. | Represents the date of the observation. |
| **`observation.location_precision`** | **NONE** | **No** | **MISMATCH:** No column for location precision exists in the schema. | Must either be discarded, stored in `geography.notes`, or stored in `observation.confidence`. |
| **`observation.location_name`** | `geography.place_name` | **Yes** | Maps to the geography spatial reference. | A geography record must be created with a unique `geo_id` and referenced via `observation.geo_id`. |
| **`validation_status`** | **NONE** | **No** | **MISMATCH:** No validation status column exists in `observation` or `measurement`. | `dataset` has a `status` column, but it only accepts `'REGISTERED', 'VALIDATED', 'REJECTED', 'UNCERTAIN'`. The JSON value `'PENDING_QA_VIJAY'` is invalid. |

---

## 2. Ingestion Blockers & Database Mismatches

1.  **Foreign Key Constraint Violations (Blocked Ingestion):**
    *   The baseline JSON references `"source_id": "SRC_GOVT_MFD_001"`. Since there is no SQL script in `schema.sql` or in the ingestion script that registers `SRC_GOVT_MFD_001` in the `source` table, inserting this record directly will trigger a foreign key violation (`FOREIGN KEY constraint failed` for `dataset.source_id` or `processing_run.source_id`).
2.  **Missing Geography/Geometry Data:**
    *   The `geography` table in `schema.sql` requires a PostGIS `geom` column (`GEOMETRY(Geometry, 4326) NOT NULL`). 
    *   The baseline JSON has no coordinate or polygon geometry data. Attempting to ingest this record into a PostGIS database would require inserting a null or empty geometry, but the schema specifies `geom` is `NOT NULL`. This is a database-level blocker.
3.  **Missing Schema Columns:**
    *   There are no columns in the `observation` or `measurement` tables to house `location_precision` or `validation_status` fields.
    *   `transformations_applied` is represented as an array in the JSON, but the database schema only provides flat `TEXT` fields (`transform_applied` and `derivation_note`).
