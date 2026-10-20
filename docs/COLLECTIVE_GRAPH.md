# Collective chart graph

The collective layer creates one canonical configuration identity across people. A shared node keeps distinct people, person-year windows and source records; exact positions remain attached to the originating charts. It does not flatten everyone's coordinates into a fictional natal chart.

The current adapter consumes the five-person Western pilot. Earlier pilot cohorts and the wider candidate list are not silently included. Further adapters must preserve their different protocols, event vocabularies and missing-label rules.

## Rebuild and retrieve

From the repository root:

```powershell
python -m cosmora.collective build --input data/western-pilot-v1 --dashboard
python -m cosmora.collective query --input data/western-pilot-v1 --house 8 --minimum-people 2 --limit 10
python -m cosmora.collective query --input data/western-pilot-v1 --person max_born --topic nobel_award --limit 5
```

Generated private artifacts live in `data/western-pilot-v1/collective/`: `graph.json`, `concepts.json`, `cases.json`, `evidence.json`, `manifest.json`, and `retrieval-documents.jsonl`. The dashboard opens in Collective brain mode; Chart relationship view remains an alternate projection. Explorer sources are under `web/collective/`. No private research data or birth records are committed with those assets.

## Shared identities

- Natal configuration: planet/point + sign + natal Whole Sign house. Exact degrees remain in source evidence.
- Transit pattern: transit point + aspect + natal point + natal house. Natal sign and transit-house variations remain in source cases rather than becoming invented constants of the pattern.
- Profection configuration: activated house + sign + traditional lord.
- Dispositor chain: named ruler profile + ordered path. Traditional and modern chains remain separate, including when they have the same path.
- Releasing configuration: selected Lot + level + sign. Fortune-relative houses are not merged with natal house concepts.

A pattern's ID excludes person identity. `PRESENT_IN` links and evidence indexes preserve supporting windows. Shared house, sign, point, aspect and outcome-category nodes connect the configuration layer. Event and non-event edges retain the official registry source. Birth sources and original artifact hashes remain provisional; these graph exports do not approve historical claims.

## Counts and limitations

Counts use distinct people and distinct person-year windows. Twelve monthly samples are not twelve independent events. A pattern occurring several times in a window counts as one present window. Missing outcomes cause an error; they are not converted to negative labels. Duplicate aggregated contact pairs are rejected.

Each configuration records four descriptive counts for each outcome: event/non-event windows with the configuration, and event/non-event windows without it. A zero denominator produces a null rate. These repeated windows and configurations are dependent. This post-reveal graph is exploratory; it does not produce significance tests, causal effects or new predictive validation. Original frozen predictions and their scores remain unchanged.

Person filters keep shared IDs and restrict supporting evidence. Minimum cohort people is a cohort-wide threshold, so selecting one contributor does not erase a configuration that is shared across the cohort. House filters use case-specific house lineage. Releasing configurations without natal-house evidence do not appear simply because their Fortune-relative house matches.

The JSONL documents provide deterministic text and provenance for retrieval. They are not embeddings, an LLM narrative, a JEPA model or a trained RAG service. Any later narrative must cite the underlying cases and preserve counterexamples and uncertainty.

## Verification

`python -m unittest discover -s tests` includes shared identity, distinct counts, counterexample denominators, source filtering, missing-label rejection and graph references. The pilot's local `test_explorer.cjs` tests the UI functions with a DOM test double; it is not a visual browser test. Automated file-page browser access was previously denied and has not been bypassed.
