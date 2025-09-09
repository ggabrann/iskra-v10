# RUN — запуск локально

## Предусловия
- Node.js 20+, pnpm 9+
- (опционально) Docker

## Установка
npm i -g pnpm
pnpm i

## Запуск сервисов
pnpm --filter @iskra/api dev     # API http://localhost:7070
pnpm --filter @iskra/web dev     # WEB http://localhost:3000

## Дымовые тесты ядра
pnpm --filter @iskra/core build && pnpm --filter @iskra/core test

## Docker (web+api)
cd infra/docker
docker compose up --build
