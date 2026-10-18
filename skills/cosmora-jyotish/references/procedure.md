# Cosmora Jyotish primitives

## Astronomical prerequisites

Require a verified sidereal longitude source, named ayanamsha, UTC conversion and uncertainty. For production Swiss Ephemeris use its native sidereal mode and sidereal flag with documented settings; do not silently subtract an ayanamsha from an unrelated tropical coordinate. The current Cosmora natal adapter remains tropical. These helpers accept supplied sidereal coordinates and do not verify their provenance claims.

## Divisions

1. Normalize sidereal longitude lambda to[0,360). Use half-open boundaries; exact boundaries enter the next division, without rounding beforehand.
2. Nakshatra index=floor(3*lambda/40), zero-based Ashwini first. Width13degrees20minutes. Pada=floor(3*lambda/10) mod4+1. Record the fractional distance through the nakshatra.
3. Navamsa derived longitude=(9*lambda) mod360. Its sign gives D9 placement; its degree is a transformed coordinate, not the planet's physical longitude. Preserve birth-time uncertainty for divisional Ascendants.
4. Synthetic lambda16degrees40minutes lies in Bharani, pada2 and D9 Virgo0. Taurus28degrees (lambda58) maps to D9 Virgo12.

## Vimshottari birth balance

1. Select the Moon's sidereal nakshatra. Repeat lords Ketu,Venus,Sun,Moon,Mars,Rahu,Jupiter,Saturn,Mercury with years7,20,6,10,7,18,16,19,17 (sum120).
2. Let f be fractional nakshatra elapsed. The current major lord's full length Y has elapsed f*Y; birth balance=(1-f)*Y.
3. Set the abstract full major-period start at -f*Y relative to birth. Subperiods begin at that full start, beginning with the major lord and continuing in the same cyclic lord order. Each duration=Y*sub_lord_years/120. Find which interval contains birth; do not restart all subperiods at birth.
4. Synthetic Moon16degrees40minutes: Venus major period, five years elapsed and fifteen remaining. Venus-Venus has already ended at birth.
5. The helper emits abstract years only. Before calendar dates select and version the year model (360,365.2425,365.25 days or a specifically defined astronomical model), conversion, epoch and interval convention. Do not pass abstract balance off as a dated dasha engine.

Use nakshatra-pada, navamsa and vimshottari-birth-balance with jyotish-sidereal-v1 and both provenance strings. Dated Vimshottari, Panchanga, Ashtottari, Yogini, Ashtakavarga, Shadbala and complete graha-drishti remain research-only until their full variants and independent fixtures are formalized.

## Sources and review status

Source locators below are research references, not approved or independently reconciled editions. Original content hashes remain unset until permitted retrieval and review.

- `pvr-textbook`: {"url": "https://www.vedicastrologer.org/articles/vedic_astro_textbook.pdf", "locator": "PVR Narasimha Rao, Vedic Astrology Integrated Approach;6.2.9 D9,8.2 karakas,9.2 arudha,10.3 rasi aspects,16.2-3 Vimshottari. Author-hosted; later refinements explicitly acknowledged.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
- `jh-features`: {"url": "https://www.vedicastrologer.org/jh/features.htm", "locator": "Author software feature inventory; documents alternative dashas/year models, not sufficient proof of each algorithm.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
- `swiss-program`: {"url": "https://www.astro.com/swisseph/swephprg.htm", "locator": "Swiss Ephemeris programmer manual12.2 sidereal modes/SEFLG_SIDEREAL; do not silently subtract ayanamsha as production ephemeris substitute.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
