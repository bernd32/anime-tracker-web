# syntax=docker/dockerfile:1.7

ARG NODE_VERSION=22

FROM node:${NODE_VERSION}-alpine AS base
WORKDIR /app

FROM base AS dev
RUN apk add --no-cache libc6-compat
COPY package*.json ./
RUN npm ci
COPY . .
RUN addgroup -S nextjs && adduser -S nextjs -G nextjs \
    && chown -R nextjs:nextjs /app
USER nextjs
EXPOSE 20773
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "20773"]

FROM base AS deps
RUN apk add --no-cache libc6-compat
COPY package*.json ./
RUN npm ci

FROM base AS builder
ARG NEXT_PUBLIC_API_BASE_URL
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    NPM_CONFIG_UPDATE_NOTIFIER=false \
    NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}
RUN apk add --no-cache libc6-compat
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:${NODE_VERSION}-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=20773 \
    HOSTNAME=0.0.0.0
RUN apk add --no-cache libc6-compat wget \
    && addgroup -S nextjs && adduser -S nextjs -G nextjs
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
RUN chown -R nextjs:nextjs /app
USER nextjs
EXPOSE 20773
CMD ["node", "server.js"]
