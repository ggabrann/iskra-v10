# Как применить архив к репозиторию

1. Скачай и распакуй в **корень** проекта (рядом с README.md).
2. Если у тебя есть старая папка-скелет `iskra-core-app/`, удали её:
   ```bash
   git rm -r iskra-core-app || true
   ```
3. Зафиксируй изменения:
   ```bash
   git add -A && git commit -m "feat(core): Iskra Core MCP + fly/dev scaffolding"
   ```
4. Установи зависимости и проверь локально:
   ```bash
   pip install -r requirements.txt
   make dev
   ```
5. Настрой деплой (секреты в GitHub → Actions): `FLY_APP_NAME`, `FLY_API_TOKEN`.
6. Для MCP-ручек доступны эндпоинты:
   - `GET /symbols/list`
   - `POST /symbols/upsert`  (body: `{ "symbols": {"A":1}, "items": ["X","Y"] }`)
   - `POST /growth/add`     (body: `{ "text": "string", "payload": {...} }`)
   - `POST /epoch/snapshot`
   - `GET /slo/report`
   - `GET /sse`  (Server-Sent Events, text/event-stream)
