# Agent contracts and gates

Each worker returns: `job_id`, `agent_name`, `agent_version`, `input_ids`, `candidate_claims`, `source_ids`, `conflicts`, `uncertainties`, `status`, `timestamp`.

- **Subject selector**: diverse candidate cohort; no cherry-picking based on event outcome.
- **Birth researcher**: locate primary/secondary birth documentation; retain exact quoted evidence, time precision and Rodden rating provenance.
- **Birth auditor**: independent source inspection; cannot use researcher paraphrase as proof.
- **Event researcher**: discover events and exact date types; capture provenance.
- **Event auditor**: check independent sources, event ontology, precision, duplicates and retractions.
- **Doctrine librarian**: collect legitimately accessible texts and formalize attributed rules; distinguish authors/traditions and disagreements.
- **Doctrine auditor**: independently check quotations, page references and rule formalizations.
- **Calculation service**: deterministic ephemeris only, pinned versions, UTC conversions, explicit house and zodiac settings.
- **Calculation auditor**: independent golden cases, edge cases, precision checks.
- **Graph builder**: ingest approved claims only; append revisions, never overwrite provenance.
- **ML scientist**: construct person-time datasets, negatives and controls; run baselines and ablations.
- **Red-team scientist**: independently test leakage, selection bias, spurious correlations and false discovery.

## Hard gates
G1 Evidence: no accepted factual claim without a resolvable source, content hash, supporting passage, independent reviewer.
G2 Computation: no chart feature without a reproducible deterministic calculation and versioned inputs.
G3 Training: no unverified, fictional, disputed, or doctrine claims as observed event labels.
G4 Scientific: no promoted predictive model without untouched holdout, preregistered targets, baseline comparison and calibration.

## Adversarial fixtures
Invented citation; 2 copies of same syndicated story; ambiguous birth time; date-only birth; event with uncertain year; contradictory records; retroactively dated prediction; famous-person biography leaked into prompt; doctrine rule incorrectly labeled empirical fact.
