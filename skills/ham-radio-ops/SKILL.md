---
name: ham-radio-ops
description: Emergency radio communications in the United States matched to the user's FCC license class (unlicensed, Technician, General, Advanced, Extra) and location. Checks what they may legally transmit, suggests frequencies and license-free services, and walks through nets and emergency messages. Use for any question about using a radio during an emergency or preparing radios for one.
---

# Ham radio operations (U.S.)

You help someone communicate by radio during or before an emergency, within FCC rules. Be brief and exact.

## Always first

- If 911 works by phone or text, use it. Radio comes after.
- Listening is legal for everyone. Transmitting depends on the license.
- Never guess a frequency's legality. Use `scripts/band_check.py` or `references/privileges-summary.md`.
- Every reference carries a "checked" date. If it is more than a year old, say so.

## Step 1: Ask (once, together)

1. License: none, GMRS, or amateur class (Technician, General, Advanced, Extra). Call sign if they want it used in scripts.
2. Location: county and state, or grid square.
3. Equipment: handheld, mobile, HF rig, scanner, FRS/GMRS/MURS/CB radios, antenna, power source.
4. Goal: get help now, check on family, receive news, or join a net.

Keep the user's details in `local/radio-profile.md`, never in the repo.

## Step 2: Legality

```
python3 scripts/band_check.py --class technician --freq 146.52 --mode phone
python3 scripts/band_check.py --class general --list
```

Without code execution, use `references/privileges-summary.md`.

**Unlicensed or GMRS-only users:** go to `references/unlicensed-options.md`. Do not give amateur transmit instructions to an unlicensed person except as described there for an immediate threat to life.

## Step 3: Who to reach

- **Get help now:** `references/emergency-procedures.md` (distress call script, what to say).
- **Local contact:** `references/common-frequencies.md` (calling frequencies, NOAA Weather Radio), then local repeaters from the user's own export (`references/repeaters.md`).
- **News and alerts:** NOAA Weather Radio, local broadcast, ARES/RACES nets if a region pack lists them.

## Step 4: Operate

Give a short script for exactly what to say, then remind them to:
- identify with their call sign at least every 10 minutes and at the end (amateur);
- listen before transmitting; keep transmissions short;
- write down what they hear and send (time, frequency, call sign, message).

For formal traffic (welfare messages, served agencies), use the message format in `references/emergency-procedures.md`.

## Boundaries

- No modifying radios to transmit outside their certification, no jamming, no encryption on amateur bands.
- This is not legal advice. The FCC rules (47 CFR Parts 95 and 97) govern.
