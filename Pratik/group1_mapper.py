from typing import Dict, Any

def map_group1_to_group2(group1_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translates raw Group 1 API response structure to Group 2's validation adapter input schema.
    Validates structural completeness and preserves all canonical metrics exactly.
    """
    if not isinstance(group1_payload, dict):
        raise ValueError("Group 1 payload must be a dictionary")

    trace_id = group1_payload.get("trace_id")
    if not trace_id:
        raise ValueError("Missing required root field: 'trace_id'")

    obs_data = group1_payload.get("observation")
    if not obs_data or not isinstance(obs_data, dict):
        raise ValueError("Missing or invalid 'observation' block in Group 1 payload")

    # Required observation-level fields
    required_obs_fields = ["observation_id", "observed_at", "geo_location", "measurements"]
    for field in required_obs_fields:
        if field not in obs_data:
            raise ValueError(f"Missing required field in Group 1 observation: '{field}'")

    obs_id = obs_data["observation_id"]
    if not obs_id or str(obs_id).strip() == "":
        raise ValueError("observation_id cannot be empty")

    # Extract geo_location
    geo_loc = obs_data["geo_location"]
    if not isinstance(geo_loc, dict) or "latitude" not in geo_loc or "longitude" not in geo_loc:
        raise ValueError("Invalid or incomplete 'geo_location' block")

    lat = geo_loc["latitude"]
    lon = geo_loc["longitude"]
    if lat is None or lon is None:
        raise ValueError("Coordinates (latitude, longitude) cannot be null")

    # Extract measurements list
    measurements = obs_data["measurements"]
    if not isinstance(measurements, list) or len(measurements) == 0:
        raise ValueError("measurements must be a non-empty list")

    meas = measurements[0]
    if not isinstance(meas, dict) or "metric_name" not in meas or "value" not in meas or "unit" not in meas:
        raise ValueError("First measurement is missing required parameter, value, or unit fields")

    # Normalize observed_at to ISO-8601 timestamp (e.g. "2026-08-13 09:14:22+00:00" -> "2026-08-13T09:14:22Z")
    observed_at = str(obs_data["observed_at"]).strip()
    normalized_timestamp = observed_at.replace(" ", "T")
    if normalized_timestamp.endswith("+00:00"):
        normalized_timestamp = normalized_timestamp[:-6] + "Z"
    elif not normalized_timestamp.endswith("Z") and "+" not in normalized_timestamp and "-" not in normalized_timestamp[-6:]:
        # If timezone suffix is missing, append Z
        normalized_timestamp += "Z"

    # Map is_synthetic to status
    is_synthetic = obs_data.get("is_synthetic", False)
    status = "SYNTHETIC_TEST" if is_synthetic else "VERIFIED"

    # Assemble mapped Group 2 structure
    mapped = {
        "trace_id": trace_id,
        "observation": {
            "observation_id": obs_id,
            "status": status,
            "measurement": {
                "parameter": meas["metric_name"],
                "value": meas["value"],
                "unit": meas["unit"],
                "method": meas.get("method", "unknown")
            },
            "location": {
                "lat": lat,
                "lon": lon,
                "place_name": geo_loc.get("place_name", "unknown")
            },
            "timestamp": normalized_timestamp
        }
    }

    # Retain geo_id if present
    if "geo_id" in obs_data:
        mapped["observation"]["geo_id"] = obs_data["geo_id"]

    return mapped
