# GIS Dataset QA Report

This report presents a Quality Assurance (QA) audit of the GIS data profile documented in [`thane_creek_gis_dataset.md`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/thane_creek_gis_dataset.md).

---

## 1. GIS Dataset Specifications Audit

| Metadata Field | Documented Profile | Verification Status / Notes |
| :--- | :--- | :--- |
| **Dataset Identity** | Global Mangrove Watch (GMW) v3.0 | **VERIFIED** — Authoritative global mangrove baseline. |
| **Publisher/Source** | UNEP-WCMC, JAXA, Wetlands International, Aberystwyth University, soloEO | **VERIFIED** — Consortium of reputable international research and conservation agencies. |
| **Spatial Coverage** | Thane Creek, Maharashtra, India (derived from global dataset) | **VERIFIED** — Coordinates/geography cover target region. |
| **Temporal Coverage** | Multi-decadal (1996, 2010 baseline, annual updates 2015-2020) | **VERIFIED** — Enables spatial change detection. |
| **Geometry Information** | Vector Polygons | **VERIFIED** — Suitable for boundary delineation and extent mapping. |
| **Coordinate Reference System (CRS)** | EPSG:4326 (WGS 84, Lat/Lon) | **VERIFIED** — Matches Prakriti's standard spatial reference system. |
| **Spatial Resolution** | 25 meters (SAR-derived historical); 10 meters (Sentinel-2 recent) | **VERIFIED** — Sufficient for regional and sanctuary-level mapping. |
| **Primary Indicator** | Mangrove Extent (spatial distribution) | **VERIFIED** — Physical boundary detection. |
| **Secondary Indicator** | Mangrove Change (quantitative gain or loss) | **VERIFIED** — Chronological area calculations. |
| **Source Reference / Access** | Zenodo (DOI: [10.5281/zenodo.6894273](https://zenodo.org/records/6894273)) | **VERIFIED** — Active, secure HTTPS link hosting vector and raster layers. |
| **Data Nature** | Observation (Satellite SAR Backscatter / Optical classification) | **VERIFIED** — Structured spatial observations, not inferences. |

---

## 2. Compliance with Critical Scientific Rules

### Observation vs. Interpretation Separation
The GIS report strictly adheres to the mandated scientific constraint regarding satellite observations:
*   **The Rule:** Satellite-derived measurements (like NDVI or radar backscatter) must NOT automatically be described as "mangrove health".
*   **GMW Report Implementation:** In Section 4, a high-priority alert explicitly states:
    > [!CAUTION]
    > **Critical Scientific Constraint:** The observations derived from this dataset represent strictly *mangrove extent and physical radar backscatter characteristics*... Under no circumstances should these raw satellite-derived spatial values (e.g., NDVI, radar backscatter) be interpreted, labeled, or documented as a scientific conclusion regarding "mangrove health" without further localized, contextual ecological analysis and ground-truthing.
*   **Audit Verdict:** **PASS**. The report successfully isolates the physical observation (extent, density, backscatter) from the interpretation (health, degradation, quality), ensuring the downstream Prakriti intelligence layer does not consume inferred conclusions as raw scientific facts.

---

## 3. Major Integration Gaps Identified

1.  **Missing Geometric Files:** While `thane_creek_gis_dataset.md` outlines the dataset metadata, there are **no spatial files (shapefiles, GeoJSON, KML)** provided in the Group 2 deliverables. The GIS lead has not supplied a subset of the Thane Creek GMW polygon.
2.  **No Coordinates in Baseline JSON:** The actual baseline JSON record (`THANE_CREEK_MANGROVE_BASELINE_V0.1.json`) has a geographic place name but has **null geometry and no coordinates**, failing to use the spatial reference systems or polygons described in this GIS report.
3.  **Expired SSL Certificate Warning:** The report correctly notes that the UNEP-WCMC data portal link (`https://data.unep-wcmc.org/datasets/45`) serves an expired SSL certificate (`NET::ERR_CERT_DATE_INVALID`) as of August 2026. The fallback to the Zenodo DOI repository is verified and functional.
