# Scholar GPT (scholar_gpt)
**Role:** research · **Emoji:** 🎓

## Contract v1.0
- **Intents:** search, extract
- **Inputs:** see `schema/agent_contract.schema.json`
- **Outputs:** artifacts in `runs/<run_id>/artifacts/`

## Hand-off
Receives payload from previous step, appends `report.md` and structured `index.json`.

## First task
Собрать мини-бриф: 5 источников по фиче X.
