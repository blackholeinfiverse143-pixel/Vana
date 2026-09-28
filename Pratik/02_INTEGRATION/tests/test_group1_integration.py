import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import requests
import copy

# Adjust paths to import client, mapper, and adapter
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "adapter"))
from group1_client import Group1ApiClient, Group1ApiClientError, ObservationNotFoundError, MalformedResponseError
from group1_mapper import map_group1_to_group2
from sanskar_adapter import SanskarContextAdapter, fetch_and_generate_context

class TestGroup1Integration(unittest.TestCase):
    def setUp(self):
        self.observation_id = "TC-Z03-F02-LIDAR-OBS001"
        self.trace_id = "VANA-27b28525d736"
        self.temporal_ruling = {"ruling": "ALLOW"}
        
        # Raw API response mock from Group 1 API
        self.raw_api_response = {
            "trace_id": self.trace_id,
            "observation_id": self.observation_id,
            "status": "RETRIEVED",
            "observation": {
                "observation_id": self.observation_id,
                "dataset_id": "DS-GROUP3-TC-Z03-F02",
                "geo_id": "GEO-53675e636907d076866516affbc285cc",
                "observed_at": "2026-08-13 09:14:22+00:00",
                "capture_method": "aerial",
                "species": None,
                "observation_type": "canopy_height",
                "quality_status": "VALIDATED",
                "confidence": None,
                "is_synthetic": False,
                "geo_location": {
                    "place_name": "Group 3 observation location",
                    "latitude": 19.1288,
                    "longitude": 72.9421,
                    "altitude_m": None,
                    "crs": "EPSG:4326"
                },
                "field_observation_meta": {
                    "device_id": "G3-LIDAR-001",
                    "operator": "Tester",
                    "mission_id": "TC-Z03-F02",
                    "accuracy": None,
                    "accuracy_unit": None,
                    "accuracy_status": "NOT_VERIFIED",
                    "calibration_status": "NOT_VERIFIED",
                    "gnss_status": None,
                    "position_accuracy_m": None,
                    "processing_status": "chm_derived",
                    "notes": None
                },
                "measurements": [
                    {
                        "measurement_id": "MEAS-4e832a718b483b2323e9dedf348472ed",
                        "metric_name": "canopy_height",
                        "data_type": "NUMERIC",
                        "value": 4.7,
                        "value_text": None,
                        "unit": "m",
                        "method": "aerial",
                        "provenance": {
                            "provenance_id": "PROV-5fc011feefc21de643dda02ccbd1f68f",
                            "source_id": "SRC-GROUP3-SYNTHETIC",
                            "run_id": "RUN-a081ed1b4219c36e35d6d5d756520a63",
                            "derivation_note": "Group 3 V2.1 observation ingested through consumer-facing API."
                        }
                    }
                ],
                "raw_artifacts": [
                    {
                        "artifact_id": "ART-061f7c326c746613ec2a9d36f914fb02",
                        "artifact_type": "point_cloud",
                        "storage_ref": "TC-Z03-F02/drone/pointcloud_F02_001.las",
                        "content_hash": "f7254999689ae5b530a0006d0fb6765df0317973504e8c5d1b393bfa5826cf9d",
                        "hash_algorithm": "sha256",
                        "captured_at": "2026-08-13 09:14:22+00:00"
                    }
                ]
            }
        }

        # Valid Context (Ansh's frozen structure, with two DOIs separate)
        self.context_payload = {
            "context_id": "ctx-tc-001",
            "parameter_name": "expected_canopy_height",
            "parameter_value": {
                "min": 3.5,
                "max": 6.5,
                "mean": 4.8
            },
            "unit": "m",
            "location_polygon": {
                "type": "Polygon",
                "coordinates": [
                    [[72.93, 19.00], [73.02, 19.00], [73.02, 19.15], [72.93, 19.15], [72.93, 19.00]]
                ]
            },
            "temporal_validity": "2020-2028",
            "source_id": "10.1016/j.rsma.2023.103207",  # Study DOI
            "source_doi": "10.1016/j.rsma.2023.103207",
            "spatial_reference_doi": "10.5281/zenodo.6894273",  # Spatial DOI
            "citation": "ScienceDirect / Elsevier (2023) — \"Standing carbon stock of Thane Creek mangrove ecosystem, Maharashtra, India\"",
            "verification_status": "VERIFIED",
            "confidence_score": 0.85,
            "quality": "VALIDATED",
            "uncertainty": None
        }

    # 1. Live Group 1 Response Mapping
    def test_group1_response_mapping(self):
        mapped = map_group1_to_group2(self.raw_api_response)
        
        self.assertEqual(mapped["trace_id"], self.trace_id)
        self.assertEqual(mapped["observation"]["observation_id"], self.observation_id)
        self.assertEqual(mapped["observation"]["status"], "VERIFIED")
        
    # 2. Observation ID preservation
    def test_observation_id_preservation(self):
        mapped = map_group1_to_group2(self.raw_api_response)
        self.assertEqual(mapped["observation"]["observation_id"], self.observation_id)

    # 3. Canonical Timestamp preservation
    def test_canonical_timestamp_preservation(self):
        mapped = map_group1_to_group2(self.raw_api_response)
        self.assertEqual(mapped["observation"]["timestamp"], "2026-08-13T09:14:22Z")

    # 4. Coordinate preservation
    def test_coordinate_preservation(self):
        mapped = map_group1_to_group2(self.raw_api_response)
        self.assertEqual(mapped["observation"]["location"]["lat"], 19.1288)
        self.assertEqual(mapped["observation"]["location"]["lon"], 72.9421)

    # 5. Measurement mapping
    def test_measurement_mapping(self):
        mapped = map_group1_to_group2(self.raw_api_response)
        meas = mapped["observation"]["measurement"]
        self.assertEqual(meas["parameter"], "canopy_height")
        self.assertEqual(meas["value"], 4.7)
        self.assertEqual(meas["unit"], "m")
        self.assertEqual(meas["method"], "aerial")

    # 6. Group 1 404 handling
    @patch("requests.get")
    def test_group1_404_handling(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        client = Group1ApiClient()
        with self.assertRaises(ObservationNotFoundError):
            client.get_observation("NON-EXISTENT")

    # 7. Network failure handling
    @patch("requests.get")
    def test_network_failure_handling(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")
        
        client = Group1ApiClient()
        with self.assertRaises(Group1ApiClientError):
            client.get_observation(self.observation_id)

    # 8. Malformed JSON handling
    @patch("requests.get")
    def test_malformed_json_handling(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("JSONDecodeError")
        mock_get.return_value = mock_response
        
        client = Group1ApiClient()
        with self.assertRaises(MalformedResponseError):
            client.get_observation(self.observation_id)

    # 9. Malformed observation structure
    def test_malformed_observation_structure(self):
        malformed = copy.deepcopy(self.raw_api_response)
        del malformed["observation"]["geo_location"]
        with self.assertRaises(ValueError) as context:
            map_group1_to_group2(malformed)
        self.assertIn("geo_location", str(context.exception))

    # 10. Unsupported parameter
    def test_unsupported_parameter(self):
        adapter = SanskarContextAdapter()
        payload = map_group1_to_group2(self.raw_api_response)
        payload["scientific_context"] = copy.deepcopy(self.context_payload)
        payload["temporal_ruling"] = self.temporal_ruling
        
        # Modify parameter to mismatched value
        payload["observation"]["measurement"]["parameter"] = "soil_pH"
        with self.assertRaises(ValueError) as context:
            adapter.resolve_context(payload)
        self.assertIn("Parameter mismatch rejection", str(context.exception))

    # 11. Missing scientific evidence
    def test_missing_scientific_evidence(self):
        adapter = SanskarContextAdapter()
        payload = map_group1_to_group2(self.raw_api_response)
        ctx_no_evidence = copy.deepcopy(self.context_payload)
        ctx_no_evidence["citation"] = ""
        ctx_no_evidence["source_citation"] = ""
        payload["scientific_context"] = ctx_no_evidence
        payload["temporal_ruling"] = self.temporal_ruling
        
        with self.assertRaises(ValueError) as context:
            adapter.resolve_context(payload)
        self.assertIn("missing a citation", str(context.exception))

    # 12 & 13. GAP context & GAP produces NO action_request
    def test_gap_context_and_no_action_request(self):
        adapter = SanskarContextAdapter()
        payload = map_group1_to_group2(self.raw_api_response)
        ctx_gap = {
            "context_id": "WAITING_FOR_VERIFIED_CONTEXT",
            "status": "GAP",
            "validation_status": "GAP"
        }
        payload["scientific_context"] = ctx_gap
        payload["temporal_ruling"] = self.temporal_ruling
        
        envelope = adapter.resolve_context(payload)
        self.assertEqual(envelope["contextual_result"]["status"], "WAITING_FOR_VERIFIED_CONTEXT")
        self.assertIsNone(envelope["action_request"])
        self.assertFalse(envelope["action_eligibility"])
        self.assertTrue(envelope["abstention_required"])

    # 14. ALLOW produces valid action_request
    def test_allow_produces_valid_action_request(self):
        adapter = SanskarContextAdapter()
        payload = map_group1_to_group2(self.raw_api_response)
        payload["scientific_context"] = self.context_payload
        payload["temporal_ruling"] = self.temporal_ruling
        
        envelope = adapter.resolve_context(payload)
        self.assertEqual(envelope["contextual_result"]["status"], "SUCCESS")
        
        action_req = envelope["action_request"]
        self.assertIsNotNone(action_req)
        self.assertEqual(action_req["context_status"], "ALLOW")
        self.assertEqual(action_req["requested_action"], "ALLOW")
        self.assertEqual(action_req["observation_id"], self.observation_id)

    # 15. ADAPT follows defined behavior
    def test_adapt_follows_defined_behavior(self):
        adapter = SanskarContextAdapter()
        payload = map_group1_to_group2(self.raw_api_response)
        
        # Modify location to force spatial mismatch (out of polygon)
        payload["observation"]["location"]["lat"] = 20.1288
        payload["scientific_context"] = self.context_payload
        payload["temporal_ruling"] = self.temporal_ruling
        
        envelope = adapter.resolve_context(payload)
        self.assertEqual(envelope["contextual_result"]["status"], "SUCCESS")
        self.assertFalse(envelope["contextual_result"]["spatial_match"])
        
        # Assert action_request is null for ADAPT path (safety constraint)
        self.assertIsNone(envelope["action_request"])
        self.assertFalse(envelope["action_eligibility"])
        self.assertTrue(envelope["abstention_required"])

    # 16 & 17. TRACE/VANA trace ID accepted
    def test_trace_and_vana_trace_ids_accepted(self):
        adapter = SanskarContextAdapter()
        payload = map_group1_to_group2(self.raw_api_response)
        payload["scientific_context"] = self.context_payload
        payload["temporal_ruling"] = self.temporal_ruling
        
        # 1. Accept VANA prefix
        payload["trace_id"] = "VANA-27b28525d736"
        is_valid, _ = adapter.validate_payload(payload)
        self.assertTrue(is_valid)
        
        # 2. Accept TRACE prefix
        payload["trace_id"] = "TRACE-a1b2c3d4e5f6"
        is_valid, _ = adapter.validate_payload(payload)
        self.assertTrue(is_valid)

    # 18. Invalid trace ID rejected
    def test_invalid_trace_id_rejected(self):
        adapter = SanskarContextAdapter()
        payload = map_group1_to_group2(self.raw_api_response)
        payload["scientific_context"] = self.context_payload
        payload["temporal_ruling"] = self.temporal_ruling
        
        # Mismatched length/chars
        payload["trace_id"] = "MOCK-123"
        is_valid, _ = adapter.validate_payload(payload)
        self.assertFalse(is_valid)

    # 19. Deterministic repeated execution
    def test_deterministic_repeated_execution(self):
        adapter = SanskarContextAdapter()
        payload = map_group1_to_group2(self.raw_api_response)
        payload["scientific_context"] = self.context_payload
        payload["temporal_ruling"] = self.temporal_ruling
        
        envelope1 = adapter.resolve_context(payload)
        envelope2 = adapter.resolve_context(payload)
        self.assertEqual(envelope1, envelope2)

    # 20. Provenance preservation
    def test_provenance_preservation(self):
        adapter = SanskarContextAdapter()
        payload = map_group1_to_group2(self.raw_api_response)
        payload["scientific_context"] = self.context_payload
        payload["temporal_ruling"] = self.temporal_ruling
        
        envelope = adapter.resolve_context(payload)
        prov = envelope["provenance"]
        self.assertEqual(prov["source_id"], self.context_payload["source_doi"])
        self.assertEqual(prov["citation"], self.context_payload["citation"])
        self.assertEqual(prov["verification_status"], "VERIFIED")

    # 21 & 22. Two-DOI role separation & Scientific DOI conflict rejection
    def test_two_doi_role_separation_and_rejection(self):
        adapter = SanskarContextAdapter()
        payload = map_group1_to_group2(self.raw_api_response)
        payload["temporal_ruling"] = self.temporal_ruling
        
        mismatched_context = copy.deepcopy(self.context_payload)
        mismatched_context["source_id"] = "10.5281/zenodo.6894273"
        mismatched_context["source_doi"] = "10.5281/zenodo.6894273"
        payload["scientific_context"] = mismatched_context
        
        with self.assertRaises(ValueError) as context:
            adapter.resolve_context(payload)
        self.assertIn("strictly assigned for spatial extent metadata", str(context.exception))

    # 23. Identity mismatch rejection
    def test_identity_mismatch_rejection(self):
        adapter = SanskarContextAdapter()
        payload = map_group1_to_group2(self.raw_api_response)
        payload["temporal_ruling"] = self.temporal_ruling
        
        # Inject context containing observation_id matching the canonical id
        ctx_mismatched = copy.deepcopy(self.context_payload)
        ctx_mismatched["observation_id"] = "TC-Z03-F02-LIDAR-OBS001"
        payload["scientific_context"] = ctx_mismatched
        
        # Change observation_id to cause mismatch
        payload["observation"]["observation_id"] = "TC-Z03-F02-LIDAR-OBS002"
        
        with self.assertRaises(ValueError) as context:
            adapter.resolve_context(payload)
        self.assertIn("Observation ID mismatch rejection", str(context.exception))

    # 24. Test Authoritative GAP Ruling overrides local ALLOW validation
    def test_authoritative_gap_overrides_local_validation(self):
        adapter = SanskarContextAdapter()
        payload = map_group1_to_group2(self.raw_api_response)
        payload["scientific_context"] = self.context_payload
        # Inject authoritative GAP ruling
        payload["temporal_ruling"] = {"ruling": "GAP"}
        
        envelope = adapter.resolve_context(payload)
        # Even though range validation is within 3.5 - 6.5, the GAP ruling overrides it
        self.assertEqual(envelope["contextual_result"]["status"], "WAITING_FOR_VERIFIED_CONTEXT")
        self.assertFalse(envelope["action_eligibility"])
        self.assertTrue(envelope["abstention_required"])
        self.assertIsNone(envelope["action_request"])

    # 25. Test No Authoritative Ruling defaults to GAP (no silent ALLOW)
    def test_no_authoritative_ruling_defaults_to_gap(self):
        adapter = SanskarContextAdapter()
        payload = map_group1_to_group2(self.raw_api_response)
        payload["scientific_context"] = self.context_payload
        # Omit temporal_ruling entirely
        payload["temporal_ruling"] = None
        
        envelope = adapter.resolve_context(payload)
        self.assertEqual(envelope["contextual_result"]["status"], "WAITING_FOR_VERIFIED_CONTEXT")
        self.assertFalse(envelope["action_eligibility"])
        self.assertTrue(envelope["abstention_required"])
        self.assertIsNone(envelope["action_request"])

if __name__ == "__main__":
    unittest.main()
