FROM node:22-alpine AS package-manager
RUN npm install --global pnpm@10.15.0

FROM package-manager AS dependencies
WORKDIR /workspace
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/web/package.json ./apps/web/package.json
RUN pnpm install --frozen-lockfile --filter @careerrank/web...

FROM package-manager AS builder
WORKDIR /workspace
ARG API_URL=http://localhost:8000
ENV API_URL=$API_URL \
    NEXT_TELEMETRY_DISABLED=1
COPY --from=dependencies /workspace/ ./
COPY apps/web ./apps/web
RUN pnpm --filter @careerrank/web build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs
COPY --from=builder --chown=nextjs:nodejs /workspace/apps/web/.next/standalone ./
# Next 16's standalone trace can retain the pnpm link while copying only the
# helper files observed at build time. Copy the pinned runtime package in full.
COPY --from=builder --chown=nextjs:nodejs /workspace/node_modules/.pnpm/@swc+helpers@0.5.23/node_modules/@swc/helpers ./node_modules/.pnpm/@swc+helpers@0.5.23/node_modules/@swc/helpers
COPY --from=builder --chown=nextjs:nodejs /workspace/apps/web/.next/static ./apps/web/.next/static
USER nextjs
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
