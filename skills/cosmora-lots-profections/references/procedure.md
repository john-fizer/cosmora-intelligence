# Cosmora Lots and profections

## Fortune and Spirit

Inputs: Ascendant A, Sun S, Moon M ecliptic longitudes and separately verified sect. All outputs normalize modulo 360. Day: Fortune=A+M-S; Spirit=A+S-M. Night: Fortune=A+S-M; Spirit=A+M-S. Preserve a non-reversing Ptolemaic Fortune rule as a separate unimplemented variant, never a silent substitution.

1. Verify the birth instant and horizon-based sect; report uncertainty near sunrise/sunset.
2. Calculate both Lots using the chosen reversal convention.
3. Record longitude, sign, Whole Sign house and ruler for each Lot. Preserve natal longitudes when another technique changes its starting sign.
4. Interpret Lot houses or derived Fortune houses only under an explicitly cited rule. The derived-house engine remains research-only.

Synthetic day example A=10, S=40, M=100: Fortune=70 Gemini; Spirit=310 Aquarius. Night exchanges these results.

## Annual Whole Sign profections

Inputs: Ascendant sign index a (Aries=0), completed calendar age n (nonnegative integer). Birth through the first birthday is age zero.

1. Determine age upstream using an explicit birthday versus solar-return boundary and leap-day policy. Do not approximate with days/365.25.
2. Activated house=(n mod 12)+1; activated sign=(a+n) mod 12.
3. Select the traditional domicile lord of that sign as annual lord; retain the modern ruler as a separate overlay only if requested.
4. Examine the annual lord's natal house, condition and rulership, then prespecified transit/return contacts. Record each layer rather than averaging incompatible methods.
5. Freeze the year's topic hypotheses before comparing events. Monthly profections require their own subdivision and boundary policy and remain research-only.

Synthetic example Leo rising a=4, age26 activates house3, Libra and Venus. Use hermetic-lots and annual-profections through the registered CLI. Output the arithmetic, sect/age provenance, ruler and boundary assumptions.

## Sources and review status

Source locators below are research references, not approved or independently reconciled editions. Original content hashes remain unset until permitted retrieval and review.

- `ptolemy-iv`: {"url": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/4C%2A.html", "locator": "Tetrabiblos IV.10 Of the Division of Times; distinguish annual movement and subdivisions.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
- `valens-riley`: {"url": "https://www.csus.edu/indiv/r/rileymt/Vettius%20Valens%20entire.pdf", "locator": "Valens Anthologies; Riley university-hosted draft; II.3/22 Lots, IV.4-10 releasing, VI.6 decennials. Direct PDF access failed in agent pass; indexed passages located.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
- `tap-prof153`: {"url": "https://theastrologypodcast.com/transcripts/ep-153-annual-profections-an-ancient-time-lord-technique/", "locator": "Brennan episode153; annual profection age and house activation; modern reconstruction.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
