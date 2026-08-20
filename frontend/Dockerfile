FROM node:20-alpine AS deps
WORKDIR /app
RUN npm config set registry https://registry.npmjs.org/ && \
    npm config set fetch-timeout 120000 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000
COPY package.json package-lock.json* ./
RUN npm ci --only=production --prefer-offline --no-audit

FROM node:20-alpine AS builder
WORKDIR /app
RUN npm config set registry https://registry.npmjs.org/ && \
    npm config set fetch-timeout 120000 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000
COPY package.json package-lock.json* ./
RUN npm ci --prefer-offline --no-audit
COPY . .
ARG NEXT_PUBLIC_API_URL=https://biasharaiq.onrender.com
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=deps /app/node_modules ./node_modules

RUN chown -R nextjs:nodejs /app

USER nextjs

EXPOSE 3000

CMD ["npm", "run", "start", "--", "-H", "0.0.0.0"]
