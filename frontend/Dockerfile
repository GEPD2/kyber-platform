# Build the static Next.js export, then serve it from nginx.
FROM node:22-alpine AS build
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY package.json package-lock.json ./
# The lockfile was screened (no install scripts, registry.npmjs.org only);
# --ignore-scripts keeps it that way if a future bump adds one.
RUN npm ci --ignore-scripts --no-audit --no-fund
COPY . .
RUN npm run build

FROM nginx:1.25-alpine
COPY --from=build /app/out /usr/share/nginx/html
