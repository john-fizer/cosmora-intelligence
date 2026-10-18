# Cosmora dispositor chains

## Required inputs

A mapping of body names to verified longitudes, a named traditional or modern domicile ruler profile, and positions for every ruler reached. Use traditional Mars for Scorpio, Saturn for Aquarius and Jupiter for Pisces; the separate modern profile uses Pluto, Uranus and Neptune respectively. Chiron and nodes may be traced as starting points but are not silently assigned domiciles.

1. Normalize each longitude modulo 360; take floor(longitude/30) as the sign index, Aries zero.
2. Map the sign to the selected domicile ruler. Create a directed body-to-ruler edge.
3. Follow the ruler's own sign and repeat. Stop at the first repeated body. If a required ruler position is missing, return an input error rather than truncating the chain.
4. Split each path into approach and terminal cycle. A self-loop is a planet in its own domicile. A two-cycle is a mutual reception by domicile; larger cycles remain cycles.
5. Call a planet the sole final dispositor only if every included path terminates at the same one-body self-loop. Multiple self-loops or a multi-body cycle do not satisfy that definition.
6. Preserve ruler profile and the included body universe in the result. Compare modern and traditional outputs as separate runs; never splice edges from both.

Synthetic check: Sun at 10 Aries points to Mars; Mars at 10 Leo points to Sun. This yields a Sun/Mars cycle, not a sole final dispositor. Use method dispositor-chains; the committed example file supplies a complete runnable input.

Interpretation follows calculation: record which topic rulers converge and which do not. Claims about psychological dominance remain attributed interpretations, not established facts.

## Sources and review status

Source locators below are research references, not approved or independently reconciled editions. Original content hashes remain unset until permitted retrieval and review.

- `ptolemy-i`: {"url": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/1B%2A.html", "locator": "Tetrabiblos I.7,13,17,19-24; public ancient text, Robbins translation; locate each named chapter.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
- `skyscript-dispositor`: {"url": "https://www.skyscript.co.uk/glossary/dispositor/", "locator": "Dispositor definition; graph tracing/terminal algorithm is Cosmora editorial formalization.", "review_status": "pending", "retrieved_content_sha256": null, "access_note": "Research-agent source discovery; independent full source/edition verification remains pending."}
