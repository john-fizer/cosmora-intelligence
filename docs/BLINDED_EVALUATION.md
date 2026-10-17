# Blinded interpretation and calibration

`cosmora.blinded` adds a separate experiment ledger to the analyst workflow. It prepares chart-only packets, commits predictions before disclosure, reveals independently labeled outcomes, scores development and holdout people separately, and exports a private provenance graph. It does not launch an LLM or train model weights.

Existing event-informed pilot annotations are exploratory and cannot become blind predictions. The five pilot subjects and their events have already been disclosed in the working conversation. Use a fresh, isolated interpreter session and a suitable new evaluation cohort.

## Roles and isolation

1. The coordinator freezes a rulebook, controlled event categories, threshold, person split, and event-independent window selection before generating predictions. Windows must include opportunities for both events and non-events; selecting only known event dates cannot measure false positives.
2. A calculation worker builds natal and transit frames with the existing deterministic ephemeris pipeline. Frames must use the supported tropical Whole Sign profile and transits through natal houses. Packet preparation uses the existing five major aspects and three-degree orb; the machine-readable `computed_aspect_policy` is authoritative. The natural-language `orb_policy` must describe it consistently.
3. The coordinator exports only the packet into a separate interpreter environment. That agent receives no original chart files, private ledger, graph, manifests, event pages, browser, retrieval tools, previous conversation or filesystem access. It interprets the registered rules, not biographical knowledge. Its identity includes model/version and prompt revision, recorded in `agent`.
4. An independent labeler classifies the full window/category grid without seeing predictions. Positive and negative labels both need evidence. A missing biography entry is not proof of absence; unknown outcomes must be resolved before revealing a complete study. Independence is an attestation; this CLI cannot enforce human independence or evidence quality.
5. The coordinator commits the complete prediction grid, then reveals the complete independently prepared labels. Both payloads are immutable through this API. Scores remain descriptive and training-ineligible.
6. A calibration analyst examines development errors and proposes a new rule version with `parent_study` and `revision_reason`. Use a new study; never edit the original predictions. Validate the revised interpretation on fresh holdout people. Reuse the same ledger and stable person keys across studies to enforce exposure history.

Chart configurations can reveal age, era or identity even after removing names and dates. The packet is pseudonymized, not guaranteed anonymous. Rule text and sampling must be inspected for clues. A successful acknowledgment does not establish blindness. An operator can also edit a local SQLite database or create a new ledger: timestamps and SHA-256 commitments support auditability, not tamper-proof external preregistration.

## Inputs

A prepare manifest contains `protocol` and `cases`.

Protocol fields:

- `version`: interpretation rulebook version.
- `rules`: mapping of stable rule IDs to explicit interpretive axioms. Keep identities, biographies and examples from the evaluation cohort out of rule text.
- `categories`: unique controlled codes such as `award` or `publication`. Define inclusion, exclusion, timing and ambiguous cases in the frozen rulebook.
- `threshold`: probability cut-off strictly between zero and one, fixed before scoring.
- `window_selection`: auditable description of the event-independent window schedule and coverage, including non-events. Software checks its presence, not its scientific adequacy.
- `techniques`: supplied calculation layers; currently natal and transit inputs only. Progressions, profections and releasing are not implemented by this module.
- `orb_policy`: description of the fixed computed aspect policy.
- Optional `parent_study`, `revision_reason`: link a new interpretation version to a revealed prior study. Changes should be based on development results; the software cannot audit what an analyst has seen.

Each case contains `person_key` (stable private identity key), `split` (`development` or `holdout`), `natal` (parsed saved chart JSON), and `windows`. Each window has a neutral ID such as `w1` and a nonempty `frames` array of parsed saved transit chart JSONs. Optional private window metadata may record date bounds, age, cadence, coverage and uncertainty. Use identical ordered window IDs across people; supply the same sampling policy and coverage independently of outcomes. Do not use event IDs as window IDs. Age-relative schedules are preferable when appropriate to the declared research question. The operator must randomize case order independently of the split before preparation.

The public packet exposes random case IDs, numeric chart placements, derived signs/decans/rulers, computed transit-to-natal contacts, and the rulebook. It excludes input names, original chart IDs, places, dates, source URLs, private window metadata, split assignments and artifact hashes. Frame order is preserved within each window. No absolute dates or age metadata are supplied to the interpreter in v1; this limits the timing questions it can answer. The ledger retains private chart hashes and window mappings for later audit.

Prediction JSON:

```json
{
  "agent": "model-version/prompt-v1",
  "acknowledges_blinding_limits": true,
  "predictions": [
    {"case_id": "case-FROM-PACKET", "window_id": "w1", "category": "award",
     "probability": 0.2, "rule_ids": ["r1"],
     "rationale": "Specific chart observations and their registered interpretation."}
  ]
}
```

Supply exactly one row for every case/window/category. A low probability is an explicit forecast of no event; omitted cells are rejected. References to nonexistent rules, NaN probabilities, out-of-range values, duplicate rows and changed commitments are rejected. The code validates rule references, not the truth or numerical accuracy of free-text rationales. Use the computed contacts instead of asking the LLM to calculate positions/aspects.

Independent label JSON:

```json
{
  "reviewer": "independent-labeler-id",
  "independent_of_predictions": true,
  "labels": [
    {"person_key": "private-stable-person-key", "window_id": "w1", "category": "award",
     "occurred": 0, "source_url": "https://publisher.example/source",
     "evidence_note": "Source passage or documented coverage supporting the classification."}
  ]
}
```

Supply the complete grid, with integer `occurred` values of 0 or 1. The reviewer ID must differ from the interpreter ID. Labels are stored as reviewer-attested, not independently verified historical facts. The system never promotes them into the approved historical graph.

## Commands

Run from the repository root. Create the private output directory first. Substitute the study ID printed by `prepare` for `STUDY_ID`.

```powershell
python -m cosmora.blinded prepare --db data/blind/studies.db --input data/blind/manifest.json
python -m cosmora.blinded packet --db data/blind/studies.db --study STUDY_ID --output data/blind/packet.json
# Give only packet.json to the isolated interpreter, then collect its predictions.json.
python -m cosmora.blinded commit --db data/blind/studies.db --study STUDY_ID --input data/blind/predictions.json
# Import labels prepared independently, without access to the predictions.
python -m cosmora.blinded reveal --db data/blind/studies.db --study STUDY_ID --input data/blind/labels.json
python -m cosmora.blinded score --db data/blind/studies.db --study STUDY_ID --output data/blind/scores.json
python -m cosmora.blinded graph --db data/blind/studies.db --study STUDY_ID --output data/blind/graph.json
```

`prepare` embeds and freezes the protocol, sanitized chart data and private artifact fingerprints. `commit` returns a SHA-256 commitment and records its UTC time. Identical resubmissions are idempotent; changed payloads require a new study. `reveal` requires a prior complete commitment. Once a person's labels are revealed in this ledger, that person cannot be fresh holdout data in a later study. This check runs again at commit time to catch studies prepared before another study revealed the same people. Stable identity keys are essential; aliases or new ledgers defeat this check.

## Scores and the axiom-change loop

Brier score measures squared probability error (lower is better). Precision, recall, false positives and false negatives use the frozen threshold. Scores are reported separately by person split. The baseline predicts each category's observed development-set frequency; it never estimates its rate from holdout labels. These descriptive cell averages do not assume independent windows or categories, and they are not significance tests.

For up to seven holdout people, the scorer enumerates all person-block label permutations, including the identity permutation, preserving each person's complete window/category pattern. This is a diagnostic null distribution only: exchangeability, cohort matching, sufficient power and a declared hypothesis family still need scientific review. For larger cohorts this diagnostic is explicitly marked not computed; no misleading significance value is generated.

Compare rule versions using development errors and their declared changes, then measure generalization on fresh people. A score difference across different cohorts can reflect cohort difficulty; it is not automatically a causal benefit of the revised axiom. Predeclare fair comparison cohorts, baselines, multiple-testing treatment and stopping criteria before claiming improvement. No automated rule optimizer, cross-version significance test or model-weight fine-tuning is provided.

The graph export links studies, registered rules, private chart cases, frozen predictions, later labels and descriptive evaluations. It uses the existing `nodes`/`edges` interchange shape but is a separate private artifact; it does not silently merge unverified outcomes into the approved knowledge graph. Do not give this export back to the interpreter. Training and predictive-validation flags remain false.

## Verification

`python -m unittest discover -s tests -v` covers the full prepare/packet/commit/reveal/score/graph CLI on synthetic data, identity stripping, computed aspects, chart compatibility, complete predictions, immutable reports, label constraints, hand-calculated scores and exposed holdout rejection. No real-world blind accuracy result has been measured by these tests.