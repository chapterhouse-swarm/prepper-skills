# Local repeaters (bring your own list)

This repo does not ship repeater data. Directory data (RepeaterBook and others) has its own terms, and repeaters change often.

## Make your own offline list

1. While you have internet, export repeaters near you from a directory you have access to, or from your radio programming software (for example, a CHIRP CSV).
2. Save it as `local/repeaters.csv`. It is ignored by git.
3. Keep at least these columns: `name, output_mhz, offset_mhz, tone_hz, location, notes`. CHIRP's `Frequency, Duplex, Offset, rToneFreq, Comment` columns map to these.
4. Program the important ones into your radios now. Print a copy.

## How the skill should use it

- Read `local/repeaters.csv` if it exists. Sort by distance to the user's location if coordinates are present; otherwise by listed city/county.
- Show output frequency, offset direction, and tone together; a repeater can't be used without the tone.
- Remind Technician+ users to listen first, give their call sign, and keep it short.
- If the file is missing, say so and fall back to simplex calling frequencies in `common-frequencies.md`.
