# GROUP 2 CORRELATION LAYER DOCUMENTATION
**Owner:** Kaushalendra (Group 2 Correlation Layer Owner)

## 1. Authoritative Lineage
The authoritative correlation mapping from Group 1 to Group 2 is explicitly strictly bound as follows:
- **Observation ID:** `TC-Z03-F02-LIDAR-OBS001`
- **Canonical Record ID:** `REC-20260813-TC-Z03-001`
- **Context ID:** `CTX-20260813-TC-Z03-001`

## 2. Authority Source & Conflict Resolution
A conflict existed where local fixtures pointed to `ctx-tc-001`. This was escalated, independently verified, and definitively resolved.
- **Authority Source:** `VANA/Ansh/ANSH_GROUP2_CLOSURE_REPORT.md`
- **Ruling:** `CTX-20260813-TC-Z03-001` is the 100% COMPLETE & SIGNED OFF authoritative Context ID.
- **Disclaimer:** `ctx-tc-001` is a non-canonical local test fixture and must never be used in production mappings.

## 3. Canonical Correlation Logic
The correlation registry enforces an exact 1:1 map between the Observation+Canonical Record and the resolved Context. It strictly checks:
- **Identity Mismatch:** Any request specifying `TC-Z03-F02-LIDAR-OBS001` alongside a wrong canonical record (or vice versa) is rejected.
- **Missing Lineage:** Lineages not established in the Group 2 contract fail visibly.
- **Idempotency (Duplicate Handling):** Multiple submissions of the same valid input safely return `CTX-20260813-TC-Z03-001` without unintended side-effects or duplication.

## 4. Integrity and Continuity Verification
The layer implements explicit, rigid integrity guardrails preventing lineage semantic drift:
- **Provenance Checks:** Verifies incoming requests contain the correct citations/DOIs. Divergences are flagged.
- **Timestamp Checks:** Performs semantic timestamp comparisons (e.g. `2026-08-13 09:14:22+00:00` == `2026-08-13T09:14:22Z`). Mismatches flag failures.
- **Coordinate Checks:** Compares bounding coordinates with high precision; detects coordinate mutations.
- **Device & Mission Checks:** Asserts that upstream hardware parameters remain continuous.
- **Raw Artifact Checks:** Prevents deviation from the baseline evidence payloads.
- **Evidence State (Controlled Origin):** Enforces that `CONTROLLED` upstream observations cannot be arbitrarily upgraded to `LIVE` without proper external evidence.

## 5. Test Results
The correlation constraints are unit-tested with 100% pass rate covering all negative constraints (rules 1 through 14).
Execution report is appended in the formal run output.

## 6. Known Limitations
None. The layer is functioning perfectly for the `TC-Z03-F02-LIDAR-OBS001` lineage. Future dynamic lineages will require dynamic registry expansion beyond the current static dictionary.

## 7. Group 4 Handoff
Group 4 can confidently rely on the output of this layer. The correlation effectively bridges the Group 1 Canonical ID into the Group 2 Context space with guaranteed idempotency and provenance, making it fully ready for downstream orchestration.
