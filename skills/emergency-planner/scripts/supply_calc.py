#!/usr/bin/env python3
"""Supply math for the emergency-planner skill. Standard library only.

Examples:
  supply_calc.py --inventory local/inventory.csv --people 3 --days 7
  supply_calc.py --inventory local/inventory.csv --people 2 --days 14 --kcal 2200 --today 2026-11-18
  supply_calc.py --bleach 8.25 --gallons 5 --cloudy

Planning figures (see references/water.md, references/food-safety.md):
  water: 1 gallon per person per day (Ready.gov); more for hot weather, nursing, illness
  food:  2,000 kcal per person per day is a planning assumption, not an official figure
  bleach: CDC/EPA table: 8 drops/gal for 5-6%, 6 drops/gal for 8.25%; double if cloudy or very cold
"""
import argparse
import csv
import datetime as dt
import json
import sys

WATER_GAL_PER_PERSON_DAY = 1.0
DEFAULT_KCAL_PER_PERSON_DAY = 2000

# drops per gallon of clear water, from CDC/EPA emergency disinfection tables
BLEACH_DROPS_PER_GALLON = {"5-6": 8, "8.25": 6}


def bleach_key(concentration):
    """Map a label concentration to a row of the official table, or None."""
    if 5.0 <= concentration <= 6.0:
        return "5-6"
    if abs(concentration - 8.25) < 0.01:
        return "8.25"
    return None


def bleach_dose(concentration, gallons, cloudy=False):
    key = bleach_key(concentration)
    if key is None:
        return {
            "ok": False,
            "message": (
                f"{concentration}% is not in the CDC/EPA table (5-6% or 8.25%). "
                "Do not guess a dose: boil the water instead (rolling boil 1 minute, "
                "3 minutes above 6,500 ft), or use a product whose label gives water-treatment directions."
            ),
        }
    drops = BLEACH_DROPS_PER_GALLON[key] * gallons * (2 if cloudy else 1)
    return {
        "ok": True,
        "drops": round(drops),
        "message": (
            f"Add {round(drops)} drops of plain unscented {concentration}% bleach to {gallons:g} gal "
            f"of {'cloudy (filtered first) ' if cloudy else 'clear '}water. Stir, wait at least 30 minutes. "
            "It should smell faintly of chlorine; if not, repeat the dose and wait another 15 minutes."
        ),
    }


def _num(value):
    try:
        return float(value) if value not in (None, "") else 0.0
    except ValueError:
        return 0.0


def load_inventory(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def summarize(rows, people, days, kcal_per_day=DEFAULT_KCAL_PER_PERSON_DAY, today=None):
    today = today or dt.date.today()
    water_have = sum(_num(r.get("water_gallons")) for r in rows)
    kcal_have = sum(_num(r.get("calories_total")) for r in rows)
    water_need = WATER_GAL_PER_PERSON_DAY * people * days
    kcal_need = kcal_per_day * people * days

    expired, expiring = [], []
    for r in rows:
        exp = (r.get("expires") or "").strip()
        if not exp:
            continue
        try:
            d = dt.date.fromisoformat(exp)
        except ValueError:
            continue
        if d < today:
            expired.append(r["item"])
        elif (d - today).days <= 60:
            expiring.append(r["item"])

    unverified = [r["item"] for r in rows
                  if (r.get("verified") or "").strip().lower() != "yes"
                  or (r.get("confidence") or "").strip().lower() == "low"]
    missing_kcal = [r["item"] for r in rows
                    if (r.get("category") or "").strip().lower() == "food" and not _num(r.get("calories_total"))]
    categories = sorted({(r.get("category") or "").strip().lower() for r in rows if r.get("category")})

    def days_covered(have, per_day):
        return round(have / per_day, 1) if per_day else 0.0

    return {
        "people": people,
        "days_planned": days,
        "water": {
            "have_gal": round(water_have, 1),
            "need_gal": round(water_need, 1),
            "short_gal": round(max(0.0, water_need - water_have), 1),
            "days_covered": days_covered(water_have, WATER_GAL_PER_PERSON_DAY * people),
        },
        "food": {
            "have_kcal": round(kcal_have),
            "need_kcal": round(kcal_need),
            "short_kcal": round(max(0.0, kcal_need - kcal_have)),
            "days_covered": days_covered(kcal_have, kcal_per_day * people),
            "kcal_per_person_day_assumed": kcal_per_day,
            "food_rows_missing_calories": missing_kcal,
        },
        "expired": expired,
        "expiring_within_60_days": expiring,
        "needs_confirmation": unverified,
        "categories_present": categories,
        "categories_missing": [c for c in ("water", "food", "light", "power", "medical", "sanitation", "comms", "safety")
                               if c not in categories],
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--inventory", help="inventory CSV path")
    p.add_argument("--people", type=int, default=1)
    p.add_argument("--days", type=int, default=3)
    p.add_argument("--kcal", type=int, default=DEFAULT_KCAL_PER_PERSON_DAY, help="kcal per person per day")
    p.add_argument("--today", help="YYYY-MM-DD (defaults to system date)")
    p.add_argument("--bleach", type=float, help="bleach concentration in percent, e.g. 6 or 8.25")
    p.add_argument("--gallons", type=float, default=1.0, help="gallons of water to treat")
    p.add_argument("--cloudy", action="store_true", help="water is cloudy, colored or very cold")
    args = p.parse_args(argv)

    if args.bleach is not None:
        result = bleach_dose(args.bleach, args.gallons, args.cloudy)
        print(result["message"])
        return 0 if result["ok"] else 2

    if not args.inventory:
        p.error("give --inventory or --bleach")
    if args.people < 1 or args.days < 1:
        p.error("--people and --days must be at least 1")
    today = dt.date.fromisoformat(args.today) if args.today else None
    print(json.dumps(summarize(load_inventory(args.inventory), args.people, args.days, args.kcal, today), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
