# Local charts and knowledge graph

The optional chart pipeline extends the SQLite starter with pending research tables, calculated chart placements, typed graph nodes/edges, CSV exports, searchable HTML tables and an SVG natal chart.

## Run

The original init/demo/audit commands still require only the standard library. Chart calculation additionally requires pyswisseph; the locally tested binding is 2.10.3.2 (Swiss Ephemeris 2.10.03).

Install the optional dependency in your chosen environment:

    python -m pip install -r requirements-ephemeris.txt

Provide the official sepl_18.se1, semo_18.se1 and seas_18.se1 files in data/ephemeris. They cover 1800–2399 for this implementation. Files are hashed and required; planetary fallback to Moshier is rejected. Mean-node positions are analytical. Automatic file downloading is not performed by the reusable command.

Run from the repository root, substituting the paths to your local research artifacts and user-confirmed example:

    python -m cosmora.knowledge bootstrap --cohort data/inputs/cohort.json --events data/inputs/events.json --example data/inputs/confirmed-reference.json --ephe-path data/ephemeris --output data

The research and example input files are private local artifacts, not bundled fixtures. Open data/index.html after the command finishes.

## Calculation profile

- Tropical, geocentric apparent ecliptic positions of date.
- Whole Sign houses; Ascendant and MC are retained separately.
- Sun through Pluto, Chiron, both true and mean North Nodes and their opposing South Nodes.
- Longitude, sign, degrees within sign, house, decan number, speed, retrograde status and returned calculation flags.
- Modern sign rulers: Scorpio–Pluto, Aquarius–Uranus, Pisces–Neptune. Other sign rulers follow the usual mapping.
- Decans are the three half-open ten-degree sections [0,10), [10,20), [20,30). Decan rulers remain unassigned until a rulership system is selected.
- Input times must already be converted to explicit UTC; this version does not infer historical time zones or missing birth times.
- Engine/binding versions, input data, profile and ephemeris SHA-256 hashes identify each deterministic chart run.

The example regression compares positions and angles to the user's confirmed local reference within one arcsecond. That checks reproducibility, not independent astronomical accuracy. All other calculate_chart() results default to calculated_unverified.

## Storage and outputs

data/research.db contains research_subjects, research_event_leads and their provenance graph. Imports force pending status and training ineligibility. Existing sourced claims, calculations and hypothesis tables are preserved; pending discoveries are not inserted as verified claims.

data/personal.db contains the user-supplied example, chart_runs, chart_placements and its separate placement graph. Personal rows are never added to the shared research cohort. Chart calculations remain ineligible for training.

data/research and data/personal hold graph.json, graph.html and a CSV per new table. The personal directory also holds natal.json and natal.svg. data/run.json records counts and calculation status; data/index.html links the outputs.

Graph relationships are HAS_SOURCE_LEAD, HAS_EVENT_LEAD, CHART_FOR, HAS_PLACEMENT, IN_SIGN and IN_HOUSE. These encode sources and calculated placement, not causal or empirical astrological claims. Rulership labels are configuration/vocabulary. Doctrine remains separate.

Imports are replayable without duplicates. Changed records or conflicting identity IDs are rejected rather than silently replacing provenance; a reviewed revision workflow remains future work. Input and export files remain local under the Git-ignored data directory.

## Remaining research work

The first 100 people and 10 event leads remain pending independent evidence verification. Event charts stay queued until adequate birth records and event time precision are available. No midnight/noon timestamps, uncertain houses, aspect claims or observed outcomes are invented. Transit comparisons, date-uncertainty sampling, independent astronomical reference checks and evidence approval workflows are not yet implemented.

## Verify

    python -m unittest discover -s tests -v

The tests cover Whole Sign and decan boundaries, pending-status preservation, graph/table consistency, duplicate rejection, replay stability, missing ephemeris data, explicit UTC requirements and SVG escaping. The optional calculation dependency is imported only for actual chart runs; the standard test suite runs without downloading ephemeris files.
