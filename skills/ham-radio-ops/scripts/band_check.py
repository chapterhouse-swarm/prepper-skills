#!/usr/bin/env python3
"""Check U.S. amateur radio transmit privileges from 47 CFR Part 97 tables.

Examples:
  band_check.py --class technician --freq 146.52 --mode phone
  band_check.py --class general --freq 7.200 --mode phone
  band_check.py --class technician --list

Classes: unlicensed, novice, technician, general, advanced, extra
Modes:   cw, phone (voice: SSB, FM, AM), data (RTTY, FT8, packet, ...), image (SSTV, ...)

Scope and data date: see data/us_amateur_privileges.json. Standard library only.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "..", "data", "us_amateur_privileges.json")
CLASSES = ("unlicensed", "novice", "technician", "general", "advanced", "extra")
MODE_ALIASES = {
    "cw": "cw", "morse": "cw",
    "phone": "phone", "voice": "phone", "ssb": "phone", "usb": "phone", "lsb": "phone", "fm": "phone", "am": "phone",
    "data": "data", "digital": "data", "rtty": "data", "ft8": "data", "packet": "data", "psk31": "data", "aprs": "data",
    "image": "image", "sstv": "image",
}
EPS = 1e-9


def load_data(path=DATA_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _in(freq, lo, hi):
    return lo - EPS <= freq <= hi + EPS


def _ranges_for(cls, data):
    ranges = list(data["class_ranges"].get(cls, []))
    if cls in data["vhf_uhf_classes"]:
        ranges += data["vhf_uhf_ranges"]
    return ranges


def _sixty_meters(cls, freq, mode, data):
    s = data["sixty_meters"]
    lo, hi = s["segment"]
    on_channel = any(_in(freq, c - s["channel_half_width_mhz"], c + s["channel_half_width_mhz"])
                     for c in s["channels_center_mhz"])
    in_segment = _in(freq, lo, hi)
    if not (on_channel or in_segment):
        return None
    base = {"band": "60 m", "frequency_mhz": freq, "mode": mode, "notes": [s["note"]]}
    if cls not in s["classes"]:
        return {**base, "allowed": False, "reason": "60 m requires General, Advanced or Extra."}
    if mode not in s["modes"]:
        return {**base, "allowed": False, "reason": f"{mode} is not authorized on 60 m (cw, phone, data only)."}
    power = s["segment_power"] if in_segment else s["channel_power"]
    return {**base, "allowed": True, "power_limit": power}


def check(cls, freq, mode, data=None):
    data = data or load_data()
    cls = cls.lower()
    mode = MODE_ALIASES.get(mode.lower(), mode.lower())
    if cls not in CLASSES:
        raise ValueError(f"unknown class {cls!r}; use one of {', '.join(CLASSES)}")
    if mode not in ("cw", "phone", "data", "image"):
        raise ValueError(f"unknown mode {mode!r}; use cw, phone, data or image")

    if cls == "unlicensed":
        return {
            "allowed": False, "frequency_mhz": freq, "mode": mode,
            "reason": "Transmitting on amateur frequencies requires an FCC amateur license. Listening is always legal.",
            "notes": ["See references/unlicensed-options.md for license-free radio services (FRS, MURS, CB) "
                      "and for what the rules say about genuine life-threatening emergencies."],
        }

    sixty = _sixty_meters(cls, freq, mode, data)
    if sixty is not None:
        return sixty

    seg = next((s for s in data["mode_segments"] if _in(freq, s["lo"], s["hi"])), None)
    if seg is None:
        return {"allowed": False, "frequency_mhz": freq, "mode": mode,
                "reason": "Not inside a modeled U.S. amateur band (see data scope)."}

    result = {"band": seg["band"], "frequency_mhz": freq, "mode": mode, "notes": []}
    if seg.get("note"):
        result["notes"].append(seg["note"])

    if not any(_in(freq, lo, hi) for lo, hi in _ranges_for(cls, data)):
        return {**result, "allowed": False,
                "reason": f"{cls.title()} class has no privileges at {freq:g} MHz."}

    nt = data["novice_technician_hf"]
    if cls in ("novice", "technician") and freq < 30:
        if any(_in(freq, lo, hi) for lo, hi in nt["cw_only"]):
            allowed_modes = ["cw"]
        else:
            ten = next(s for s in nt["ten_meters"] if _in(freq, s["lo"], s["hi"]))
            allowed_modes = ten["modes"]
            if ten.get("note"):
                result["notes"].append(ten["note"])
        if mode not in allowed_modes:
            return {**result, "allowed": False,
                    "reason": f"{cls.title()} may use only {', '.join(allowed_modes)} here."}
        return {**result, "allowed": True, "power_limit": nt["power"]}

    # CW is allowed anywhere the operator has privileges (97.305(a)).
    if mode != "cw" and mode not in seg["modes"]:
        return {**result, "allowed": False,
                "reason": f"{mode} is not authorized in {seg['lo']:g}-{seg['hi']:g} MHz "
                          f"(allowed: {', '.join(seg['modes'])})."}

    p = data["power"]
    if seg["band"] == "30 m":
        power = p["thirty_meters"]
    elif cls == "novice" and seg["band"] == "1.25 m":
        power = p["novice_222"]
    elif cls == "novice" and seg["band"] == "23 cm":
        power = p["novice_1270"]
    else:
        power = p["default"]
    return {**result, "allowed": True, "power_limit": power}


def list_privileges(cls, data=None):
    data = data or load_data()
    cls = cls.lower()
    if cls == "unlicensed":
        return "No amateur transmit privileges. Listening is legal. See references/unlicensed-options.md."
    lines = [f"{cls.title()} class privileges (MHz), data as of {data['as_of']}:"]
    for lo, hi in _ranges_for(cls, data):
        lines.append(f"  {lo:g} - {hi:g}")
    if cls in data["sixty_meters"]["classes"]:
        s = data["sixty_meters"]
        lines.append(f"  60 m: {s['segment'][0]:g}-{s['segment'][1]:g} and channels "
                     f"{', '.join(f'{c:g}' for c in s['channels_center_mhz'])}")
    if cls in ("novice", "technician"):
        lines.append("  HF segments: CW only on 80/40/15 m; 10 m 28.0-28.3 CW/data, 28.3-28.5 CW/SSB voice; 200 W PEP.")
    lines.append(f"Scope: {data['scope']}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--class", dest="cls", required=True, choices=CLASSES)
    ap.add_argument("--freq", type=float, help="frequency in MHz")
    ap.add_argument("--mode", default="phone")
    ap.add_argument("--list", action="store_true", help="list privileges for the class")
    args = ap.parse_args(argv)
    try:
        data = load_data()
    except OSError:
        print("Privilege data file not found; use references/privileges-summary.md instead.")
        return 2
    if args.list:
        print(list_privileges(args.cls, data))
        return 0
    if args.freq is None:
        ap.error("give --freq or --list")
    try:
        print(json.dumps(check(args.cls, args.freq, args.mode, data), indent=2))
    except ValueError as e:
        ap.error(str(e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
