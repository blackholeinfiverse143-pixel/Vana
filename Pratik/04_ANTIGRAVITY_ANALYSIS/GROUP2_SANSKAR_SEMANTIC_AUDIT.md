# SANSKAR Semantic Audit Report

This report presents a thorough semantic and architectural validation of the SANSKAR pipeline against the scientific requirements of the VANA / PRAKRITI Thane Creek Mangrove Baseline.

---

## 1. SANSKAR Semantics Verification (Task 1)

The following table evaluates whether the input schema in [`sanskar.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/02_SANSKAR/Sanskar-Integration-main/sanskar.py) can legitimately accept Thane Creek environmental observations.

| SANSKAR Field | Actual Meaning | Used in Calculation | Thane Creek Equivalent | Valid Mapping? | Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`Region`** | Geographic division of candidates. | Groups data during aggregation: `df.groupby("Region")`. | Station Name (e.g., `Station I`) | **YES** | `sanskar.py` line 100. Maps textual place keys correctly. |
| **`Rainfall_mm`** | Annual/monthly precipitation depth. | Scaled as `(x - 100) / 900` to yield `rainfall_score` (weight `0.15`). | Mapped to Chlorides (%) or Salinity (ppt). | **NO** | `sanskar.py` lines 52, 59. Salinity/chloride values fall outside expected precipitation scaling ranges (`[100, 1000]`). Forcing them here creates zero scores or division discrepancies. |
| **`Temperature_Celsius`** | Ambient growth temperature. | Deviation scaled: `1 - abs(x - 25) / 15` for `temp_score` (weight `0.12`). | Mapped to Sediment pH. | **NO** | `sanskar.py` lines 53, 60. pH is logarithmic and alkaline (7–8), not linear thermal. Formula would interpret pH 7.5 as a freezing temperature (yielding 0 score). |
| **`Irrigation_Used`** | Managed water input. | High score flag: `1.0` if true, `0.35` if false for `irrigation_score` (weight `0.18`). | Mapped to Wastewater Exposure. | **NO** | `sanskar.py` lines 54, 61. Irrigation is a resource asset; wastewater inflow is an environmental stressor and pollutant. Treating them as equivalent violates semantic truth. |
| **`Fertilizer_Used`** | Controlled soil nutrient replenishment. | High score flag: `1.0` if true, `0.35` if false for `fertilizer_score` (weight `0.08`). | Mapped to Nutrient Accumulation. | **NO** | `sanskar.py` lines 55, 62. Fertilizers promote crop growth; sewage-derived eutrophication causes macrofaunal mortality. Mappings confuse stress with nourishment. |
| **`Soil_Type`** | Soil texture class (Loam, Clay, Peaty, etc.). | Scored via dict lookup for `soil_quality_score` (weight `0.10`). | Mapped to Substrate Texture (Sand/Silt/Clay). | **NO** | `sanskar.py` lines 56, 66–74. Clay/sand are penalized in the map (`0.90` / `0.85`), whereas clayey and peaty mudflats are highly productive native estuarine substrates. |
| **`Weather_Condition`** | Atmospheric conditions (Sunny, Cloudy, Rainy). | Scored via dict lookup for `weather_score` (weight `0.09`). | Mapped to Seasonal status. | **NO** | `sanskar.py` lines 57, 76–81. Monsoonal precipitation is penalized as "Rainy" (0.88) compared to "Sunny" (0.95), yet monsoon fresh water input is vital for reducing mangrove hypersalinity. |
| **`Yield_tons_per_hectare`** | Weight of harvested crop per area. | Divided by days to get yield efficiency (weight `0.28`). | Mapped to Organic Carbon (%). | **NO** | `sanskar.py` lines 63–64. Estuarine sediment organic carbon accumulation is a biogeochemical sink, not a seasonal harvest yield. |
| **`Days_to_Harvest`** | Crop maturity duration. | Divisor for yield efficiency. | Mapped to Study Duration (months). | **NO** | `sanskar.py` lines 63–64. Dividing organic carbon by study duration produces an arbitrary mathematical rate with no ecological meaning. |

---

## 2. Canonical Observation Verification (Task 2)

Based on Group 1's [`schema.sql`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/01_SOURCE_ARTIFACTS/ANSH/schema.sql) and [`demo_pipeline.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/01_SOURCE_ARTIFACTS/ANSH/demo_pipeline.py), the actual canonical observation fixture is structured as follows:

*   **`observation_id`:** `OBS-THANECREEK-AGB-2023-01` (Uniquely identifies the observation instance).
*   **`dataset_id`:** `DS-THANECREEK-CARBONSTOCK-2023-01` (Traces the observation to a defined dataset version).
*   **`geo_id`:** `GEO-THANECREEK-01` (Links to coordinates: `19.2183` N, `72.9781` E).
*   **`measurement_id`:** `MEAS-THANECREEK-AGB-ALLOM-01` / `MEAS-THANECREEK-AGB-INTEG-01` (Holds the actual quantitative value `84.83 Mg/ha` / `111.31 Mg/ha` and metric name `above_ground_biomass`).
*   **`source_id`:** `SRC-THANECREEK-2023-CARBONSTOCK-01` (Links back to the authoritative citation in the source registry).
*   **`context_id`:** **NONE**. The database schema in `schema.sql` does **not** contain a `context_id` column or table.

---

## 3. Scientific Context Verification (Task 3)

The scientific context record fixture defined in [`SCIENCE_CONTEXT_MODEL.md`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/01_SOURCE_ARTIFACTS/KAUSHLENDRA/SCIENCE_CONTEXT_MODEL.md) is:
*   **Context ID:** `ctx-9876-abcd-1234`
*   **Parameter:** `baseline_salinity`
*   **Value:** `{"min": 15.0, "max": 35.0, "mean": 28.5}`
*   **Unit:** `ppt`
*   **Location Polygon:** Coordinates covering central Thane Creek `[[[72.95, 19.10], ...]]`
*   **Temporal Validity:** `2020-2023`
*   **Source / Citation:** `Thane Creek Environmental Assessment Report, MMRDA, 2023.`
*   **Confidence Score:** `0.85`
*   **Validation Status:** `VERIFIED`

### Semantic Mismatch Verdict
The context record parameter (`baseline_salinity` measured in `ppt`) **does not match** the parameters of either of the canonical observation fixtures:
1.  Group 1 Ingested Observation: `above_ground_biomass` measured in `Mg/ha`.
2.  Group 2 Baseline JSON Observation: `mangrove_forest_extent` measured in `sq km`.

No context record exists in the folder structure that genuinely matches these parameters.

---

## 4. SANSKAR Contract Capability Verification (Task 4)

> [!WARNING]  
> **SANSKAR current /signal contract is domain-specific and cannot safely consume this scientific observation without contract adaptation.**

Forcing Thane Creek benthos observations or carbon metrics into the agricultural CSV schema (`Rainfall_mm`, `Fertilizer_Used`, etc.) requires a semantic reinterpretation that violates VANA's core ground rules. Doing so would write misleading, scientifically invalid mappings into SANSKAR's audit logs, breaking the chain of provenance.

---

## 5. Decision / Enforcement Boundary Check (Task 5)

*   **Execution Flow:** Yes, in SANSKAR's [`api.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/02_SANSKAR/Sanskar-Integration-main/api.py), the `/signal` endpoint is hardcoded to execute sequentially:
    `run_sanskar` $\rightarrow$ `run_core` $\rightarrow$ `run_enforcement` $\rightarrow$ `truth_output`.
*   **Operational Decision Bypassing:** There is **no existing supported way** to obtain contextual output from SANSKAR without executing the operational decision (`core`) and enforcement stages.
*   **Boundary Violation:** The core and enforcement stages output agricultural decisions (e.g., allocating irrigation or deploying fertilizer to Station I). Exposing a scientific contextualisation result (such as an organic carbon anomaly) as an operational agricultural action violates the separation between scientific context and administrative execution.

---

## 6. Conceptual Result Envelope Design (Task 6)

To preserve provenance and context without mutating the observation or invoking mock decisions, the target envelope is conceptually designed as:

```json
{
  "observation_id": "OBS-THANECREEK-AGB-2023-01",
  "context_id": "ctx-9876-abcd-1234",
  "source_id": "TCM-LIT-WQ-2016-001",
  "citation": "Pachpande, S. & Pejaver, M. (2016). Impact of Water Released from STP on Macrofaunal Diversity...",
  "confidence": 0.85,
  "uncertainty": "Medium (based on abstract and partial extraction verification)",
  "contextual_result": {
    "parameter_evaluated": "sediment_organic_carbon",
    "measured_value": 2.85,
    "historical_baseline_mean": 1.98,
    "deviation": "+0.87%",
    "anomaly_detected": true,
    "ecological_assessment": "Organic enrichment observed at Station I relative to reference Station II"
  },
  "observation_mutated": false
}
```

---

## 7. MasterDB Configuration Status (Task 7)

*   **MasterDB Accessibility:** **NOT ACCESSIBLE**. There is no network path or active credentials to a production PostgreSQL database.
*   **PostgreSQL URL:** None exists in the environment or configurations.
*   **Local Databases:** The local `.db` files (`vana_demo.db` and `vana_demo_corrected.db`) are strictly **local SQLite fixtures** used for proof-of-concept testing.
*   **Observation Interface:** Group 1 has not provided any other API or network interface for canonical observations.

---

## 8. Final Integration Decision (Task 8)

### C. SANSKAR CONTRACT IS DOMAIN-MISMATCHED AND MUST BE ADAPTED

#### Smallest Architectural Change Required:
1.  **Add a new API Endpoint (`/context/resolve`):** Implement this endpoint in SANSKAR's [`api.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/02_SANSKAR/Sanskar-Integration-main/api.py). It must accept the structured JSON payload containing the observation and the context record.
2.  **Implement a Scientific Contextualisation Service:** Create a new module (e.g. `scientific_context.py` or a dedicated function inside `sanskar.py`) that compares the observation's measured values (e.g., pH, organic carbon) against the context record's thresholds (min/max/mean) to compute deviation scores.
3.  **Bypass Core and Enforcement Stages:** Ensure that queries hitting `/context/resolve` do **not** call `run_core` or `run_enforcement`. It must return the result directly within the conceptual result envelope.
4.  **Trace Continuity Integration:** Ensure that `/context/resolve` continues to register trace hashes via `verify_trace_continuity` to maintain compatibility with TANTRA and the audit log.
