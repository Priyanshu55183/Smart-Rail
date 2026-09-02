# =============================================
# SmartRail Frontend — Dockerfile
# =============================================
# Multi-stage build for Next.js with standalone output.
#
# Stage 1 (deps):    Install all npm dependencies
# Stage 2 (builder): Build the Next.js production bundle
# Stage 3 (runner):  Run the standalone server

FROM node:20-alpine AS deps

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --prefer-offline

# ── Build Stage ──────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Set build-time env vars
ENV NEXT_PUBLIC_API_URL=http://backend:8000
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# ── Runtime Stage ────────────────────────────────
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV NEXT_PUBLIC_API_URL=http://backend:8000

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy standalone output
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
