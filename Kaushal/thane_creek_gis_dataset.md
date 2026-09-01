# Earth Observation and Spatial Data Assessment Report

**Target Area:** Thane Creek, Maharashtra, India  
**Role:** Member 3 — Earth Observation / GIS Lead  
**Date:** August 2026

---

## 1. Executive Summary

This report establishes the spatial and temporal foundation for observing the Thane Creek mangrove ecosystem. It documents the identification, selection, and technical metadata of a high-quality, authoritative Earth Observation dataset. This dataset is designated to feed into the Group 2 data pipeline and ultimately support Prakriti's intelligence layer.

## 2. Mission Objective

Establish a robust spatial and temporal foundation for Thane Creek mangrove observation, focusing on:
* Delineation of mangrove boundaries
* Tracking historical extent and spatial change
* Confirming satellite imagery availability
* Identifying relevant remote-sensing indicators
* Establishing standard spatial reference systems
* Ensuring adequate temporal coverage

## 3. Dataset Profile: Global Mangrove Watch (GMW)

The Global Mangrove Watch (GMW) dataset has been selected as the primary spatial reference. It provides an authoritative, globally consistent, and temporally extensive baseline for mangrove observation that fulfills all technical requirements for the Group 2 pipeline.

### 3.1 Source and Access Information
*   **Source / Publisher:** Global Mangrove Watch (a collaborative effort by UNEP-WCMC, Japan 

Source / Publisher	Global Mangrove Watch — a collaboration between UNEP-WCMC, Japan Aerospace Exploration Agency (JAXA), Wetlands International, Aberystwyth University (UK), and solo Earth Observation (soloEO, Japan)
Recommended Data Access — Zenodo (DOI: 10.5281/zenodo.6894273)https://zenodo.org/records/6894273 — hosts all GMW v3.0 vector (shapefile) and raster (GeoTIFF) files directly, valid HTTPS
Interactive Data Portal / Map Explorer	https://www.globalmangrovewatch.org/
JAXA Raster Access	https://www.eorc.jaxa.jp/ALOS/en/dataset/gmw_e.htm
UNEP-WCMC Data Page	https://data.unep-wcmc.org/datasets/45 — ⚠️ as of Aug 2026 this domain is serving an expired/invalid SSL certificate (NET::ERR_CERT_DATE_INVALID); browsers will show a security warning even though the content is legitimate. Use the Zenodo link above instead where possible.
GEO Wetlands Technical Summary	https://geowetlands.org/knowledge-base/datasets/global-mangrove-watch-gmw-v3-0/
License	Creative Commons Attribution 4.0 International (CC BY 4.0) — free to share and adapt with attribution
*   **License:** Open access under Creative Commons Attribution 4.0 International (CC BY 4.0). Data is available for direct download via the UNEP-WCMC portal and Zenodo.

### 3.2 Technical Specifications
*   **Geometry Type:** Vector Polygons (representing mangrove extent).
*   **Coordinate Reference System (CRS):** EPSG:4326 (WGS 84, latitude/longitude).
*   **Spatial Resolution:** 
    *   Standard historical dataset: 25 meters (0.0002 degrees).
    *   Recent iterations (Sentinel-2 derived): 10 meters.
*   **Temporal Coverage:** Multi-decadal time-series spanning from 1996 to 2020. The series includes a baseline year of 2010, with annual updates from 2015 to 2020.

### 3.3 Derived Indicators
*   **Primary Indicator:** Mangrove Extent (spatial distribution and boundary delineation).
*   **Secondary Indicator:** Mangrove Change (quantitative assessment of spatial gain or loss across documented temporal epochs).
*   **Sensor/Methodology:** Extents and changes are derived primarily from L-band Synthetic Aperture Radar (SAR) mosaics.

## 4. Methodological Constraints and Critical Rules

> [!CAUTION]
> **Critical Scientific Constraint:** The observations derived from this dataset represent strictly *mangrove extent and physical radar backscatter characteristics* (which are known to correlate with physical structure or above-ground biomass).
> 
> **Under no circumstances should these raw satellite-derived spatial values (e.g., NDVI, radar backscatter) be interpreted, labeled, or documented as a scientific conclusion regarding "mangrove health" without further localized, contextual ecological analysis and ground-truthing.**
> 
> The observations are strictly limited to structural and spatial dynamics. These observations will serve as foundational spatial inputs to be processed subsequently by Prakriti’s intelligence layer.

## 5. Conclusion and Next Steps

The GMW dataset fulfills all required criteria for the spatial, temporal, and methodological foundations necessary for Thane Creek mangrove observation. It is recommended for immediate integration into the spatial processing pipeline. Ensure all geometries are maintained in EPSG:4326 during initial ingestion before any required local reprojections.
