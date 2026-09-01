import sys
import os
import unittest

# Adjust python path to import adapter module
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "adapter"))
from sanskar_adapter import SanskarContextAdapter

class TestContractValidation(unittest.TestCase):
    def setUp(self):
        self.adapter = SanskarContextAdapter()
        
        self.valid_obs = {
            "observation_id": "TC-Z03-F02-LIDAR-OBS001",
            "status": "SYNTHETIC_TEST",
            "measurement": {
                "parameter": "canopy_height",
                "value": 4.7,
                "unit": "m",
                "method": "LiDAR canopy scan"
            },
            "location": {
                "lat": 19.1288,
                "lon": 72.9421,
                "place_name": "Thane Creek Zone 3 Plot 2"
            },
            "timestamp": "2026-08-13T09:14:22Z"
        }

        self.valid_context = {
            "context_id": "ctx-tc-001",
            "parameter": "expected_canopy_height",
            "value": {
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
            "source_id": "GMW-v3.0",
            "citation": "ScienceDirect / Elsevier (2023) — \"Standing carbon stock of Thane Creek mangrove ecosystem, Maharashtra, India\"",
            "verification_status": "VERIFIED",
            "confidence_score": 0.85,
            "quality": "HIGH",
            "uncertainty": "LOW",
            "status": "VERIFIED"
        }
        
        self.valid_temporal_ruling = {"ruling": "ALLOW"}

    def test_valid_payload_passes(self):
        payload = {
            "trace_id": "TRACE-a1b2c3d4e5f6",
            "observation": self.valid_obs,
            "scientific_context": self.valid_context,
            "temporal_ruling": self.valid_temporal_ruling
        }
        res, msg = self.adapter.validate_payload(payload)
        self.assertTrue(res, msg)

    def test_missing_trace_id_rejection(self):
        payload = {
            "observation": self.valid_obs,
            "scientific_context": self.valid_context,
            "temporal_ruling": self.valid_temporal_ruling
        }
        res, msg = self.adapter.validate_payload(payload)
        self.assertFalse(res)
        self.assertIn("Missing trace_id", msg)

    def test_invalid_trace_id_format_rejection(self):
        payload = {
            "trace_id": "TRACE-invalid",
            "observation": self.valid_obs,
            "scientific_context": self.valid_context,
            "temporal_ruling": self.valid_temporal_ruling
        }
        res, msg = self.adapter.validate_payload(payload)
        self.assertFalse(res)
        self.assertIn("Invalid trace_id format", msg)

    def test_missing_citation_rejection(self):
        ctx_no_cit = self.valid_context.copy()
        ctx_no_cit["citation"] = ""
        payload = {
            "trace_id": "TRACE-a1b2c3d4e5f6",
            "observation": self.valid_obs,
            "scientific_context": ctx_no_cit,
            "temporal_ruling": self.valid_temporal_ruling
        }
        with self.assertRaises(ValueError) as context:
            self.adapter.resolve_context(payload)
        self.assertIn("missing a citation", str(context.exception))

    def test_parameter_mismatch_rejection(self):
        ctx_mismatch = self.valid_context.copy()
        ctx_mismatch["parameter"] = "salinity" # Mismatch canopy_height vs salinity
        payload = {
            "trace_id": "TRACE-a1b2c3d4e5f6",
            "observation": self.valid_obs,
            "scientific_context": ctx_mismatch,
            "temporal_ruling": self.valid_temporal_ruling
        }
        with self.assertRaises(ValueError) as context:
            self.adapter.resolve_context(payload)
        self.assertIn("Parameter mismatch", str(context.exception))

    def test_unit_mismatch_rejection(self):
        ctx_unit_mismatch = self.valid_context.copy()
        ctx_unit_mismatch["unit"] = "cm" # Unit mismatch
        payload = {
            "trace_id": "TRACE-a1b2c3d4e5f6",
            "observation": self.valid_obs,
            "scientific_context": ctx_unit_mismatch,
            "temporal_ruling": self.valid_temporal_ruling
        }
        with self.assertRaises(ValueError) as context:
            self.adapter.resolve_context(payload)
        self.assertIn("Unit mismatch", str(context.exception))

    def test_spatial_validation_out_of_bounds(self):
        obs_outside = self.valid_obs.copy()
        obs_outside["location"] = {
            "lat": 20.1411, # Outside latitude bounding box
            "lon": 72.9642,
            "place_name": "Deep Sea Location"
        }
        payload = {
            "trace_id": "TRACE-a1b2c3d4e5f6",
            "observation": obs_outside,
            "scientific_context": self.valid_context,
            "temporal_ruling": self.valid_temporal_ruling
        }
        envelope = self.adapter.resolve_context(payload)
        self.assertFalse(envelope["contextual_result"]["spatial_match"])
        # Governance fields present and indicate ADAPT (abstention)
        self.assertFalse(envelope["action_eligibility"])
        self.assertTrue(envelope["abstention_required"])
        self.assertIsNone(envelope["action_request"])

    def test_temporal_validation_out_of_bounds(self):
        obs_future = self.valid_obs.copy()
        obs_future["timestamp"] = "2029-08-14T12:00:00Z" # Beyond 2020-2028 temporal range
        payload = {
            "trace_id": "TRACE-a1b2c3d4e5f6",
            "observation": obs_future,
            "scientific_context": self.valid_context,
            "temporal_ruling": self.valid_temporal_ruling
        }
        envelope = self.adapter.resolve_context(payload)
        self.assertFalse(envelope["contextual_result"]["temporal_match"])
        # Governance fields present and indicate ADAPT (abstention)
        self.assertFalse(envelope["action_eligibility"])
        self.assertTrue(envelope["abstention_required"])
        self.assertIsNone(envelope["action_request"])

    def test_gap_context_status_handling(self):
        ctx_gap = {
            "context_id": "WAITING_FOR_VERIFIED_CONTEXT",
            "status": "GAP"
        }
        payload = {
            "trace_id": "TRACE-a1b2c3d4e5f6",
            "observation": self.valid_obs,
            "scientific_context": ctx_gap,
            "temporal_ruling": self.valid_temporal_ruling
        }
        
        envelope = self.adapter.resolve_context(payload)
        self.assertEqual(envelope["scientific_context"]["context_id"], "WAITING_FOR_VERIFIED_CONTEXT")
        self.assertEqual(envelope["provenance"]["verification_status"], "GAP")
        self.assertEqual(envelope["contextual_result"]["status"], "WAITING_FOR_VERIFIED_CONTEXT")
        self.assertFalse(envelope["observation_mutated"])
        self.assertFalse(envelope["action_eligibility"])
        self.assertTrue(envelope["abstention_required"])
        self.assertIsNone(envelope["action_request"])

    def test_lower_confidence_status_preservation(self):
        # Verify that GAP, UNKNOWN, PENDING, and NOT_VERIFIED preserve their states
        # and do not silently upgrade to VERIFIED
        for status in ["GAP", "UNKNOWN", "PENDING", "NOT_VERIFIED"]:
            ctx_pending = self.valid_context.copy()
            ctx_pending["verification_status"] = status
            ctx_pending["validation_status"] = status
            payload = {
                "trace_id": "TRACE-a1b2c3d4e5f6",
                "observation": self.valid_obs,
                "scientific_context": ctx_pending,
                "temporal_ruling": self.valid_temporal_ruling
            }
            # Note: if status is GAP, it will exit early and return GAP envelope
            envelope = self.adapter.resolve_context(payload)
            self.assertEqual(envelope["provenance"]["verification_status"], status)
            if status != "VERIFIED":
                self.assertNotEqual(envelope["provenance"]["verification_status"], "VERIFIED")

    def test_doi_conflict_rejection(self):
        # 1. Test that spatial extent DOI is rejected for canopy_height attribute resolution
        ctx_conflicted = self.valid_context.copy()
        ctx_conflicted["source_id"] = "10.5281/zenodo.6894273"  # Zenodo spatial DOI
        payload = {
            "trace_id": "TRACE-a1b2c3d4e5f6",
            "observation": self.valid_obs,
            "scientific_context": ctx_conflicted,
            "temporal_ruling": self.valid_temporal_ruling
        }
        with self.assertRaises(ValueError) as context:
            self.adapter.resolve_context(payload)
        self.assertIn("strictly assigned for spatial extent metadata", str(context.exception))

        # 2. Test that another random DOI is rejected for canopy_height
        ctx_wrong = self.valid_context.copy()
        ctx_wrong["source_id"] = "10.1016/j.ecolind.2023.109876"  # Typo paper DOI
        payload = {
            "trace_id": "TRACE-a1b2c3d4e5f6",
            "observation": self.valid_obs,
            "scientific_context": ctx_wrong,
            "temporal_ruling": self.valid_temporal_ruling
        }
        with self.assertRaises(ValueError) as context:
            self.adapter.resolve_context(payload)
        self.assertIn("not the authoritative citation", str(context.exception))

if __name__ == "__main__":
    unittest.main()
