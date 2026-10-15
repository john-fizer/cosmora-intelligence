# Two brains, one research system

## Brain A: Historical Evidence Graph (HEG)
Source-backed birth records, biographies, events, precise dates, calculated configurations, and counterexample windows. The graph records *what is documented*, not astrological significance.

## Brain B: Astrological Doctrine Graph (ADG)
Canonical vocabulary (planets, signs, houses, rulerships, aspects, dignities, techniques), interpretation statements with attributed tradition, edition/page/source, contradictory schools, and formalized rule expressions. Interpretations are propositions attributed to texts, **not factual causal edges**.

## Joining them
A hypothesis layer asks whether a doctrine rule matches historical observations. It stores proposed associations, tests, effect sizes, baselines, and failures. This is not a third source-of-truth graph.

## Orchestration
Research director -> birth-source agent -> independent birth auditor -> event discovery -> event verification -> entity resolver -> calculation service -> independent calculation audit -> graph ingest -> ML dataset builder -> baseline scientist -> graph/JEPA scientist -> red-team scientist -> model registry.

All agent messages are typed. No agent may mark its own outputs verified. Human review is required for unresolved conflicts. Deterministic tools, not LLMs, calculate chart positions.

## ML sequence
1. Collect verified corpus and negative person-time windows.
2. Freeze event ontology and sampling protocol.
3. Split by **person**, plus time-based prospective simulation where applicable.
4. Establish age/calendar/publicity and other non-astrological baselines.
5. Test doctrine-derived features, graph features, and JEPA-style representations as distinct ablations.
6. Use held-out evaluation, correction for multiple comparisons, calibration, and replication before deployment.

## Product integration
Cosmora API reads immutable graph versions and model registry entries; personal graph remains separate. Observations, predictions, and postdictions have different types. No feedback silently retrains production models.

## Suggested production stack
PostgreSQL + typed edge tables (start), optional graph database if traversal needs justify it; object storage with SHA-256; workflow engine (e.g. Temporal); Pydantic contracts; Swiss Ephemeris with licensing review; PyTorch for ML; FastAPI for product interface. Keep database and evidence locally initially.
