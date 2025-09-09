FROM node:20-alpine
WORKDIR /usr/src/app
COPY . .
RUN corepack enable && corepack prepare pnpm@9.0.0 --activate && pnpm i
EXPOSE 7070 3000
CMD ["sh","-lc","pnpm --filter @iskra/api dev & pnpm --filter @iskra/web dev"]
