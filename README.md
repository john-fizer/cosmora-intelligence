# Cosmora Intelligence

Cosmora Dual Knowledge Graph Research Engine — v0.1.

A runnable **local-first proof of architecture**, not a populated or scientifically validated research corpus. Two separate graphs share a typed ontology:

1. **Historical Evidence Graph (HEG)**: sourced birth facts, dated biographical events, verified calculation states, derived features and provenance.
2. **Astrological Doctrine Graph (ADG)**: sourced traditional interpretations, school/tradition, source passages, rules and counterinterpretations. Doctrine is **not** empirical evidence.

A comparison/evaluation service can join the graphs **only via a hypothesis record**. It must never promote a doctrine claim into an observed fact.

## Requirements and setup

Use Python 3.12 or later and Git. Python 3.12, 3.13, and 3.14 are checked in CI on Windows and Linux. The engine uses only the Python standard library; no third-party packages or installation step are required. Run commands from the repository root.

Windows PowerShell:

```powershell
git clone https://github.com/john-fizer/cosmora-intelligence.git
cd cosmora-intelligence
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m cosmora.cli init --db cosmora.db
.\.venv\Scripts\python.exe -m cosmora.cli demo --db cosmora.db
.\.venv\Scripts\python.exe -m cosmora.cli audit --db cosmora.db
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Calling the virtual environment's Python directly avoids requiring a PowerShell activation script. If the Windows `py` launcher is unavailable, use `python -m venv .venv` instead.

macOS/Linux:

```bash
git clone https://github.com/john-fizer/cosmora-intelligence.git
cd cosmora-intelligence
python3 -m venv .venv
.venv/bin/python -m cosmora.cli init --db cosmora.db
.venv/bin/python -m cosmora.cli demo --db cosmora.db
.venv/bin/python -m cosmora.cli audit --db cosmora.db
.venv/bin/python -m unittest discover -s tests -v
```

## CLI

With your chosen Python interpreter:

```bash
python -m cosmora.cli init --db cosmora.db
python -m cosmora.cli demo --db cosmora.db
python -m cosmora.cli audit --db cosmora.db
python -m unittest discover -s tests -v
```

`init` creates the SQLite schema. `demo` adds **explicitly fictional data** and keeps it quarantined; it does not claim to research actual people. `audit` prints a JSON summary. On a fresh demo database, expect two claims (one historical and one doctrine), one hypothesis, no eligible historical claims, and one blocked fictional claim. Running the demo again preserves those counts.

Database files, SQLite journal/WAL files, virtual environments, and Python caches are ignored by Git. Research data stays local.

## Design and research documents

- [Architecture](docs/ARCHITECTURE.md): graph separation, hypothesis layer, and proposed production stack.
- [Agent contracts](docs/AGENT_CONTRACTS.md): worker responsibilities and evidence, computation, training, and scientific gates.
- [Research protocol](docs/RESEARCH_PROTOCOL.md): staged corpus development and experimental evaluation.

These documents describe the intended system. The core implements a minimal SQLite schema, a fictional demo, and claim eligibility checks. The optional chart pipeline adds pending research graphs, chart calculations and local exports. Full orchestration, independent evidence verification and the proposed production stack remain future work.

## Validation

GitHub Actions runs the supplied unittest suite and CLI smoke checks on pushes and pull requests. Smoke checks create a temporary database, run `init`, run `demo` twice, run `audit`, and verify expected counts and fictional-data exclusion.

## Important boundaries

- No automated web crawling is performed in v0.1. Real source adapters must be added with terms-of-use, robots, rate limits, and copyright handling.
- No birth time may be inferred from chart interpretation.
- No LLM may calculate ephemeris positions or approve its own evidence.
- No model training should begin until audited data, negative windows, and person-level held-out sets exist.
- The core requires only the Python standard library. The optional chart pipeline uses pyswisseph and external ephemeris data; orchestration and ML remain future work.


## Local chart and graph pipeline

The optional pipeline now imports pending research leads, stores reproducible Whole Sign chart calculations, and exports graph data, CSV tables and a saved SVG chart. Personal charts use a separate database. See [Local charts and knowledge graph](docs/CHART_PIPELINE.md) for setup, commands, calculation settings and verification limits. Research data and generated charts remain local in the ignored data directory.

See [Five-person pilot and analyst annotations](docs/PILOT_WORKFLOW.md) for sampled event transits, natal comparisons, house filters and provenance-linked agent augmentation.

See [Blinded interpretation and calibration](docs/BLINDED_EVALUATION.md) for anonymous chart packets, frozen rule-based predictions, independent event labels, baseline scoring, private graph exports and fresh-person validation of revised interpretations.

See [Technique and reusable skill library](docs/TECHNIQUE_LIBRARY.md) for source-attributed Hellenistic, Jaimini/Jyotish, degree-system and Eastern-framework procedures, calculation helpers and explicit research gaps.

See [Collective chart graph](docs/COLLECTIVE_GRAPH.md) for shared cross-person configurations, case/source lineage, descriptive event and counterexample counts, retrieval documents and the collective explorer.
