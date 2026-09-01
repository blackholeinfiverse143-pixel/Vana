# PROVENANCE_PRESERVATION_PROOF.md

A final contextual result must preserve both provenance legs.

## Observation provenance
- observation_id unchanged
- source_observation_id equals observation_id
- timestamp unchanged
- location unchanged
- measurement/value unchanged
- unit unchanged
- quality preserved

## Scientific provenance
- source identity preserved
- citation/source reference preserved
- validation status preserved
- confidence preserved separately from quality

## Trace distinction
`VANA-04aa4b71f56f` is retrieval trace metadata.
`TC-Z03-F02-LIDAR-OBS001` is immutable observation identity.

A trace_id alone is not sufficient provenance.

**Status:** Rules implemented/documented; final live SANSKAR proof pending Group 4 runtime contract.
