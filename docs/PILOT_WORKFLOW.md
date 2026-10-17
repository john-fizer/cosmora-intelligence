# Five-person event/transit pilot and analyst annotations

This is a working computational pilot, not an approved research corpus or empirical correlation result.

## Workflow

1. Select five source-linked people and explicit natal inputs. Preserve local clock convention, offset, derived historical UT, coordinates, publisher quality classification and unresolved provenance.
2. Collect five public professional events per subject independently of chart outcomes. Distinguish occurrence, publication, premiere, ceremony, announcement, interval and award year.
3. Calculate provisional tropical Whole Sign natal charts with modern sign rulers, Chiron and both true and mean node variants.
4. For day/range-only events without verified timezone or clock time, construct a conservative civil-date envelope with 14 hours of expansion on each side. Sample every six hours and include endpoints.
5. Place the transiting bodies in the natal Whole Sign houses. Do not publish calculated event-location houses or angles from an unknown event location/time.
6. Compare the 15 transit points with the 17 natal points and angles. Initial exploration uses conjunction, sextile, square, trine and opposition with a uniform three-degree orb.
7. Record individual samples and grouped contacts, then attach pending analyst annotations with source and calculation references.
8. Review primary evidence, timing, calculation accuracy and matched controls before scaling the verified cohort.

## Commands

Supply your local input files; they are not bundled with source code:

    python -m cosmora.pilot --people data/pilot5/inputs/people.json --events data/pilot5/inputs/events.json --ephe-path data/ephemeris --output data/pilot5
    python -m cosmora.annotations --output data/pilot5 --annotations data/pilot5/inputs/agent-report.json

Run the annotation command after replaying the pilot to refresh its annotation page/link and final counts.

Open data/pilot5/index.html for natal SVGs, all sampled event charts, event records, and house/person/category filters. The amber dots in transit SVGs are natal positions; teal dots are transit samples. Table positions and houses describe transits through natal houses.

## Records and provenance

pilot.db extends the existing graph/chart tables with pilot_birth_inputs, pilot_events, pilot_transit_frames, pilot_aspect_samples, pilot_run_policy, pilot_extra_nodes, pilot_extra_edges and pilot_agent_annotations.

graph.json includes the provenance/calculation graph plus sampled aspect edges, category links and pending analyst nodes. CSV/JSON exports retain exact values and source URLs. Research and pilot artifacts stay local in the ignored data directory.

A comparison/sampling policy is immutable within one output database. A different orb or aspect set requires a new output directory; incompatible reruns are rejected. Existing records are not silently reinterpreted under new settings.

Agent annotations must identify a saved event, its natal chart, matching event source and exact computed contact values. Orb, house and sample-count references are checked before graph insertion. Non-finite or changed values are rejected. This validates numerical references only, not narrative truth, primary historical evidence or astrological interpretation. Changed annotations require a new revision ID.

## Interpretation limits

An event sample is not the event's exact timestamp. Minimum sampled orb is not the continuous-time minimum. Presence in every sampled frame is not a guarantee across the entire interval. Sampling counts are neither confidence values nor independent events. Longer windows naturally provide more opportunities for contacts.

True/mean nodes are alternative representations; do not count them as independent discoveries. Public film-release events do not imply personal attendance. A house placement does not establish that a traditional house topic happened.

The initial annotations use selected examples, not an unbiased statistical discovery procedure. All remain pending review and training-ineligible. No baseline, holdout or significance test has passed.

## Additional technique layers

Dispositor chains, secondary progressions, annual profections, Zodiacal Releasing and Loosing of the Bond, decan rulership, source-backed topic ontology, validated story-arc models and RAG generation remain future work. Each calculation layer needs a named method/profile, source-aware settings, independent reference cases and typed outputs. Narrative hypotheses and doctrine must remain separate from observations and tested associations.
