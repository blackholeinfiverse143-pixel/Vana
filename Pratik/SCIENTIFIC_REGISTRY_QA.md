# Scientific Source Registry QA Report

This report presents a Quality Assurance (QA) audit of [`Scientific_Source_Registry_V0.1.xlsx`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/Scientific_Source_Registry_V0.1.xlsx). It systematically evaluates the authenticity, completeness, metadata quality, and extraction status of all registered literature sources and their associated observations.

---

## 1. Overall Registry Summary

*   **Total Sources Registered:** 13
*   **Total Observations Extracted:** 19 (spread across 9 of the 13 sources)
*   **Unique Source IDs?** Yes, all source IDs are unique and structured.
*   **Primary/Secondary Evidences Distinguished?** Yes, the registry distinguishes between primary studies, spatial derivations, model studies, and secondary review syntheses.
*   **Core Mismatches Found:** 
    *   **ID Mismatch:** The 2023 carbon stock study has ID `TCM-LIT-CARB-2023-001` in the registry, but the demo pipeline uses `SRC-THANECREEK-2023-CARBONSTOCK-01`.
    *   **Value/Parameter Mismatch:** The registry extracts `Mean total carbon stock` as `116.58` and `127.89` Mg C ha⁻¹, but the demo pipeline ingests `above_ground_biomass` as `84.83` and `111.31` Mg/ha.
    *   **Baseline JSON Source Missing:** The source `SRC_GOVT_MFD_001` (Maharashtra Forest Department & ISRO Mangrove Cell Report 2020) used in the baseline JSON is completely missing from the Excel registry.

---

## 2. Source-by-Source QA Classification

### ACCEPTED
*These sources are real, have complete metadata, and their observations are fully extracted.*

1.  **`TCM-LIT-CARB-2010-001`** (Chaudhari & Pejaver, 2010)
    *   *Type:* Conference paper
    *   *Parameters:* Sediment organic carbon, pH, moisture, leaf OC, macrobenthos OC.
    *   *Temporal Scope:* Nov 2009 - Oct 2010 (Complete)
    *   *Geographic Scope:* Bhandup and Airoli, Thane Creek (four substations)
    *   *Observations Extracted:* `TCM-OBS-2010-001` through `TCM-OBS-2010-005` (sediment pH, moisture, OC, and depth-resolved OC).
2.  **`TCM-LIT-CARB-2015-001`** (Chaudhari Pachpande & Pejaver, 2015)
    *   *Type:* Journal article
    *   *Parameters:* Above-ground biomass, below-ground biomass, carbon content of *Avicennia marina var. accutissima*.
    *   *Temporal Scope:* May 2010 - Apr 2011 (Complete)
    *   *Geographic Scope:* Thane Creek, Maharashtra
    *   *Observations Extracted:* `TCM-OBS-2015-001` and `TCM-OBS-2015-002` (above and below ground biomass).
3.  **`TCM-LIT-BIOD-2016-001`** (Chaudhari-Pachpande & Pejaver, 2016)
    *   *Type:* Journal short communication
    *   *Parameters:* Bird species diversity, IUCN status, foraging category.
    *   *Temporal Scope:* 2009-2011 (Complete)
    *   *Geographic Scope:* Thane Creek (two study locations, ~6 km investigated)
    *   *Observations Extracted:* `TCM-OBS-2016-001` (95 bird species recorded).
4.  **`TCM-LIT-SPAT-2022-001`** (Azeez et al., 2022)
    *   *Type:* Journal research article
    *   *Parameters:* Mangrove area, species distribution, tidal current velocity, sediment deposition.
    *   *Temporal Scope:* 1990-2017; species mapping in 2017 (Complete)
    *   *Geographic Scope:* Thane Creek, Mumbai
    *   *Observations Extracted:* `TCM-OBS-2022-001` (area 79.14 -> 154.5 km²) and `TCM-OBS-2022-002` (model-derived tidal-current attenuation of ~80%).
5.  **`TCM-LIT-CARB-2023-001`** (Singh et al., 2023)
    *   *Type:* Journal research article
    *   *Parameters:* Above-ground biomass, carbon stock, NDVI, standing carbon stock.
    *   *Temporal Scope:* Field study, publication 2023 (Complete)
    *   *Geographic Scope:* Thane Creek (10 stations along both banks)
    *   *Observations Extracted:* `TCM-OBS-2023-001` (116.58 Mg C ha⁻¹) and `TCM-OBS-2023-002` (127.89 Mg C ha⁻¹).
6.  **`TCM-LIT-SPAT-2023-001`** (Adluri et al., 2023)
    *   *Type:* Journal research communication
    *   *Parameters:* Creek width, mangrove cover, bank-to-bank area.
    *   *Temporal Scope:* 1972-2020; cover analysis 2005-2020 (Complete)
    *   *Geographic Scope:* Thane Creek, Maharashtra
    *   *Observations Extracted:* `TCM-OBS-2023-003` (mangrove cover increase of 14.1 km²) and `TCM-OBS-2023-004` (creek width reduction at mouth of 1.15 km).
7.  **`TCM-LIT-SPAT-2024-001`** (Parmar & Chakraborty, 2024)
    *   *Type:* Journal article
    *   *Parameters:* Mangrove cover, NDVI, density, land-cover classes.
    *   *Temporal Scope:* 1993-2023 (Complete)
    *   *Geographic Scope:* Thane Creek Ramsar Site region
    *   *Observations Extracted:* `TCM-OBS-2024-001` (extent 12.623 -> 23.516 km²) and `TCM-OBS-2024-002` (density 0.1921 -> 0.3579 dimensionless).

---

### UNCERTAIN
*These sources are bibliographically verified, but have critical metadata gaps or missing numerical parameters.*

8.  **`TCM-LIT-WQ-2015-001`** (Chaudhari Pachpande, Pejaver & Gholba, 2015)
    *   *Type:* Conference paper
    *   *Temporal Scope:* `Not established`
    *   *Observations Extracted:* `TCM-OBS-WQ-2015-001` (indicates physicochemical parameters studied but numerical values are missing: `"numerical results are not yet extracted"`).
    *   *Uncertainty:* Missing temporal scope and raw/normalised quantitative values.
9.  **`TCM-LIT-WQ-2016-001`** (Pachpande & Pejaver, 2016)
    *   *Type:* Conference paper
    *   *Temporal Scope:* `Not established`
    *   *Observations Extracted:* `TCM-OBS-WQ-2016-001` (sewage discharge macrofaunal diversity scope; notes: `"numerical values not yet extracted"`).
    *   *Uncertainty:* Missing temporal scope and raw/normalised macrofaunal diversity metrics.

---

### MISSING
*Authoritative sources listed in the sheets but whose actual observations have NOT been extracted.*

10. **`TCM-LIT-BIOD-2001-001`** (Goldin I. Quadros, 2001 PhD Thesis)
    *   *Type:* PhD Thesis, University of Mumbai
    *   *Temporal Scope:* `Thesis study period to be extracted from full thesis`
    *   *Observations Extracted:* **None** (No observation rows exist in the `Scientific Observations` sheet).
    *   *Status:* Missing extraction. Full thesis PDF is available via Ramsar link but needs to be systematically read and populated.

---

### REQUIRES_EXTERNAL_VERIFICATION
*These sources represent review articles or unlocated literature where original primary data must be fetched and verified before extraction.*

11. **`TCM-LIT-POLL-2006-001`** (Chavan, Lokhande & Rajput, 2006)
    *   *Type:* Journal article (Physicochemical & organic pollutants)
    *   *Verification status:* Verified bibliographically only. Full paper was not accessed. No observations are extracted in the observations sheet.
12. **`TCM-LIT-CONS-2008-001`** (Nikam, Kumar, Lalla & Gupta, 2008)
    *   *Type:* Conference proceeding (Conservation of wetlands)
    *   *Verification status:* Secondary synthesis compiling prior studies. No primary observations extracted. Primary papers cited within this proceeding must be traced and verified.
13. **`TCM-LIT-POLL-2025-001`** (Corbett et al., 2025)
    *   *Type:* Critical review
    *   *Verification status:* Synthesis layer of water quality, sediment, and contamination. No primary observations extracted. Individual measurements must be traced back to the cited primary studies.

---

## 3. Literature Gaps & Leads (Sheet Summary)

The registry identifies several critical bibliographic leads that are currently unverified:

1.  **Sheetal Pachpande PhD Thesis on Carbon Sequestration (Mumbai University):**
    *   *Status:* **CLAIM ONLY / NOT SOURCE-VERIFIED** (No thesis document located; only ResearchGate profile mention).
    *   *Action:* Locate the thesis PDF to unify Sheetalji's carbon research.
2.  **STP discharge macrofaunal diversity paper (Sheetalji):**
    *   *Status:* **MISSING** (Full text not located).
3.  **Borkar Mangala (2004) Thesis on Mangrove Ecology:**
    *   *Status:* **BIBLIOGRAPHIC LEAD** (Cited in Sheetalji's 2010 paper; document unlocated).
4.  **Athalye R.P. (1988) Thesis on Macrobenthos:**
    *   *Status:* **BIBLIOGRAPHIC LEAD** (Cited in Sheetalji's 2010 paper; document unlocated).
