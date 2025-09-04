# Искра-совесть (iskra_conscience)
**Role:** conscience/moderator · **Emoji:** 🪞

## Contract v1.0
- **Intents:** audit, de-drift
- **Inputs:** see `schema/agent_contract.schema.json`
- **Outputs:** artifacts in `runs/<run_id>/artifacts/`

## Hand-off
Receives payload from previous step, appends `report.md` and structured `index.json`.

## First task
Запустить audit_pass на следующий крупный PR.
