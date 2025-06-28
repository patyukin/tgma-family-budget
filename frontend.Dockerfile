# -------- Stage 1: Build --------
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy dependency manifests
COPY frontend/package*.json ./

# Install dependencies (reproducible & cached)
RUN --mount=type=cache,target=/root/.npm \
    npm ci --silent --progress=false --no-audit

# Copy source code
COPY frontend/ .

# Build the application (output will be in /app/dist)
RUN npm run build

# -------- Stage 2: Production image --------
FROM caddy:2-alpine AS runner

# Copy Caddyfile (SPA routing + headers)
COPY frontend/Caddyfile /etc/caddy/Caddyfile

# Copy built files from the previous stage
COPY --from=builder /app/dist /usr/share/caddy

EXPOSE 80

# Default entrypoint from the official image will start Caddy with the supplied config
