# GROUP2_CONTEXT_CONTRACT.md
**Owner:** Sakshi Thakur — Group 2  
**Version:** 1.0.0  
**Date:** 19 August 2026

## Required continuity fields
`observation_id`, `source_observation_id`, `raw_artifact_reference`, `provenance`, `timestamp`, `location`, `measurement`, `measurement_unit`, `quality`, `scientific_source_reference`, `context_id`, `context_status`, `context_ruling`.

## Identity continuity
For `TC-Z03-F02-LIDAR-OBS001`:
`source_observation_id == observation_id`

Group 2/SANSKAR must not generate, replace, or overwrite the canonical observation ID.

## Verified Group 1 observation
```text
GET /observations/TC-Z03-F02-LIDAR-OBS001
HTTP 200 OK
observation_id = TC-Z03-F02-LIDAR-OBS001
parameter = canopy_height
measurement = 4.7
measurement_unit = m
timestamp = 2026-08-13T09:14:22+00:00
location = {lat: 19.1288, lon: 72.9421}
quality = VALIDATED
```

The observation remains retrievable by `observation_id`.

`trace_id = VANA-04aa4b71f56f` is request/response metadata and is not the observation identity.

## Continuity rules
1. Preserve observation ID unchanged.
2. Preserve source observation ID as the same canonical ID.
3. Preserve coordinates exactly.
4. Preserve observation timestamp.
5. Preserve measurement and unit; no silent conversion.
6. Preserve quality and provenance.
7. Keep scientific context separate from the source observation.
8. Contextual results must not overwrite source-owned fields.

## Verified scientific context
- parameter: `expected_canopy_height`
- reference: `4.8 m`
- range: `3.5–6.5 m`
- confidence: `0.85`
- validation: `VERIFIED`
- DOI: `10.1016/j.rsma.2023.103207`

The 4.8 m reference must not overwrite the observed 4.7 m.

## Negative requirements
Reject/fail validation for replacement IDs, mismatched source IDs, unsupported measurements, incompatible units, coordinate mutation, timestamp mutation, or source-observation overwrite.

## Group 4 boundary
This is the Group 2 semantic/continuity contract. Group 4 runtime-specific details must be documented separately.

**Group 4 authoritative runtime contract was not received by EOD.**
