# syntax=docker.io/docker/dockerfile:1

# 📦 Base stage
FROM node:18-alpine AS base

RUN apk add --no-cache libc6-compat curl && \
    corepack enable && \
    corepack prepare pnpm@latest --activate

WORKDIR /app

# 📦 Dépendances
FROM base AS deps

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# ⚙️ Build avec variable API publique
FROM base AS builder

ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_USER_ID
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_USER_ID=$NEXT_PUBLIC_USER_ID

COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/pnpm-lock.yaml ./pnpm-lock.yaml
COPY . .

RUN cp next.config.dev.mjs next.config.mjs
RUN pnpm build

# 🚀 Image finale exécutable
FROM base AS runner

WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

COPY --chown=nextjs:nodejs entrypoint.sh /home/nextjs/entrypoint.sh
RUN chmod +x /home/nextjs/entrypoint.sh

USER nextjs

EXPOSE 3000
ENTRYPOINT ["/home/nextjs/entrypoint.sh"]
CMD ["node", "server.js"]
