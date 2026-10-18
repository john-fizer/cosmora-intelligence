# Cosmora Jaimini methods

## Inputs and convention lock

Require precomputed sidereal longitudes, named ayanamsha and ephemeris/longitude source, birth uncertainty, Whole Sign Ascendant and selected school. A provenance label alone does not verify astronomical correctness. For eight karakas require mean/true node_mode. Keep seven/eight-karaka conventions and PVR's2008 alternative distinct. Do not use tropical positions as sidereal inputs.

## Ordered delineation

1. Verify D1 and derive D9 using longitude_D9=(9*sidereal_longitude) mod360. Retain both physical and derived coordinates and boundary sensitivity.
2. Rank chara karakas using within-sign degrees of Sun,Moon,Mars,Mercury,Jupiter,Venus,Saturn. Seven roles descending: AK,AmK,BK,MK,PK,GK,DK. In the conventional eight scheme include Rahu with score30-within-sign-degree; roles AK,AmK,BK,MK,PiK,PK,GK,DK. Ketu, outer planets and Chiron are excluded from this ranking. Ordinary retrograde planets are not degree-reversed. The helper halts ties within1e-9 degrees as a conservative unresolved-rule policy; it does not claim this is universal ancient doctrine.
3. Compute rasi drishti as sign relationships, without degree orbs: movable signs aspect fixed signs except the next adjacent fixed sign; fixed signs aspect movable signs except the previous adjacent movable sign; dual signs aspect the other dual signs. Keep this separate from Parashari graha drishti.
4. Compute arudha under the explicitly named PVR textbook9.2 convention. Given source sign s and its resolved lord sign l, raw=(l+(l-s) mod12) mod12. If raw is s or its opposite, set result=raw+9 mod12; otherwise retain raw. Resolve Scorpio/Aquarius co-lord rules before calling; the helper does not decide them. AL uses house1, UL house12 under the selected school.
5. Derive karakamsha from AK's D9 sign. Explicitly select reading that sign within D9 versus projecting it as a reference Ascendant in D1. Neither is automatically the D9 Ascendant. Document all later house counting from the selected frame.
6. For argala, tabulate intervention/obstruction pairs2/12,4/10,11/3; separately tabulate secondary5/9 and8/6 if the selected school uses them. Record special third-house malefic rules, seventh/first and Ketu reversals only with the exact school citation. Equal counts require a documented strength hierarchy; do not invent a winner. This is procedure-only, not an implemented complete resolution engine.
7. Record yogas and contradictory testimony with source-specific definitions. Freeze the topic hypotheses before adding a named, verified dasha schedule and before revealing events.

## Checks and unresolved timing

Aries with Mars in Gemini gives Leo arudha; Mars in Aries gives Capricorn; Mars in Cancer gives Cancer; Mars in Libra gives Capricorn. These check the chosen textbook exception, not every lineage.

The older Jaimini Sutras translation attribution and edition need review. PVR2008 karaka proposals are separate from the conventional schemes. PVR2014 Chara Dasa is an innovative Parashari variant, not a universal Jaimini algorithm: seed, co-lord strength, ninth-sign direction, inclusive counts, dignity adjustments, year conversion and subdivisions must all be formalized together. Its antardasha rules are omitted in the cited paper. Chara, Narayana, Sthira and Shoola dashas remain research-only. Stop an execution request at these gaps; do not borrow a missing rule from another school.

Use registered chara-karakas, rasi-drishti and arudha-pvr-textbook with jaimini-sidereal-v1. Include ayanamsha_id and longitude_source in each input; scheme eight additionally needs node_mode. Karakamsha and argala remain manual procedures.

## Sources and review status

Source locators below are research references, not approved or independently reconciled editions. Original content hashes remain unset until permitted retrieval and review.

- `jaimini-older`: {"url": "https://www.shanti-ganesha.com/classic/jaimini-sutras.pdf", "locator": "Older English Jaimini Sutras commentary;1.1.2-4 aspects,1.1.11ff karakas,1.1.29-31 arudha,1.2.1 navamsa. Translation attribution/title page requires edition verification.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
- `pvr-textbook`: {"url": "https://www.vedicastrologer.org/articles/vedic_astro_textbook.pdf", "locator": "PVR Narasimha Rao, Vedic Astrology Integrated Approach;6.2.9 D9,8.2 karakas,9.2 arudha,10.3 rasi aspects,16.2-3 Vimshottari. Author-hosted; later refinements explicitly acknowledged.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
- `pvr-karaka2008`: {"url": "https://www.vedicastrologer.org/articles/c_karaka.pdf", "locator": "PVR2008-10-24 independent interpretation,pp1-4; distinct from conventional seven/eight schemes.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
- `pvr-chara2014`: {"url": "https://vedicastrologer.org/articles/pp_chara_dasa.pdf", "locator": "PVR2014-04-14 v1,pp3-4; innovative Parasara Chara Dasa; seed/co-lord/duration rules; antardashas omitted.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
- `srath-argala`: {"url": "https://srath.com/jyoti%E1%B9%A3a/amateur/argala-planetary-intervention/", "locator": "Sanjay Rath Argala: Planetary Intervention; primary, secondary and special intervention sections.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
- `srath-ak`: {"url": "https://srath.com/jyoti%E1%B9%A3a/scholar/atmakaraka-karakamsa/", "locator": "Sanjay Rath Atmakaraka and Karakamsa; opening definition and AK relative to Lagnamsa.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
- `jh-features`: {"url": "https://www.vedicastrologer.org/jh/features.htm", "locator": "Author software feature inventory; documents alternative dashas/year models, not sufficient proof of each algorithm.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
