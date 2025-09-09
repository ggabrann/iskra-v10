# RUN — запуск (monorepo)

## Предусловия
- Node.js 20+, pnpm 9+
- (опционально) Docker

## Установка
npm i -g pnpm
pnpm i

## Запуск
pnpm --filter @iskra/api dev     # API http://localhost:7070
pnpm --filter @iskra/web dev     # Web http://localhost:3000

## Docker
cd infra/docker
docker compose up --build
