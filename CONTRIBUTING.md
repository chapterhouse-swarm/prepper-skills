# Contributing

Thanks for helping. The bar for this repo is simple: **every fact must have a source and a date.**

## Ground rules

1. **Cite official sources first.** FCC rules (eCFR), Ready.gov/FEMA, CDC, EPA, USDA, NWS, and your state or county emergency agency. Add the URL and the date you checked it to the skill's `references/sources.md`.
2. **Don't paste copyrighted material.** Summarize in your own words and link. Do not commit ARRL band charts, Red Cross handouts, or RepeaterBook exports.
3. **No personal data.** Don't commit real inventories, addresses, call signs other than your own in a contributor line, or photos of your home.
4. **Keep `SKILL.md` short.** Small local models follow short instructions better. Put depth in `references/`.
5. **Scripts are standard-library Python 3 only**, so they run in Pyodide. Add a test in `tests/` for any calculation.
6. **Stay within safe, lawful guidance.** No weapons, no unlicensed transmitting outside a genuine life-safety emergency, no improvised medical or chemical procedures beyond what an official source publishes.

## Region packs

A region pack adds local context to `emergency-planner` (and optionally `ham-radio-ops`). Copy
`skills/emergency-planner/regions/_template.md` to `regions/us-<state>-<area>.md` and fill in:

- the hazards that actually affect the area, with the official source for each
- official alert sources (NWS office, county EMA, NOAA Weather Radio transmitter)
- non-emergency numbers and official websites (no private individuals)
- optional: ARES/RACES or other public nets, with where the schedule is published

## Running tests

```
python3 -m unittest discover -s tests -v
```
