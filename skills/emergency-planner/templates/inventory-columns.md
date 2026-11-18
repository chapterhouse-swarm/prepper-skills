# Inventory columns

| Column | Required | Meaning |
|---|---|---|
| item | yes | What it is, as specific as the label allows |
| category | yes | One of: water, food, medical, medication, light, power, heat, cooking, sanitation, safety, comms, tools, shelter, documents, pets, other |
| quantity | yes | Number of units |
| unit | yes | each, can, jar, jug, bottle, box, kit, gallon, lb, ... |
| calories_total | no | Total kcal for the whole row (all units). From the label; blank if unknown |
| water_gallons | no | Total drinking water in gallons for the whole row |
| expires | no | YYYY-MM-DD; blank if none or unreadable |
| location | no | Where it is kept |
| condition | no | sealed, good, opened, damaged, working, unknown |
| confidence | yes | high, medium, low (how sure the reader is about this row) |
| verified | yes | yes or no (has a person confirmed it) |
| notes | no | Anything else |

Keep the real file at `local/inventory.csv` (ignored by git). Medication rows: record what the household says it has; never infer doses.
