# Provenance Preservation Test

## Objective

Verify that the contextual result remains traceable to both the original observation and the scientific evidence.

## Required assertions

### Observation provenance
- `observation_id` is unchanged.
- Observation parameter, value, unit, location and timestamp are unchanged.
- `geo_id`, when present, is unchanged.

### Scientific provenance
- `source_id` is preserved.
- Human-readable `citation` is preserved.
- `verification_status` is preserved.
- `source_url` is preserved or remains null if unavailable.

### Confidence and quality
- `confidence` and `quality` remain separate.
- No confidence value is fabricated.
- No quality value is derived from confidence.

### Acceptance

```text
contextual_result
      |
      +--> observation.observation_id
      |
      +--> provenance.source_id
      +--> provenance.citation
```

Both traceability legs must be present for acceptance.
