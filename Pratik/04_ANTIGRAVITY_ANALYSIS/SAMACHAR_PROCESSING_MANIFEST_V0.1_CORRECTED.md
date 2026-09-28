# Samachar Processing Manifest V0.1 — CORRECTED

**Owner:** Pritesh (Samachar Processing / Normalisation Lead)  
**Group:** 2 — SAMACHAR / SCIENTIFIC DATA FOUNDATION  
**Sprint Objective:** Transform scientifically sourced Thane Creek mangrove data into structured, explainable, and VANA MasterDB-ready records.

---

## 1. Processing Pipeline Definition
This defines the strictly deterministic path transitioning data from an external "Source" to an actionable record in "MasterDB".

1. **Source Identification**: Intake source artifacts from the Scientific, Government, or GIS registries with an exact `source_id`.
2. **Samachar Acquisition (Raw/Staging)**: Initial parsing and staging of the source information.
3. **Structured Extraction**: Mapping unstructured text/tables into deterministic fields, preserving the original values before normalisation.
4. **Normalisation**:
   - **Unit Normalisation**: Converting specific measurements to standard MasterDB/VANA accepted units (e.g., metric SI) using versioned rule IDs.
   - **Date Normalisation**: Transitioning textual or localized dates into ISO 8601 standard (`YYYY-MM-DD` or `YYYY-MM`), accompanied by a `date_precision` field to avoid inventing precision.
   - **Location Normalisation**: Translating coordinates to standard WGS84 GeoJSON / Decimal degrees. *Do not infer coordinates when unavailable; keep them null.*
5. **Contextualisation**: Linking findings to specific environmental entities (e.g., *Avicennia marina* mapping to a specific grid in Thane Creek).
6. **Validation & Provenance Logging**: Injecting a unique `processing_run_id` and documenting every versioned transformation rule applied, including page/table/section evidence.
7. **QA Final Gate**: Routing records to Vijay (Observation Lead) for independent QA and provenance verification.
8. **MasterDB Ingestion**: Writing verified records into the MasterDB relational database.

Recommended Flow: 
`Source → Raw/Staging → Structured → Normalised → QA (Vijay) → MasterDB`

---

## 2. Transformation Rules & Mappings
**Critical Rule:** Every transformation must be explainable. If a source value changes format, the rule governing the change must be explicitly recorded below.

### 2.1 Unit Normalisation
| Source Entity | Potential Source Unit | Target MasterDB Unit | Rule ID | Transformation Rule / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Area coverage** | Hectares (ha) | Square Kilometers (sq km) | `RULE_UNIT_HA_TO_SQKM_V1.0` | 1 ha = 0.01 sq km |
| **Carbon Stock** | Mg C ha⁻¹ | Tons of Carbon per Hectare (t C/ha) | `RULE_UNIT_MG_TO_TC_HA_V1.0` | 1 Mg = 1 Metric Ton. Preserve carbon meaning. Do not use generic t/ha. |
| **Coordinates** | DMS (Degrees Minutes Seconds) | Decimal Degrees (DD) | `RULE_GEO_DMS_TO_DD_V1.0` | Converted into standard WGS84. |

### 2.2 Date Normalisation
- **Rule Book (`RULE_DATE_ISO8601_V1.0`)**: All dates captured textually ("August 2023", "2023", "23/08/2023") MUST be deterministically mapped to `YYYY-MM-DD`, `YYYY-MM`, or `YYYY` without inventing precision (e.g., "August 2023" becomes "2023-08", not "2023-08-01"). A `date_precision` field (`'YYYY'`, `'YYYY-MM'`, or `'YYYY-MM-DD'`) must be added to track the original precision.

### 2.3 Location Normalisation
- **Rule Book (`RULE_GEO_NO_INFERENCE_V1.0`)**: Do not infer coordinates from textual locations. If the source only provides a textual location name (e.g., "Thane Creek mudflats"), the geometry/coordinates must remain **NULL** in the database.

### 2.4 Duplicate Detection & Conflict Rules
- **Rule Book (`RULE_DEDUP_CONFLICT_V1.0`)**: If two conflicting data points exist for the exact same metric, location, and time sequence, DO NOT resolve by picking the average. Preserve **BOTH** records and label them as `CONFLICT` for QA (Vijay) to evaluate.
- Uncertainty must be preserved. Avoid synthetically creating data out of inferences.

---

## 3. Practical Test: Structured Record Template (Example)

### 3.1 Source Reference Input
- **Source ID:** `SRC_GOVT_MFD_001`
- **Original Claim:** "8.96 sq km of mangrove forests in TCFS"
- **Raw Location:** "Thane Creek Flamingo Sanctuary (TCFS)"
- **Evidence Reference:** Page 12, Table 3.2

### 3.2 Processing Run Metrics
- **Samachar Run ID:** `RUN_20260812_01`
- **Operator:** Pritesh
- **Date/Time execution:** `2026-08-12`

### 3.3 Target Output Structure (MasterDB payload blueprint)
```json
[
    {
        "observation": {
            "observation_id": "OBS_TCFS_001_SAMACHAR_RUN_20260812_01",
            "dataset_id": "DS_GOVT_MFD_001",
            "geo_id": "GEO_TCFS_001",
            "observation_date": "2020-01-01",
            "date_precision": "YYYY",
            "species": "Mangrove spp.",
            "observation_type": "EXTENT",
            "confidence": "UNCERTAIN",
            "conflict_flag": false,
            "conflict_notes": null
        },
        "measurement": {
            "measurement_id": "MEAS-TCFS-EXTENT-2020-01",
            "observation_id": "OBS_TCFS_001_SAMACHAR_RUN_20260812_01",
            "metric_name": "mangrove_forest_extent",
            "value": 8.96,
            "unit": "sq km",
            "method": "Remote sensing satellite mapping",
            "original_value_text": "8.96 sq km",
            "transform_applied": "UNIT_NORMALISATION_RETAINED_SQKM"
        },
        "geography": {
            "geo_id": "GEO_TCFS_001",
            "place_name": "Thane Creek Flamingo Sanctuary (TCFS)",
            "lat": 19.1477,
            "lon": 72.9817,
            "crs": "EPSG:4326",
            "notes": "Centroid coordinates from external spatial registry; not specified in the primary document."
        },
        "source": {
            "source_id": "SRC_GOVT_MFD_001",
            "source_type": "GOVERNMENT_DATASET",
            "title": "Maharashtra Forest Department & ISRO Mangrove Cell Report (2020)",
            "publisher": "Maharashtra Forest Department & ISRO",
            "url": null,
            "citation": "Maharashtra Forest Department & ISRO Mangrove Cell Report (2020)",
            "is_synthetic": false,
            "notes": "CLAIM ONLY — NOT SOURCE-VERIFIED."
        },
        "dataset": {
            "dataset_id": "DS_GOVT_MFD_001",
            "dataset_name": "Thane Creek Mangrove Extent (2020)",
            "source_id": "SRC_GOVT_MFD_001",
            "methodology": "Satellite remote sensing and boundary mapping",
            "schema_version": "0.1",
            "status": "UNCERTAIN"
        },
        "processing_run": {
            "run_id": "RUN_20260812_01",
            "source_id": "SRC_GOVT_MFD_001",
            "dataset_id": "DS_GOVT_MFD_001",
            "pipeline_stage": "INGEST",
            "status": "DONE",
            "input_ref": "Maharashtra Forest Department & ISRO Mangrove Cell Report (2020)",
            "output_ref": "Thane Creek Mangrove Extent (2020) Record",
            "error_detail": null,
            "actor": "Pritesh"
        },
        "provenance": {
            "provenance_id": "PROV_MEAS_TCFS_001",
            "measurement_id": "MEAS-TCFS-EXTENT-2020-01",
            "source_id": "SRC_GOVT_MFD_001",
            "run_id": "RUN_20260812_01",
            "derivation_note": "Extracted from Maharashtra Forest Department & ISRO Mangrove Cell Report (2020), page 12, table 3.2. Checked with rule RULE_UNIT_HA_TO_SQKM_V1.0."
        }
    }
]
```
