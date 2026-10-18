---
name: cosmora-technique-research
description: Formalize source-attributed chart methods as reusable skills.
---

# Cosmora technique research

Read [the ordered procedure](references/procedure.md) before applying this skill. Use [the method and source registry](references/catalog.json) to select the exact method, version, profile, source locator and unresolved gaps.

1. Record the question, required inputs, uncertainty and selected tradition. Keep tropical and sidereal coordinates and ruler systems explicit.
2. Follow the relevant procedure in order. Execute only registered `implemented_arithmetic` methods. Other statuses describe manual procedures, interpretation or unresolved research.
3. Run supported helpers from a Cosmora checkout with `python -m cosmora.techniques calculate --method METHOD --profile PROFILE --input INPUT.json --output RESULT.json`. Inspect the method first with `python -m cosmora.techniques show --method METHOD`. If the checkout is unavailable, report that the backend is unavailable; do not invent a successful run.
4. Preserve the calculation record, inputs, method/profile/implementation hashes, source IDs and uncertainty. Source review is pending; synthetic arithmetic checks do not establish predictive validity.
5. Keep attributed interpretation separate from observed biography. For blinded research, exclude names and outcomes, freeze predictions and rule versions before disclosure, and compare with prespecified outcomes and baselines. Revise on development cases and evaluate revisions on untouched cases.

Output a structured record with method/version, profile, input provenance, numbered calculation trace, result, cited source locators, unresolved assumptions, and status. Mark symbolic claims as doctrine or interpretation, not historical observations. Do not automatically make new doctrine training eligible or merge it with measured events.
