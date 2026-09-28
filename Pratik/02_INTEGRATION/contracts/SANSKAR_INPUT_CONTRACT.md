# SANSKAR Input Contract Documentation

This document describes SANSKAR's existing input contracts as derived from SANSKAR's FastAPI codebase ([`api.py`](file:///c:/Pratik_Bhuwad/VANA/GROUP2_THANE_CREEK/02_SANSKAR/Sanskar-Integration-main/api.py)).

---

## 1. POST /signal

This is SANSKAR's primary data ingestion endpoint. It is domain-specific to agricultural crop yields and expects an input body conforming to the Pydantic model `SignalInput`.

### Endpoint & Protocol Specifications
*   **Endpoint:** `/signal`
*   **HTTP Method:** `POST`
*   **Base URL & Port:** `http://localhost:8000/signal`
*   **Usability for Group 2 Environmental Contextualisation:** **NO**. The endpoint is domain-specific to agriculture. It forces data through agricultural scoring ranges and generates operational decision/enforcement directives, which violates VANA's semantic validation and decision-boundary rules.

### Request JSON Shape (Pydantic `SignalInput`)
```json
{
  "trace_id": "string",
  "signal": {
    "dataset": "string"
  },
  "contract_version": "string (default: 'v1')"
}
```

### Required Fields
*   `trace_id` (String) — Unique trace tracking identifier.
*   `signal` (Object) — Container object.
*   `signal.dataset` (String) — Valid path to an agricultural crop yield CSV file.
*   `contract_version` (String) — Must be exactly `"v1"`.

### CSV Input Schema Constraints
The target CSV file must contain the following columns:
*   `Region` (String) — Agricultural territory name.
*   `Rainfall_mm` (Float) — Annual precipitation.
*   `Temperature_Celsius` (Float) — Growth temperature.
*   `Irrigation_Used` (Boolean/String: "True"/"False") — Irrigation status.
*   `Fertilizer_Used` (Boolean/String: "True"/"False") — Fertilisation status.
*   `Soil_Type` (String) — Soil classification (e.g., "Loam", "Clay", "Silt").
*   `Weather_Condition` (String) — Weather status (e.g., "Sunny", "Cloudy", "Rainy").
*   `Yield_tons_per_hectare` (Float) — Harvest tonnage.
*   `Days_to_Harvest` (Float) — Duration to harvest.

---

## 2. POST /replay

This endpoint is used to deterministically verify a historical trace transaction.

### Endpoint & Protocol Specifications
*   **Endpoint:** `/replay`
*   **HTTP Method:** `POST`
*   **Base URL & Port:** `http://localhost:8000/replay`
*   **Usability for Group 2 Environmental Contextualisation:** **NO**. It only replays transaction traces that were already stored in memory via `/signal`.

### Request JSON Shape (Pydantic `ReplayInput`)
```json
{
  "trace_id": "string",
  "contract_version": "string (default: 'v1')"
}
```

### Required Fields
*   `trace_id` (String) — Historical trace ID to verify.
*   `contract_version` (String) — Must be exactly `"v1"`.
