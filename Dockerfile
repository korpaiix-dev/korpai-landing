# syntax=docker/dockerfile:1.6

# ---------- Stage 1: build ----------
FROM node:20-alpine AS build
WORKDIR /build

# Install only runtime deps needed to build Astro
COPY site/package.json site/package-lock.json ./site/
RUN cd site && npm ci --no-audit --no-fund

# Copy source + build
COPY site ./site
ARG GIT_SHA=local
RUN echo "$GIT_SHA" > site/public/version.txt \
 && cd site \
 && npm run build

# ---------- Stage 2: serve ----------
FROM nginx:1.27-alpine AS serve
# Static assets
COPY --from=build /build/site/dist /var/www/korpai
# Site-specific nginx config (served on port 80 inside container)
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf

# Healthcheck — nginx replies 200 on /version.txt when site is up
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1/version.txt >/dev/null || exit 1

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
