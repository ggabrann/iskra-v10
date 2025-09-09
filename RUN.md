# RUN — запуск (monorepo)
npm i -g pnpm || true
pnpm i
pnpm --filter @iskra/api dev     # 7070
pnpm --filter @iskra/web dev     # 3000
# Docker: cd infra/docker && docker compose up --build
