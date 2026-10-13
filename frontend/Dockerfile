# Build the static Next.js export, then serve it from nginx with ModSecurity
# and the OWASP Core Rule Set (the web application firewall).
FROM node:22-alpine AS build
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY package.json package-lock.json ./
# The lockfile was screened (no install scripts, registry.npmjs.org only);
# --ignore-scripts keeps it that way if a future bump adds one.
RUN npm ci --ignore-scripts --no-audit --no-fund
COPY . .
RUN npm run build && node scripts/csp-hashes.mjs out /app/csp_script.conf

# Official OWASP image: nginx 1.30 + ModSecurity v3 + CRS 4.25 LTS, non-root
# (user nginx, uid 101). Pinned to a dated build; bump it on purpose.
FROM owasp/modsecurity-crs:4.25.1-nginx-alpine-202609241109-lts
USER root
# The image's entrypoint renders a demo proxy vhost and edits nginx.conf; this
# project mounts its own nginx.conf and conf.d, so drop those parts and keep
# only the ModSecurity / CRS setup (templates 20, copy 90, plugins 94, rules 95).
RUN rm -f /etc/nginx/templates/nginx.conf.template \
          /etc/nginx/conf.d/default.conf \
    && rm -rf /etc/nginx/templates/conf.d /etc/nginx/templates/includes \
    && rm -f /docker-entrypoint.d/10-generate-certificate.sh \
             /docker-entrypoint.d/91-update-resolver.sh \
             /docker-entrypoint.d/92-update-real_ip.sh \
             /docker-entrypoint.d/93-update-proxy-ssl-config.sh \
             /docker-entrypoint.d/96-update-http3-config.sh \
    && rm -rf /usr/share/nginx/html/* \
    && mkdir -p /etc/nginx/csp
COPY --from=build /app/out /usr/share/nginx/html
COPY --from=build /app/csp_script.conf /etc/nginx/csp/csp_script.conf
USER nginx
