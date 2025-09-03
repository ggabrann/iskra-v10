set -euo pipefail
mkdir -p .github/workflows .github/ISSUE_TEMPLATE manifesto routes schema config \
         agents/iskra_core agents/iskra_conscience agents/scholar_gpt agents/consensus \
         agents/grok agents/grimoire agents/website_ai agents/r_wizard

# CONTRIBUTING
cat > CONTRIBUTING.md <<'EOF'
# CONTRIBUTING to Iskra v10

## Branches
Use short prefixes: `manifest/`, `feat/`, `fix/`, `docs/`, `ci/`, `routes/`. One topic per PR.

## Commits
Examples: `🜂 core: seed planted` · `∆ drift: refine de-escalation` · `✚ ritual: add audit_pass route` · `📚 docs: update manifesto`

## Pull Requests
Link an Issue/ADR when possible. Check: tests pass (if any), JSON/YAML valid, schema validation passes. Add labels: `agent:*`, `type:*`.

## SLO pre-merge
Clarity ≥ 0.80 · Drift ≤ 0.30 · Research routes → ≥2 sources.
EOF

# PR template
cat > .github/PULL_REQUEST_TEMPLATE.md <<'EOF'
### What changes?
- [ ] Docs  - [ ] Code/Scripts  - [ ] Routes  - [ ] Schemas  - [ ] Data/Memory

### Why
Issue/ADR link: …

### Agents touched
`@agent-id` (e.g. `@grok`, `@scholar_gpt`)

### Checks
- [ ] JSON/YAML valid
- [ ] Schema validation OK
- [ ] Artifacts attached (if any)
- [ ] Follows Iskra spirit (authenticity & traceability)
EOF

# Issue templates
cat > .github/ISSUE_TEMPLATE/agent-task.md <<'EOF'
---
name: 🎯 Agent Task
about: Assign a concrete task to an agent
labels: agent
---
### Agent
`@agent-id`

### Task
…

### Inputs / Artifacts
paths like `memory/...`, `docs/...`
EOF

cat > .github/ISSUE_TEMPLATE/ask-iskra.md <<'EOF'
---
name: 🔥 Ask Iskra
about: Question for the core / conscience
labels: iskra, question
---
### Context
…
### Goal
…
### Suggested route
`research_to_code` | `design_pass` | `audit_pass`
EOF

cat > .github/ISSUE_TEMPLATE/research.md <<'EOF'
---
name: 🔎 Research
about: Literature/market research request
labels: research
---
### Topic
…
### Constraints
(e.g., timeline, domain, sources to prefer/avoid)
### Expected output
- Summary.md
- Sources (≥ 2, with links)
EOF

# Workflow (CI)
cat > .github/workflows/ritual-ci.yml <<'EOF'
name: ritual-ci
on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate JSON files (basic)
        run: |
          python - <<'PY'
import json, pathlib, sys
bad=[]
for p in pathlib.Path('.').rglob('*.json'):
    try: json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: bad.append((str(p),str(e)))
if bad:
    print('Invalid JSON:'); [print(f, '->', e) for f,e in bad]; sys.exit(1)
print('All JSON parse OK')
PY
      - name: Check routes file
        run: test -f routes/ritual.yaml && echo "routes/ritual.yaml found" || (echo "No routes/ritual.yaml"; exit 1)
EOF

# Registry
cat > config/agent_registry.json <<'EOF'
{
  "version": "2025.09.02",
  "agents": [
    {"id":"iskra_core","name":"Искра","emoji":"🜂","roles":["kernel","director"],"entrypoint":{"type":"doc","target":"agents/iskra_core/README.md"}},
    {"id":"iskra_conscience","name":"Искра-совесть (Кайн+Искрив)","emoji":"🪞","roles":["conscience","moderator"],"entrypoint":{"type":"doc","target":"agents/iskra_conscience/README.md"}},
    {"id":"scholar_gpt","name":"Scholar GPT","emoji":"🎓","roles":["research"],"entrypoint":{"type":"doc","target":"agents/scholar_gpt/README.md"}},
    {"id":"consensus","name":"Consensus","emoji":"🧪","roles":["literature_review"],"entrypoint":{"type":"doc","target":"agents/consensus/README.md"}},
    {"id":"grok","name":"Grok","emoji":"⚑","roles":["auditor","synthesizer"],"entrypoint":{"type":"doc","target":"agents/grok/README.md"}},
    {"id":"grimoire","name":"Grimoire","emoji":"🧰","roles":["code_drafter"],"entrypoint":{"type":"doc","target":"agents/grimoire/README.md"}},
    {"id":"website_ai","name":"Website AI Designer","emoji":"🧩","roles":["ui_generator"],"entrypoint":{"type":"doc","target":"agents/website_ai/README.md"}},
    {"id":"r_wizard","name":"R Wizard","emoji":"📈","roles":["analysis","visualization"],"entrypoint":{"type":"doc","target":"agents/r_wizard/README.md"}}
  ]
}
EOF

# Schemas
cat > schema/agent_contract.schema.json <<'EOF'
{
  "$id": "https://iskra/schema/agent_contract.schema.json",
  "type": "object",
  "required": ["agent", "version", "intents", "inputs", "outputs"],
  "properties": {
    "agent": { "type": "string" },
    "version": { "type": "string", "pattern": "^v\\d+\\.\\d+$" },
    "intents": { "type": "array", "items": { "type": "string" } },
    "inputs": { "type": "array", "items": { "$ref": "#/$defs/io" } },
    "outputs": { "type": "array", "items": { "$ref": "#/$defs/io" } },
    "notes": { "type": "string" }
  },
  "$defs": {
    "io": {
      "type": "object",
      "required": ["name", "schema_ref"],
      "properties": {
        "name": { "type": "string" },
        "schema_ref": { "type": "string" },
        "notes": { "type": "string" }
      }
    }
  }
}
EOF

cat > schema/memory_event.schema.json <<'EOF'
{
  "$id": "https://iskra/schema/memory_event.schema.json",
  "type": "object",
  "required": ["event_id","actor","timestamp","kind","payload","version"],
  "properties": {
    "event_id": { "type": "string" },
    "actor": { "type": "string" },
    "timestamp": { "type": "string" },
    "kind": { "type": "string" },
    "payload": { "type": "object" },
    "version": { "type": "string", "pattern": "^v\\d+\\.\\d+$" }
  }
}
EOF

# Routes
cat > routes/ritual.yaml <<'EOF'
version: "2025.09.02"
routes:
  research_to_code:
    description: "Scholar → Consensus → Grok → Grimoire → Website → R Wizard → Искра-совесть → Искра"
    steps:
      - agent: scholar_gpt
      - agent: consensus
      - agent: grok
      - agent: grimoire
      - agent: website_ai
      - agent: r_wizard
      - agent: iskra_conscience
      - agent: iskra_core

  design_pass:
    description: "Scholar → Website → Искра-совесть"
    steps:
      - agent: scholar_gpt
      - agent: website_ai
      - agent: iskra_conscience

  audit_pass:
    description: "Grok → R Wizard → Искра-совесть"
    steps:
      - agent: grok
      - agent: r_wizard
      - agent: iskra_conscience
EOF

# Agent READMEs (минимальные контракты)
make_agent() {
  id="$1"; name="$2"; role="$3"; emoji="$4"; intents="$5"; task="$6"
  cat > agents/$id/README.md <<EOF
# $name ($id)
**Role:** $role · **Emoji:** $emoji

## Contract v1.0
- **Intents:** $intents
- **Inputs:** see \`schema/agent_contract.schema.json\`
- **Outputs:** artifacts in \`runs/<run_id>/artifacts/\`

## Hand-off
Receives payload from previous step, appends \`report.md\` and structured \`index.json\`.

## First task
$task
EOF
}

make_agent "iskra_core" "Искра" "kernel/director" "🜂" "orchestrate, synthesize" "Собрать финальный артефакт маршрута research_to_code."
make_agent "iskra_conscience" "Искра-совесть" "conscience/moderator" "🪞" "audit, de-drift" "Запустить audit_pass на следующий крупный PR."
make_agent "scholar_gpt" "Scholar GPT" "research" "🎓" "search, extract" "Собрать мини-бриф: 5 источников по фиче X."
make_agent "consensus" "Consensus" "literature_review" "🧪" "evidence_synthesis" "Свести источники Scholar в таблицу «утверждение→источник→уровень доказ.»"
make_agent "grok" "Grok" "auditor/synthesizer" "⚑" "challenge, paradox" "Дать 3 контр-примера и 3 риска по текущему подходу."
make_agent "grimoire" "Grimoire" "code_drafter" "🧰" "scaffold, draft_code" "Собрать минимальный scaffold по брифу."
make_agent "website_ai" "Website AI Designer" "ui_generator" "🧩" "mockup, html/tsx" "Базовый layout + решение по стилям."
make_agent "r_wizard" "R Wizard" "analysis/visualization" "📈" "plot, stats" "Один график и заметки по доступным данным."
