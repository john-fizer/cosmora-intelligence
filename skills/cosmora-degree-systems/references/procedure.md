# Cosmora degree systems

## Convention lock

Record coordinate system, longitude precision, table edition and rulership before selecting a degree technique. Degree fractions, ordinal degrees and zodiacal subdivisions are different inputs. Preserve unrounded longitudes for all boundaries.

## Implemented subdivisions

1. Normalize lambda to[0,360); sign s=floor(lambda/30), within-sign degree d=lambda-30*s.
2. Chaldean decan: j=floor(d/10); global index=3*s+j. Repeat Mars,Sun,Venus,Mercury,Moon,Saturn,Jupiter from Aries's first decan. Half-open spans[0,10),[10,20),[20,30).
3. Triplicity decan: decan sign=(s+4*j) mod12; select that sign's domicile ruler under the explicit traditional or modern table. This is a separate method, not a correction of the Chaldean table.
4. Dodecatemoria in the selected own-sign expansion: derived longitude=(30*s+12*d) mod360. Do not substitute global harmonic12 (12*lambda mod360), which gives a different starting sign.
5. Run chaldean-decans, triplicity-decans or dodecatemoria and record the profile. Example Aries13 gives second Chaldean decan Sun and second triplicity decan Leo; traditional ruler Sun.

## Bounds: researched manual specification

Choose Egyptian or Ptolemaic edition before lookup. Each sign needs five ordered rulers and positive spans summing30. Cumulative half-open intervals determine the ruler; exact endpoints enter the next interval. Egyptian Aries spans Jupiter6,Venus6,Mercury8,Mars5,Saturn5; Ptolemaic Aries Jupiter6,Venus8,Mercury7,Mars5,Saturn4. Thus Aries13 gives Mercury versus Venus. Do not publish a complete executable table from these examples: the online Robbins Libra table repeats Saturn and needs edition reconciliation. Both full bounds methods remain research-only.

## Authored symbolic systems

Stojanovic degree theory: the attributed primary page could not be accessed. Fractional handling, ordinal mapping, zero degrees and exceptions remain unverified. Do not reconstruct a dictionary from conflicting tertiary tables. Return a research gap for requested execution.

Sabian symbols: choose author and edition (Jones/Wheeler material versus Rudhyar interpretations), indexing and licensed text access. The Sabian Assembly sunrise convention assigns exact whole26degrees to symbol26,26degrees01minute to27, and exact0degrees to the preceding sign's30. Other common floor(d)+1 conventions differ at boundaries; label each explicitly. Preserve coordinates and selected symbol index; quote only permitted excerpts rather than embedding a full copyrighted symbol corpus. Interpretation remains interpretation-only, with no measured event claim.

For any new degree doctrine, obtain the originator's rule, boundary examples and exception list, version it separately and run blind comparisons against degree-shuffled controls before claiming predictive value.

## Sources and review status

Source locators below are research references, not approved or independently reconciled editions. Original content hashes remain unset until permitted retrieval and review.

- `skyscript-faces`: {"url": "https://www.skyscript.co.uk/glossary/faces/", "locator": "Faces: distinguish Firmicus/planetary sequence from Manilius/triplicity decans.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
- `skyscript-twelfths`: {"url": "https://www.skyscript.co.uk/glossary/dodekatemoria/", "locator": "Dodekatemoria: own-sign twelfth parts and multiplication convention; retain variants.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
- `nikola-primary`: {"url": "https://www.astrologyinserbia.com/e/nikola/tajna_svakogstepena.htm", "locator": "Nikola Stojanovic author page; unavailable during research. Exact degree indexing and exception dictionary unresolved.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
- `sabian-origin`: {"url": "https://sabian.org/sabiansymbols.php", "locator": "Sabian Assembly origin/history; Marc Edmund Jones and Elsie Wheeler; source/edition distinction.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
- `sabian-index`: {"url": "https://sabian.org/sunrise_symbols.php", "locator": "Sabian Assembly Which Sabian Symbol Should You Use?,rules1-5; exact-degree and zero-degree indexing differs from common floor+1 bins.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
- `rudhyar-book`: {"url": "https://www.khaldea.com/rudhyar/aoft/aoft_c8_s4_p1.shtml", "locator": "Rudhyar bibliographic discussion; separate modern commentary; no full symbol dictionary redistribution.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
