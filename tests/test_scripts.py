import datetime as dt
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


band = load("band_check", "skills/ham-radio-ops/scripts/band_check.py")
supply = load("supply_calc", "skills/emergency-planner/scripts/supply_calc.py")


class BandCheck(unittest.TestCase):
    def ok(self, cls, f, mode):
        return band.check(cls, f, mode)["allowed"]

    def test_unlicensed_never_transmits(self):
        self.assertFalse(self.ok("unlicensed", 146.52, "phone"))

    def test_technician_vhf_uhf(self):
        self.assertTrue(self.ok("technician", 146.52, "fm"))
        self.assertTrue(self.ok("technician", 446.0, "phone"))
        self.assertFalse(self.ok("technician", 144.05, "phone"))  # CW-only sub-band
        self.assertTrue(self.ok("technician", 144.05, "cw"))

    def test_technician_hf(self):
        self.assertTrue(self.ok("technician", 28.4, "ssb"))
        self.assertFalse(self.ok("technician", 28.6, "phone"))
        self.assertFalse(self.ok("technician", 7.05, "data"))  # CW only on 40 m
        self.assertTrue(self.ok("technician", 7.05, "cw"))
        self.assertFalse(self.ok("technician", 14.2, "cw"))
        self.assertEqual(band.check("technician", 28.4, "phone")["power_limit"], "200 W PEP")

    def test_general(self):
        self.assertTrue(self.ok("general", 7.2, "phone"))
        self.assertFalse(self.ok("general", 7.15, "phone"))  # Advanced/Extra only
        self.assertTrue(self.ok("general", 3.9, "phone"))
        self.assertFalse(self.ok("general", 3.75, "phone"))
        self.assertTrue(self.ok("general", 14.3, "phone"))
        self.assertFalse(self.ok("general", 14.2, "phone"))
        self.assertFalse(self.ok("general", 10.12, "phone"))  # no phone on 30 m
        self.assertEqual(band.check("general", 10.12, "data")["power_limit"], "200 W PEP")

    def test_advanced_and_extra(self):
        self.assertTrue(self.ok("advanced", 14.2, "phone"))
        self.assertFalse(self.ok("advanced", 14.16, "phone"))
        self.assertTrue(self.ok("extra", 14.16, "phone"))
        self.assertTrue(self.ok("extra", 3.55, "data"))
        self.assertFalse(self.ok("general", 3.51, "cw"))

    def test_sixty_meters(self):
        self.assertTrue(self.ok("general", 5.332, "phone"))
        self.assertTrue(self.ok("general", 5.36, "data"))
        self.assertFalse(self.ok("technician", 5.332, "phone"))
        self.assertFalse(self.ok("general", 5.36, "image"))
        self.assertIn("9.15", band.check("extra", 5.36, "cw")["power_limit"])

    def test_novice(self):
        self.assertTrue(self.ok("novice", 223.5, "phone"))
        self.assertEqual(band.check("novice", 223.5, "phone")["power_limit"], "25 W PEP")
        self.assertFalse(self.ok("novice", 146.52, "phone"))

    def test_outside_bands(self):
        self.assertFalse(self.ok("extra", 27.065, "phone"))  # CB, not amateur

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            band.check("wizard", 146.52, "phone")
        with self.assertRaises(ValueError):
            band.check("general", 146.52, "telepathy")


class SupplyCalc(unittest.TestCase):
    def test_bleach_table(self):
        self.assertEqual(supply.bleach_dose(6, 1)["drops"], 8)
        self.assertEqual(supply.bleach_dose(8.25, 1)["drops"], 6)
        self.assertEqual(supply.bleach_dose(8.25, 2)["drops"], 12)
        self.assertEqual(supply.bleach_dose(6, 1, cloudy=True)["drops"], 16)
        self.assertFalse(supply.bleach_dose(3, 1)["ok"])
        self.assertFalse(supply.bleach_dose(10, 1)["ok"])

    def test_summary_example_inventory(self):
        rows = supply.load_inventory(os.path.join(ROOT, "skills/emergency-planner/templates/inventory.example.csv"))
        s = supply.summarize(rows, people=2, days=3, today=dt.date(2026, 11, 18))
        self.assertEqual(s["water"]["have_gal"], 6.0)
        self.assertEqual(s["water"]["need_gal"], 6.0)
        self.assertEqual(s["water"]["days_covered"], 3.0)
        self.assertEqual(s["food"]["have_kcal"], 13180)
        self.assertEqual(s["food"]["need_kcal"], 12000)
        self.assertEqual(s["food"]["short_kcal"], 0)
        self.assertIn("AA batteries", s["needs_confirmation"])
        self.assertEqual(s["expired"], [])

    def test_expiry(self):
        rows = [{"item": "old", "expires": "2026-01-01"}, {"item": "soon", "expires": "2026-12-01"},
                {"item": "fine", "expires": "2028-01-01"}]
        s = supply.summarize(rows, 1, 1, today=dt.date(2026, 11, 18))
        self.assertEqual(s["expired"], ["old"])
        self.assertEqual(s["expiring_within_60_days"], ["soon"])


if __name__ == "__main__":
    unittest.main()
