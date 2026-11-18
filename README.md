# prepper-skills

Offline-first agent skills for household emergency preparedness, by AlveyTech.

These skills follow the open [Agent Skills](https://agentskills.io) format (a folder with a `SKILL.md`), so the same folders work in **Open WebUI**, **Claude**, and other agents that support the spec. They are written to run well on small local models: short instructions, hard numbers kept in reference tables and scripts instead of model memory.

| Skill | What it does |
|---|---|
| [`emergency-planner`](skills/emergency-planner/) | Turns photos or a typed list of your supplies into an inventory, then builds a plan for a specific emergency (power outage, winter storm, water outage, tornado, flood, evacuation) and lists the gaps. |
| [`ham-radio-ops`](skills/ham-radio-ops/) | Radio communications in an emergency, matched to your FCC license class (or none) and location. Includes a privilege checker built from 47 CFR Part 97. |

> **Not a substitute for emergency services or official guidance.** If you can reach 911, call 911. Follow instructions from local officials. These skills summarize public guidance and can be wrong or out of date; every reference file shows its source and the date it was checked.

## Install

**Open WebUI:** Workspace → Skills → Import, then choose a skill folder, a ZIP of it, or its URL in this repo. Attach the skill to the model you use offline. Scripts need a code-execution backend; every script is standard-library Python so it runs in Pyodide. If code execution is off, the skills fall back to the tables in their `references/` folders.

**Claude (Code, desktop, or claude.ai):** copy a skill folder into your skills directory (for Claude Code, `~/.claude/skills/`), or upload it as a skill.

## Your data stays local

Your own inventory, photos, location, license details and repeater lists belong in a `local/` folder at the repo root. It is listed in `.gitignore` and never committed. Templates and made-up examples live in each skill's `templates/` folder.

## Contributing

Region packs (local hazards, nets, emergency contacts for an area) and corrections are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

- Code (`scripts/`, `tests/`): [MIT](LICENSE)
- Written guidance (`SKILL.md`, playbooks, references): [CC BY 4.0](LICENSE-CONTENT.md)

Material quoted or summarized from U.S. federal sources (FCC, FEMA/Ready.gov, CDC, EPA, USDA, NWS) is public domain and credited in each `sources.md`.
