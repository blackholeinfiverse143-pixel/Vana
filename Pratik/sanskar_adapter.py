import re
import copy
import uuid
from typing import Dict, Any, Tuple

class SanskarContextAdapter:
    """
    SANSKAR External Integration Adapter.
    Validates, aligns, and evaluates Thane Creek observations against scientific context baselines
    independently of SANSKAR's agricultural core engine, preserving provenance and immutability.
    """

    def __init__(self):
        self.trace_pattern = re.compile(r"^(TRACE|VANA)-[a-zA-Z0-9]{12}$")

    def validate_payload(self, payload: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates the structure of the input payload against the contextualisation contract.
        """
        if not payload:
            return False, "Empty payload"

        # 1. Trace ID validation
        trace_id = payload.get("trace_id")
        if not trace_id:
            return False, "Missing trace_id"
        if not self.trace_pattern.match(trace_id):
            return False, f"Invalid trace_id format: '{trace_id}'. Must match (TRACE|VANA)-xxxxxxxxxxxx"

        # 2. Observation structure validation
        observation = payload.get("observation")
        if not observation:
            return False, "Missing observation"

        required_obs = ["observation_id", "status", "measurement", "location", "timestamp"]
        for field in required_obs:
            if field not in observation:
                return False, f"Missing required observation field: '{field}'"

        obs_measurement = observation.get("measurement", {})
        required_meas = ["parameter", "value", "unit"]
        for field in required_meas:
            if field not in obs_measurement:
                return False, f"Missing required measurement field: '{field}'"

        # 3. Context structure validation
        context = payload.get("scientific_context")
        if not context:
            # Missing context record is handled, but if context key is entirely missing, return validation error
            return False, "Missing scientific_context object"

        return True, "Valid"

    def is_point_in_polygon(self, lat: float, lon: float, polygon: Dict[str, Any]) -> bool:
        """
        Checks if observation lat/lon falls within the context polygon coordinates.
        Utilizes a simple bounding box calculation derived from polygon coordinates for performance.
        """
        if not polygon or "coordinates" not in polygon:
            return False
        
        try:
            coords = polygon["coordinates"][0]
            lons = [pt[0] for pt in coords]
            lats = [pt[1] for pt in coords]
            min_lon, max_lon = min(lons), max(lons)
            min_lat, max_lat = min(lats), max(lats)
            return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon
        except Exception:
            return False

    def is_date_valid(self, date_str: str, temporal_validity: str) -> bool:
        """
        Validates if the observation date matches the temporal validity range.
        Handles format like 'YYYY-YYYY' or 'YYYY'.
        """
        if not date_str or not temporal_validity:
            return False
        
        try:
            # Extract year from observation date (expects ISO format starting with YYYH)
            obs_year = int(date_str.split("-")[0])
            
            if "-" in temporal_validity:
                start_year, end_year = map(int, temporal_validity.split("-"))
                return start_year <= obs_year <= end_year
            else:
                valid_year = int(temporal_validity)
                return obs_year == valid_year
        except Exception:
            return False

    def resolve_context(self, payload: Dict[str, Any], temporal_ruling: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validates, checks parameters, and resolves the contextual comparison.
        Returns the structured result envelope.
        """
        # Deep copy the input payload to perform immutability assertions later
        original_payload = copy.deepcopy(payload)

        # Basic contract validation
        is_valid, err_msg = self.validate_payload(payload)
        if not is_valid:
            raise ValueError(f"Contract Validation Failed: {err_msg}")

        observation = payload["observation"]
        context = payload["scientific_context"]
        trace_id = payload["trace_id"]

        obs_id = observation["observation_id"]
        obs_meas = observation["measurement"]
        obs_param = obs_meas["parameter"]
        obs_value = obs_meas["value"]
        obs_unit = obs_meas["unit"]
        obs_status = observation["status"]

        # Resolve temporal ruling
        if temporal_ruling is None:
            temporal_ruling = payload.get("temporal_ruling")

        # If no temporal ruling is provided, or the ruling is not ALLOW, it is a GAP
        has_allow_ruling = (temporal_ruling is not None and temporal_ruling.get("ruling") == "ALLOW")

        # Check for Kaushlendra's context availability or temporal GAP ruling
        is_context_gap = (
            not context or 
            context.get("status") == "GAP" or 
            context.get("validation_status") == "GAP" or
            context.get("context_id") == "WAITING_FOR_VERIFIED_CONTEXT" or
            not context.get("context_id") or
            not has_allow_ruling
        )

        obs_loc = observation.get("location", {})
        lat = obs_loc.get("lat", 0.0)
        lon = obs_loc.get("lon", 0.0)

        if is_context_gap:
            ctx_id = context.get("context_id") if (context and context.get("context_id")) else "WAITING_FOR_VERIFIED_CONTEXT"
            validation_status = context.get("validation_status") if (context and context.get("validation_status")) else "GAP"
            
            # Extract citation and provenance details if context is available
            source_id = context.get("source_doi") or context.get("source_id") if context else "WAITING_FOR_VERIFIED_CONTEXT"
            citation = context.get("citation") or context.get("source_citation") if context else "WAITING_FOR_VERIFIED_CONTEXT"
            confidence = context.get("confidence_score") if (context and context.get("confidence_score") is not None) else 0.0

            envelope = {
                "observation": {
                    "observation_id": obs_id,
                    "parameter": obs_param,
                    "value": obs_value,
                    "unit": obs_unit,
                    "timestamp": observation.get("timestamp"),
                    "location": {
                        "lat": lat,
                        "lon": lon
                    }
                },
                "provenance": {
                    "source_id": source_id,
                    "citation": citation,
                    "verification_status": validation_status,
                    "source_url": context.get("source_url") if context else None,
                    "confidence": confidence,
                    "quality": context.get("quality") if context else None,
                    "uncertainty": context.get("uncertainty") if context else None
                },
                "scientific_context": {
                    "context_id": ctx_id,
                    "parameter_name": obs_param,
                    "validation_status": validation_status
                },
                "contextual_result": {
                    "status": "WAITING_FOR_VERIFIED_CONTEXT",
                    "parameter_evaluated": obs_param,
                    "reference_value": None,
                    "deviation": None,
                    "anomaly_detected": None,
                    "assessment": None,
                    "action_eligibility": False,
                    "abstention_required": True
                },
                "trace": {
                    "trace_id": trace_id
                },
                "action_request": None,
                "observation_mutated": False,
                "action_eligibility": False,
                "abstention_required": True
            }
            if "geo_id" in observation:
                envelope["observation"]["geo_id"] = observation["geo_id"]
            # Assert immutability of the primary input payload
            assert payload == original_payload, "Assertion Failed: Primary input payload was mutated during adapter execution!"
            return envelope

        # 1a. Observation identity mismatch validation
        ctx_obs_id = context.get("observation_id")
        if ctx_obs_id and ctx_obs_id != obs_id:
            raise ValueError(f"Observation ID mismatch rejection: observation '{obs_id}' does not match context target '{ctx_obs_id}'")

        # 1. Missing citation validation
        citation = context.get("source_citation") or context.get("citation")
        if not citation or str(citation).strip() == "":
            raise ValueError("Context resolution rejected: scientific_context is missing a citation")

        # 2. Parameter alignment check
        ctx_param = context.get("parameter_name") or context.get("parameter")
        param_match = obs_param == ctx_param or ctx_param == f"expected_{obs_param}" or ctx_param == f"baseline_{obs_param}"
        if not param_match:
            raise ValueError(f"Parameter mismatch rejection: observation parameter '{obs_param}' does not match context parameter '{ctx_param}'")

        # 2a. Scientific DOI conflict validation
        source_doi = context.get("source_doi") or context.get("source_id")
        if obs_param in ["canopy_height", "biomass"]:
            if source_doi == "10.5281/zenodo.6894273":
                raise ValueError(
                    f"DOI conflict rejection: Zenodo DOI '10.5281/zenodo.6894273' is strictly "
                    f"assigned for spatial extent metadata, and cannot be used for '{obs_param}' scientific attributes."
                )
            elif source_doi and str(source_doi).startswith("10.") and source_doi != "10.1016/j.rsma.2023.103207":
                raise ValueError(
                    f"DOI conflict rejection: DOI '{source_doi}' is not the authoritative citation for '{obs_param}' scientific attributes."
                )

        # 3. Unit compatibility check
        ctx_unit = context.get("unit")
        if isinstance(context.get("parameter_value"), dict):
            ctx_unit = context.get("parameter_value", {}).get("unit") or ctx_unit
        if obs_unit != ctx_unit:
            raise ValueError(f"Unit mismatch rejection: observation unit '{obs_unit}' does not match context unit '{ctx_unit}'")

        # 4. Spatial validation
        polygon = context.get("location_polygon", {})
        spatial_match = self.is_point_in_polygon(lat, lon, polygon)

        # 5. Temporal validation (only when temporal validity is actually available)
        obs_date = observation["timestamp"]
        valid_range = context.get("temporal_validity", "")
        valid_from = context.get("valid_from")
        valid_to = context.get("valid_to")

        if valid_range:
            temporal_match = self.is_date_valid(obs_date, valid_range)
        elif valid_from or valid_to:
            temporal_match = True
            if valid_from:
                temporal_match = temporal_match and (obs_date >= valid_from)
            if valid_to:
                temporal_match = temporal_match and (obs_date <= valid_to)
        else:
            temporal_match = True

        # Compute contextual metrics
        ctx_val_raw = context.get("parameter_value", {}) if isinstance(context.get("parameter_value"), dict) else context.get("value", {})
        min_val = None
        max_val = None
        mean_val = None

        if isinstance(ctx_val_raw, dict):
            mean_val = ctx_val_raw.get("value") or ctx_val_raw.get("mean")
            if "range" in ctx_val_raw and isinstance(ctx_val_raw["range"], list) and len(ctx_val_raw["range"]) == 2:
                min_val = ctx_val_raw["range"][0]
                max_val = ctx_val_raw["range"][1]
            else:
                min_val = ctx_val_raw.get("min")
                max_val = ctx_val_raw.get("max")

        anomaly_detected = False
        deviation_str = "Within expected range"

        if min_val is not None and max_val is not None:
            if obs_value < min_val:
                anomaly_detected = True
                diff = min_val - obs_value
                deviation_str = f"Below baseline minimum by {round(diff, 2)} {obs_unit}"
            elif obs_value > max_val:
                anomaly_detected = True
                diff = obs_value - max_val
                deviation_str = f"Above baseline maximum by {round(diff, 2)} {obs_unit}"
        elif mean_val is not None:
            diff = obs_value - mean_val
            deviation_str = f"Deviation from mean: {round(diff, 2)} {obs_unit}"
            if abs(diff) / mean_val > 0.25: # Arbitrary threshold for anomaly if no bounds
                anomaly_detected = True

        # Determine contextual status (ALLOW or ADAPT) and eligibility
        if anomaly_detected or not spatial_match or not temporal_match:
            context_status = "ADAPT"
            action_eligibility = False
            abstention_required = True
            action_request_val = None
        else:
            context_status = "ALLOW"
            action_eligibility = True
            abstention_required = False
            action_request_val = {
                "action_request_id": f"req-{uuid.uuid5(uuid.NAMESPACE_DNS, f'{trace_id}:{obs_id}')}",
                "observation_id": obs_id,
                "context_id": context.get("context_id"),
                "context_status": context_status,
                "scientific_source_reference": citation,
                "requested_capability": "ENVIRONMENTAL_CONTEXTUALISATION",
                "requested_action": context_status,
                "semantic_contract_version": payload.get("contract_version") or "v1",
                "provenance_reference": context.get("source_doi") or context.get("source_id") or "N/A",
                "trace_id": trace_id
            }

        # Assemble the final contextual result envelope matching Sakshi's schema
        envelope = {
            "observation": {
                "observation_id": obs_id,
                "parameter": obs_param,
                "value": obs_value,
                "unit": obs_unit,
                "timestamp": obs_date,
                "location": {
                    "lat": lat,
                    "lon": lon
                }
            },
            "provenance": {
                "source_id": context.get("source_doi") or context.get("source_id"),
                "citation": citation,
                "verification_status": context.get("validation_status") or context.get("verification_status", "PENDING"),
                "source_url": context.get("source_url"),
                "confidence": context.get("confidence_score") if context.get("confidence_score") is not None else context.get("confidence", 0.0),
                "quality": context.get("quality"),
                "uncertainty": context.get("uncertainty")
            },
            "scientific_context": {
                "context_id": context.get("context_id"),
                "parameter_name": ctx_param,
                "validation_status": context.get("validation_status") or context.get("verification_status", "PENDING")
            },
            "contextual_result": {
                "status": "SUCCESS",
                "parameter_evaluated": obs_param,
                "reference_value": mean_val,
                "deviation": deviation_str,
                "anomaly_detected": anomaly_detected,
                "assessment": deviation_str,
                "spatial_match": spatial_match,
                "temporal_match": temporal_match,
                "action_eligibility": action_eligibility,
                "abstention_required": abstention_required
            },
            "trace": {
                "trace_id": trace_id
            },
            "action_request": action_request_val,
            "observation_mutated": False,
            "action_eligibility": action_eligibility,
            "abstention_required": abstention_required
        }

        if "geo_id" in observation:
            envelope["observation"]["geo_id"] = observation["geo_id"]

        # Assert immutability of the primary observation
        assert payload == original_payload, "Assertion Failed: Primary input payload was mutated during adapter execution!"

        return envelope

def fetch_and_generate_context(observation_id: str, context_payload: Dict[str, Any], client) -> Dict[str, Any]:
    """
    Orchestrates the entire live integration pipeline:
    1. Retrieves canonical observation from live API client
    2. Maps Group 1 schema to Group 2 input contract
    3. Loads the authoritative temporal ruling
    4. Resolves context against baseline registry using SanskarContextAdapter
    """
    # Fetch raw Group 1 observation
    raw_g1 = client.get_observation(observation_id)
    
    # Map to Group 2 input format
    from group1_mapper import map_group1_to_group2
    g2_payload = map_group1_to_group2(raw_g1)
    
    # Inject the scientific context into mapped payload
    g2_payload["scientific_context"] = context_payload
    
    # Load temporal ruling if available
    import os
    import json
    temporal_ruling = None
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ruling_path = os.path.join(base_dir, "01_SOURCE_ARTIFACTS", "KAUSHLENDRA", "temporal_applicability_ruling.json")
    if os.path.exists(ruling_path):
        try:
            with open(ruling_path, "r") as f:
                temporal_ruling = json.load(f)
        except Exception:
            pass
            
    # Resolve using adapter
    adapter = SanskarContextAdapter()
    return adapter.resolve_context(g2_payload, temporal_ruling=temporal_ruling)
