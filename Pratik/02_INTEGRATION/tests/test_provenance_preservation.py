import sys
import os
import unittest
import copy
import json

# Adjust python path to import adapter module
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "adapter"))
from sanskar_adapter import SanskarContextAdapter

class TestProvenancePreservation(unittest.TestCase):
    def setUp(self):
        self.adapter = SanskarContextAdapter()
        
        self.observation = {
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

        self.scientific_context = {
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
            "source_id": "10.1016/j.rsma.2023.103207",
            "source": "ScienceDirect / Elsevier (2023) — \"Standing carbon stock of Thane Creek mangrove ecosystem, Maharashtra, India\"",
            "citation": "ScienceDirect / Elsevier (2023) — \"Standing carbon stock of Thane Creek mangrove ecosystem, Maharashtra, India\"",
            "verification_status": "VERIFIED",
            "confidence_score": 0.85,
            "quality": "HIGH",
            "uncertainty": "LOW",
            "status": "VERIFIED"
        }

        self.trace_id = "TRACE-a1b2c3d4e5f6"
        self.temporal_ruling = {"ruling": "ALLOW"}

    def test_provenance_and_immutability(self):
        payload = {
            "trace_id": self.trace_id,
            "observation": self.observation,
            "scientific_context": self.scientific_context,
            "temporal_ruling": self.temporal_ruling
        }

        # Keep a copy of the observation and context before processing to verify immutability
        observation_before = copy.deepcopy(self.observation)
        context_before = copy.deepcopy(self.scientific_context)

        # Execute adapter resolution
        envelope = self.adapter.resolve_context(payload)

        # 1. Verify Immutability: observation and context must not be mutated
        self.assertFalse(envelope["observation_mutated"])
        self.assertEqual(self.observation, observation_before, "Primary observation was mutated during execution!")
        self.assertEqual(self.scientific_context, context_before, "Context provenance fields were mutated during execution!")

        # 2. Verify Provenance Preservation
        self.assertEqual(envelope["observation"]["observation_id"], self.observation["observation_id"])
        self.assertEqual(envelope["scientific_context"]["context_id"], self.scientific_context["context_id"])
        self.assertEqual(envelope["provenance"]["source_id"], self.scientific_context["source_id"])
        self.assertEqual(envelope["provenance"]["citation"], self.scientific_context["citation"])
        self.assertEqual(envelope["provenance"]["verification_status"], self.scientific_context["verification_status"])
        self.assertEqual(envelope["provenance"]["confidence"], self.scientific_context["confidence_score"])
        self.assertEqual(envelope["provenance"]["quality"], self.scientific_context["quality"])
        self.assertEqual(envelope["provenance"]["uncertainty"], self.scientific_context["uncertainty"])
        self.assertEqual(envelope["trace"]["trace_id"], self.trace_id)

        # 3. Verify Contextual Result Values (4.7 m against range 3.5 - 6.5 m)
        self.assertEqual(envelope["contextual_result"]["parameter_evaluated"], "canopy_height")
        self.assertEqual(envelope["observation"]["value"], 4.7)
        self.assertEqual(envelope["observation"]["unit"], "m")
        self.assertEqual(envelope["contextual_result"]["reference_value"], self.scientific_context["value"]["mean"])
        self.assertFalse(envelope["contextual_result"]["anomaly_detected"]) # 4.7 is within 3.5-6.5
        self.assertEqual(envelope["contextual_result"]["deviation"], "Within expected range")
        self.assertEqual(envelope["contextual_result"]["status"], "SUCCESS")
        
        # 4. Verify Governance fields
        self.assertTrue(envelope["action_eligibility"])
        self.assertFalse(envelope["abstention_required"])
        self.assertTrue(envelope["contextual_result"]["action_eligibility"])
        self.assertFalse(envelope["contextual_result"]["abstention_required"])

    def test_determinism_validation(self):
        payload = {
            "trace_id": self.trace_id,
            "observation": self.observation,
            "scientific_context": self.scientific_context,
            "temporal_ruling": self.temporal_ruling
        }

        # Run contextualisation twice
        envelope1 = self.adapter.resolve_context(payload)
        envelope2 = self.adapter.resolve_context(payload)

        # Assert that the outputs are identical, proving determinism
        self.assertEqual(envelope1, envelope2, "Deterministic repeated execution failed: outputs differ!")

    def test_kaushlendra_updated_record_resolution(self):
        # 1. Load Kaushlendra's updated context record from the copy file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        context_path = os.path.join(base_dir, "01_SOURCE_ARTIFACTS", "KAUSHLENDRA", "TC-Z03-F02-LIDAR-OBS001 - Copy.json")
        self.assertTrue(os.path.exists(context_path), f"Kaushlendra's updated copy record not found at {context_path}")
        with open(context_path, "r") as f:
            updated_context = json.load(f)

        # 2. Assemble payload
        payload = {
            "trace_id": self.trace_id,
            "observation": self.observation,
            "scientific_context": updated_context,
            "temporal_ruling": self.temporal_ruling
        }

        # 3. Execute adapter resolution
        envelope = self.adapter.resolve_context(payload)

        # 4. Assert provenance and evaluation parameters
        self.assertEqual(envelope["observation"]["observation_id"], self.observation["observation_id"])
        self.assertEqual(envelope["scientific_context"]["context_id"], updated_context["context_id"])
        self.assertEqual(envelope["provenance"]["verification_status"], "VERIFIED")
        self.assertEqual(envelope["provenance"]["confidence"], 0.85)
        self.assertEqual(envelope["provenance"]["source_id"], "10.1016/j.rsma.2023.103207")
        self.assertIn("Elsevier", envelope["provenance"]["citation"])

        # 5. Assert evaluation bounds
        self.assertEqual(envelope["contextual_result"]["parameter_evaluated"], "canopy_height")
        self.assertEqual(envelope["observation"]["value"], 4.7)
        self.assertEqual(envelope["contextual_result"]["reference_value"], 4.8)
        self.assertFalse(envelope["contextual_result"]["anomaly_detected"])
        self.assertTrue(envelope["contextual_result"]["spatial_match"])
        self.assertTrue(envelope["contextual_result"]["temporal_match"])
        self.assertEqual(envelope["contextual_result"]["status"], "SUCCESS")

    def test_action_request_generation(self):
        payload = {
            "trace_id": self.trace_id,
            "observation": self.observation,
            "scientific_context": self.scientific_context,
            "temporal_ruling": self.temporal_ruling
        }

        observation_before = copy.deepcopy(self.observation)

        envelope = self.adapter.resolve_context(payload)

        # Assert no canonical observation fields were mutated during resolution
        self.assertEqual(self.observation, observation_before)

        # Assert Action Request generation
        self.assertIn("action_request", envelope)
        action_req = envelope["action_request"]

        self.assertTrue(action_req["action_request_id"].startswith("req-"))
        self.assertEqual(action_req["observation_id"], self.observation["observation_id"])
        self.assertEqual(action_req["context_id"], self.scientific_context["context_id"])
        self.assertEqual(action_req["context_status"], "ALLOW")
        self.assertEqual(action_req["scientific_source_reference"], self.scientific_context["citation"])
        self.assertEqual(action_req["requested_capability"], "ENVIRONMENTAL_CONTEXTUALISATION")
        self.assertEqual(action_req["requested_action"], "ALLOW")
        self.assertEqual(action_req["semantic_contract_version"], "v1")
        self.assertEqual(action_req["provenance_reference"], "10.1016/j.rsma.2023.103207")
        self.assertEqual(action_req["trace_id"], self.trace_id)

    def test_scientific_gap_preservation(self):
        ctx_gap = {
            "context_id": "WAITING_FOR_VERIFIED_CONTEXT",
            "status": "GAP",
            "validation_status": "GAP"
        }
        payload = {
            "trace_id": self.trace_id,
            "observation": self.observation,
            "scientific_context": ctx_gap,
            "temporal_ruling": self.temporal_ruling
        }

        envelope = self.adapter.resolve_context(payload)

        # Assert GAP preservation behavior (distinction between observation and reference/baseline)
        self.assertEqual(envelope["contextual_result"]["status"], "WAITING_FOR_VERIFIED_CONTEXT")
        self.assertIsNone(envelope["contextual_result"]["reference_value"])
        self.assertIsNone(envelope["contextual_result"]["deviation"])
        self.assertIsNone(envelope["contextual_result"]["anomaly_detected"])
        
        # Verify Action Request preserves GAP by returning None (abstention)
        self.assertIsNone(envelope["action_request"])
        self.assertFalse(envelope["action_eligibility"])
        self.assertTrue(envelope["abstention_required"])

        # Confirm that observation values were NOT mutated or used as a baseline
        self.assertEqual(envelope["observation"]["value"], 4.7)

if __name__ == "__main__":
    unittest.main()
