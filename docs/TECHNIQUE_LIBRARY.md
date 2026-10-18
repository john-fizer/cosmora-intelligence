# Cosmora technique and skill library

This first release adds nine reusable agent skills, 57 method entries and 33 source locators. Thirteen methods have local arithmetic helpers. It is an expandable inventory, not exhaustive coverage of every tradition.

## Skills

- [Ordered natal delineation and Western timing research](../skills/cosmora-delineation/SKILL.md) — `$cosmora-delineation`
- [Traditional and modern dispositor chains](../skills/cosmora-dispositors/SKILL.md) — `$cosmora-dispositors`
- [Fortune, Spirit and annual whole-sign profections](../skills/cosmora-lots-profections/SKILL.md) — `$cosmora-lots-profections`
- [Zodiacal Releasing and Loosing of the Bond](../skills/cosmora-zodiacal-releasing/SKILL.md) — `$cosmora-zodiacal-releasing`
- [Jaimini delineation, karakas, sign aspects and padas](../skills/cosmora-jaimini/SKILL.md) — `$cosmora-jaimini`
- [Jyotish subdivisions and Vimshottari primitives](../skills/cosmora-jyotish/SKILL.md) — `$cosmora-jyotish`
- [Decans, twelfth parts, bounds and degree doctrines](../skills/cosmora-degree-systems/SKILL.md) — `$cosmora-degree-systems`
- [Chinese calendrical systems and philosophical concepts](../skills/cosmora-eastern-frameworks/SKILL.md) — `$cosmora-eastern-frameworks`
- [Research and formalize additional techniques](../skills/cosmora-technique-research/SKILL.md) — `$cosmora-technique-research`

## Run the registered methods

Run from the Cosmora checkout with Python:

```powershell
python -m cosmora.techniques list
python -m cosmora.techniques show --method zodiacal-releasing
python -m cosmora.techniques calculate --method annual-profections --profile hellenistic-traditional-v1 --input INPUT.json --output RESULT.json
python -m cosmora.techniques graph --output GRAPH.json
```

For the profection example, INPUT.json can contain `{"asc_sign_index":4,"completed_age":26}`: Leo rising at completed age 26 activates house 3, Libra, Venus. Dates and calendar-age boundaries remain caller responsibilities.

For releasing, INPUT.json can contain `{"start_utc":"2000-01-01T00:00:00Z","days":7200,"fortune_longitude":10,"spirit_longitude":70,"release_lot":"spirit","levels":2}`. The named reconstruction uses fixed 360-day years, Capricorn 27 and Aquarius 30, with explicit LoB and parent/request boundaries. This is a synthetic example, not a prediction.

Jyotish/Jaimini helpers require precomputed sidereal positions plus textual `ayanamsha_id` and `longitude_source`; eight-karaka runs also require `node_mode` of `mean` or `true`. The existing natal ephemeris engine remains tropical. No native sidereal chart adapter or complete Chinese calendrical engine is included.

Synthetic runnable inputs for every implemented method are in [methods/examples](../methods/examples). For example, run `python -m cosmora.techniques calculate --method zodiacal-releasing --profile hellenistic-traditional-v1 --input methods/examples/zodiacal-releasing.json --output RESULT.json`. These are arithmetic fixtures, not historical charts or event evidence.

## Status and provenance

- `implemented_arithmetic`: 13
- `interpretation_only`: 3
- `procedure_only`: 3
- `research_only`: 38

`implemented_arithmetic` means synthetic reference calculations pass. It does not establish source approval, independent astronomical validation, or predictive accuracy. `procedure_only` supplies an ordered method without a complete engine. `research_only` records specific gaps and refuses execution. `interpretation_only` preserves attributed symbolic/philosophical material.

Calculation records bind method definition, profile, inputs and implementation hash. They retain source IDs, pending review, no empirical validation and training ineligibility. The registry graph contains doctrine-method, source-reference and profile nodes; it does not promote them to observed historical events.

Current modern tropical Whole Sign defaults remain available separately from historical traditional-ruler profiles. Decan rulership is chosen explicitly for the relevant technique rather than retroactively changing old natal charts.

Source records retain a null original-content hash until permitted source retrieval and independent review. Some author pages or primary PDFs were unavailable; these access limitations are preserved. Do not treat the source catalog as an approved textual corpus.

Stojanovic degree theory needs an authorized primary indexing/exception source. Sabian symbols require named edition/indexing and permitted excerpts; complete copyrighted dictionaries are not bundled. Chara Dasha, primary directions and Chinese systems retain unresolved algorithm/calendar branches.

Vimshottari currently supplies birth balance and full-parent antardasha fractions in abstract dasha years. A dated engine requires a fixed-day, astronomical or tithi-based year model plus independent fixtures.

## Catalog

| Method | Status | Tradition | Procedure |
|---|---|---|---|
| `natal-delineation` | procedure_only | Hellenistic | [skill](../skills/cosmora-delineation/SKILL.md) |
| `dispositor-chains` | implemented_arithmetic | Western | [skill](../skills/cosmora-dispositors/SKILL.md) |
| `hermetic-lots` | implemented_arithmetic | Hellenistic | [skill](../skills/cosmora-lots-profections/SKILL.md) |
| `annual-profections` | implemented_arithmetic | Hellenistic reconstruction | [skill](../skills/cosmora-lots-profections/SKILL.md) |
| `zodiacal-releasing` | implemented_arithmetic | Brennan-Schaim reconstruction | [skill](../skills/cosmora-zodiacal-releasing/SKILL.md) |
| `chaldean-decans` | implemented_arithmetic | Traditional Western | [skill](../skills/cosmora-degree-systems/SKILL.md) |
| `triplicity-decans` | implemented_arithmetic | Named zodiacal decan profile | [skill](../skills/cosmora-degree-systems/SKILL.md) |
| `dodecatemoria` | implemented_arithmetic | Named historical variant | [skill](../skills/cosmora-degree-systems/SKILL.md) |
| `nakshatra-pada` | implemented_arithmetic | Jyotish | [skill](../skills/cosmora-jyotish/SKILL.md) |
| `navamsa` | implemented_arithmetic | Jyotish | [skill](../skills/cosmora-jyotish/SKILL.md) |
| `chara-karakas` | implemented_arithmetic | Jaimini named profiles | [skill](../skills/cosmora-jaimini/SKILL.md) |
| `rasi-drishti` | implemented_arithmetic | Jaimini | [skill](../skills/cosmora-jaimini/SKILL.md) |
| `arudha-pvr-textbook` | implemented_arithmetic | PVR textbook9.2 named convention | [skill](../skills/cosmora-jaimini/SKILL.md) |
| `vimshottari-birth-balance` | implemented_arithmetic | Jyotish | [skill](../skills/cosmora-jyotish/SKILL.md) |
| `sect` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `house-rulers` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `essential-dignities` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `triplicity-rulers` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `sign-configurations` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `application-separation` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `planetary-conditions` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `egyptian-bounds` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `ptolemaic-bounds` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `fortune-derived-houses` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `monthly-profections` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `primary-directions` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `distributions-bounds` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `circumambulations` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `decennials` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `natural-ages` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `prenatal-syzygy` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `secondary-progressions` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `solar-returns` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `solar-arcs` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `firdaria` | research_only | Western named tradition | [skill](../skills/cosmora-delineation/SKILL.md) |
| `karakamsha` | procedure_only | Jaimini and related sign-dasha schools | [skill](../skills/cosmora-jaimini/SKILL.md) |
| `argala` | procedure_only | Jaimini and related sign-dasha schools | [skill](../skills/cosmora-jaimini/SKILL.md) |
| `jaimini-chara-dasha` | research_only | Jaimini and related sign-dasha schools | [skill](../skills/cosmora-jaimini/SKILL.md) |
| `karaka-pvr2008` | research_only | Jaimini and related sign-dasha schools | [skill](../skills/cosmora-jaimini/SKILL.md) |
| `narayana-dasha` | research_only | Jaimini and related sign-dasha schools | [skill](../skills/cosmora-jaimini/SKILL.md) |
| `sthira-dasha` | research_only | Jaimini and related sign-dasha schools | [skill](../skills/cosmora-jaimini/SKILL.md) |
| `shoola-dasha` | research_only | Jaimini and related sign-dasha schools | [skill](../skills/cosmora-jaimini/SKILL.md) |
| `jaimini-yogas` | research_only | Jaimini and related sign-dasha schools | [skill](../skills/cosmora-jaimini/SKILL.md) |
| `sidereal-ephemeris` | research_only | Jyotish | [skill](../skills/cosmora-jyotish/SKILL.md) |
| `vimshottari-dated` | research_only | Jyotish | [skill](../skills/cosmora-jyotish/SKILL.md) |
| `panchanga` | research_only | Jyotish | [skill](../skills/cosmora-jyotish/SKILL.md) |
| `ashtottari-dasha` | research_only | Jyotish | [skill](../skills/cosmora-jyotish/SKILL.md) |
| `yogini-dasha` | research_only | Jyotish | [skill](../skills/cosmora-jyotish/SKILL.md) |
| `ashtakavarga` | research_only | Jyotish | [skill](../skills/cosmora-jyotish/SKILL.md) |
| `shadbala` | research_only | Jyotish | [skill](../skills/cosmora-jyotish/SKILL.md) |
| `graha-drishti` | research_only | Jyotish | [skill](../skills/cosmora-jyotish/SKILL.md) |
| `stojanovic-degree-theory` | research_only | Modern author-specific | [skill](../skills/cosmora-degree-systems/SKILL.md) |
| `sabian-symbols` | interpretation_only | Modern author-specific | [skill](../skills/cosmora-degree-systems/SKILL.md) |
| `bazi` | research_only | Chinese named systems | [skill](../skills/cosmora-eastern-frameworks/SKILL.md) |
| `zi-wei-dou-shu` | research_only | Chinese named systems | [skill](../skills/cosmora-eastern-frameworks/SKILL.md) |
| `yin-yang-wuxing` | interpretation_only | Chinese named systems | [skill](../skills/cosmora-eastern-frameworks/SKILL.md) |
| `i-ching` | interpretation_only | Chinese named systems | [skill](../skills/cosmora-eastern-frameworks/SKILL.md) |

## Use in research and blinded experiments

Select a method/profile and read its skill before building features. Obtain checked astronomical/calendrical inputs, run supported arithmetic, attach source-attributed interpretation separately, and freeze method versions and predictions before outcome disclosure. Technique agreement is not automatically independent evidence. Rule revisions belong to development work; predictive claims require fresh held-out evaluation.

The source references in each procedure identify tradition, author/translator and exact section or titled technical passage. Cosmora editorial sequences are labeled as working procedures rather than falsely attributed to one universally agreed ancient reading order.

## Current selection preference

Eastern philosophical concepts remain in scope. BaZi is deferred and retained only as optional research; exclude it from default chart readings, feature generation and comparisons unless explicitly requested. No BaZi engine is enabled.
