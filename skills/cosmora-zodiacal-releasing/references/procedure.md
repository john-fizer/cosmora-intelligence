# Cosmora Zodiacal Releasing

## Selected reconstruction and inputs

This release follows the named modern Brennan/Schaim reconstruction discussed in episode192, with ancient Valens references pending edition reconciliation. Required: verified birth instant in UTC, Fortune/Spirit longitudes, release_lot fortune or spirit, explicit horizon in days, levels1-4 and a period cap. UTC must be explicit. This is timing arithmetic; peak does not mean a favorable event.

1. Calculate sect-correct natal Lots first. Choose the Fortune or Spirit topic and freeze it. If both Lots occupy the same sign, move only Spirit's releasing start to the next sign. Preserve both original Lot longitudes and Fortune's reference sign.
2. Use sign allocations Aries15,Taurus8,Gemini20,Cancer25,Leo19,Virgo20,Libra8,Scorpio15,Sagittarius12,Capricorn27,Aquarius30,Pisces12. Do not substitute Capricorn30.
3. At L1 start in the selected releasing sign and advance zodiacally. Each allocation unit is360 days. At L2 use30 days; L3 uses2.5 days; L4 uses5 hours. These fixed units are not Gregorian years/months.
4. For each parent, seed its child sequence in the parent's sign. Children advance zodiacally within the actual parent interval. Preserve nominal ends and clip child ends to the parent's end. Separately label clipping by the requested observation horizon.
5. On lower levels, after the first full twelve-sign circuit, replace the would-be return to the seed sign with its opposite: Loosing of the Bond. Continue zodiacally from there. Apply at most once per parent; reset the state for each new parent. Do not apply this jump at L1.
6. Mark each period's house relative to natal Fortune. Fortune angular signs (1,4,7,10) are the named peak classification; record it separately from judgments of benefit/harm and from observed events.
7. Save every level, parent, sign, start/end, nominal end, LoB flag and clipping reason. Halt at the configured period cap. Keep alternative year lengths in separately versioned profiles; they are not implemented here.

## Synthetic check

Birth2000-01-01T00:00:00Z, Fortune10 Aries, Spirit70 Gemini, horizon7200days, levels2. Gemini L1 lasts7200days. The first child circuit totals211 allocation units=6330days. LoB begins Sagittarius at day6330 for360days; Capricorn starts day6690 and is clipped after510days by Gemini's end. When only the request ends early, label request clipping, not a fictitious parent boundary.

Use zodiacal-releasing. Freeze dates and predictions before outcome comparison; no retrospective reinterpretation of peaks as hits.

## Sources and review status

Source locators below are research references, not approved or independently reconciled editions. Original content hashes remain unset until permitted retrieval and review.

- `valens-riley`: {"url": "https://www.csus.edu/indiv/r/rileymt/Vettius%20Valens%20entire.pdf", "locator": "Valens Anthologies; Riley university-hosted draft; II.3/22 Lots, IV.4-10 releasing, VI.6 decennials. Direct PDF access failed in agent pass; indexed passages located.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
- `tap-zr192`: {"url": "https://theastrologypodcast.com/transcripts/ep-192-transcript-zodiacal-releasing-an-ancient-timing-technique/", "locator": "Brennan and Schaim, episode192, calculation, allocation, same-sign and Loosing of Bond discussions; named modern reconstruction.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
