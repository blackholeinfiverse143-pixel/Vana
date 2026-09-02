# Kaushlendra — Technical Review / Schema-Runtime Support

## Purpose
This packet is prepared for Kaushlendra's assigned VANA EOD role: **Technical review / schema-runtime support**.

## Files included
1. `GROUP2_CONTEXT_CONTRACT (1).md` — Group 2 continuity/context contract.
2. `GROUP1_TO_GROUP2_RUNTIME.md` — Group 1 → Group 2 runtime mapping and interface documentation.
3. `VANA_Combined_EOD_Closure_Command_PPT.pdf` — EOD closure ownership and acceptance requirements.
4. `LIVE_EVIDENCE_TO_VERIFY.json` — current evidence/checklist for live verification.

## Important note about V2.2 schema
The exact library file named `observation.schema.v2.2.json` was **not found** in the available file library during packet preparation. It is referenced by other VANA artifacts, but this packet does not recreate or invent its contents.

If the actual `observation.schema.v2.2.json` exists in the project repository, Kaushlendra should use that authoritative project file for the schema check.

## Review to perform
Please verify:
- V2.2 schema consistency against the authoritative project schema.
- G1 → G2 field mapping consistency.
- `observation_id` continuity.
- `canonical_record_id` continuity where returned by Group 1.
- Timestamp preservation.
- Location/coordinates preservation.
- Measurement and unit preservation.
- Provenance preservation.
- G2 decision-envelope field consistency.
- No identity rewrite or silent semantic change.
- No fabricated fallback data.

## Current UI/runtime evidence
The current UI test is using:
- Observation ID: `SMR-Z01-EXT-SAMACHAR-OBS001`
- Group 1: healthy in the live UI.
- Group 2: healthy in the live UI.
- Group 4: live governed abstention is now visible in the UI.

For the exact current Group 1 and Group 2 JSON payloads, use the live API response / UI raw response as the source of truth. Do not infer missing fields from older examples.

## Expected report
Return a short report:

V2.2 schema consistency: PASS / FAIL / NOT_VERIFIED
G1 → G2 field mapping: PASS / FAIL / NOT_VERIFIED
Observation identity continuity: PASS / FAIL / NOT_VERIFIED
Canonical record continuity: PASS / FAIL / NOT_VERIFIED
Timestamp preservation: PASS / FAIL / NOT_VERIFIED
Location preservation: PASS / FAIL / NOT_VERIFIED
Measurement/unit preservation: PASS / FAIL / NOT_VERIFIED
Provenance preservation: PASS / FAIL / NOT_VERIFIED
G2 decision envelope: PASS / FAIL / NOT_VERIFIED
Remaining blocker: NONE / <specific blocker>
Evidence used: <file/API/runtime evidence>

**No contract or semantic changes are requested as part of this review.**
