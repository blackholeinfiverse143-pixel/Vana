# SANSKAR Input / Output Mapping

## Semantic Input

### Observation
```text
observation_id = TC-Z03-F02-LIDAR-OBS001
parameter      = canopy_height
value          = 4.7
unit           = m
timestamp      = 2026-08-13T09:14:22Z
location       = {lat: 19.1288, lon: 72.9421}
```

### Scientific Context
```text
parameter_name    = expected_canopy_height
reference         = 4.8 m
range             = 3.5–6.5 m
confidence        = 0.85
validation_status = VERIFIED
citation          = ScienceDirect / Elsevier (2023)
DOI               = 10.1016/j.rsma.2023.103207
```

## Semantic Output

The output must keep source observation and derived context separate:

```json
{
  "observation": {},
  "provenance": {},
  "scientific_context": {},
  "contextual_result": {},
  "trace": {}
}
```

## Required Output Semantics

- Original `observation_id` remains unchanged.
- Original observation value remains `4.7 m`.
- Scientific reference remains separate as contextual data.
- Scientific source/citation remains traceable.
- Confidence and quality remain separate.
- SANSKAR-derived assessment fields are separate from source-owned fields.

## Runtime Contract Status

The semantic mapping is defined by Group 2.

The authoritative Group 4 runtime contract is still pending and must establish:
- endpoint;
- HTTP method;
- request schema;
- response schema;
- trace ID ownership/format;
- idempotency behavior;
- replay/trace behavior.

No unverified runtime endpoint or response is claimed here.
