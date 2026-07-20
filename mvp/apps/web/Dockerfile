# VNBOT Web — Dockerfile for Fase 0.2
# Build: docker build -t vnbot-web -f apps/web/Dockerfile .
FROM node:20-slim AS builder

WORKDIR /app
RUN npm install -g pnpm

COPY pnpm-workspace.yaml package.json ./
COPY apps/web/package.json ./apps/web/
COPY packages/ui/package.json ./packages/ui/
COPY packages/pixelart/package.json ./packages/pixelart/

RUN pnpm install --no-frozen-lockfile

COPY . .
RUN pnpm --filter @vnbot/web build

FROM nginx:alpine
COPY --from=builder /app/apps/web/dist /usr/share/nginx/html
COPY apps/web/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
