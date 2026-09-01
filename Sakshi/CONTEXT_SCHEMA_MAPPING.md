# CONTEXT_SCHEMA_MAPPING.md

| Group 1 canonical field | Group 2 context field | Rule |
|---|---|---|
| observation_id | observation_id | Same value |
| observation_id | source_observation_id | Same value |
| timestamp | timestamp | Same source time |
| location | location | Same coordinates |
| measurement/value | measurement | Same value |
| unit | measurement_unit | Same unit |
| quality | quality | Preserve |
| provenance/source | provenance | Preserve |
| raw artifact | raw_artifact_reference | Preserve/reference |
| scientific evidence | scientific_source_reference | Separate from observation |
| Group 2 context identity | context_id | Context identity only |
| validation | context_status | Preserve context state |
| ruling | context_ruling | Context decision |

Critical chain:
`Group 1 observation_id = Group 2 observation_id = Group 2 source_observation_id`

`context_id` may differ because it identifies the context record.
