ARG ALPINE_VERSION=alpine3.21

FROM node:${ALPINE_VERSION} AS build

# Create a non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy only package files first to leverage Docker cache
COPY package*.json ./

# Install dependencies (including dev dependencies for build)
RUN npm ci

# Copy application code
COPY --chown=appuser:appgroup . .

# Build the application with environment variables
ARG VITE_API_PROTOCOL
ARG VITE_API_HOST
ARG VITE_API_PORT

ENV VITE_API_PROTOCOL=${VITE_API_PROTOCOL}
ENV VITE_API_HOST=${VITE_API_HOST}
ENV VITE_API_PORT=${VITE_API_PORT}

RUN npm run build

# Create a second stage to run the application
FROM node:${ALPINE_VERSION}

# Create a non-root user in the runtime image
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set working directory
WORKDIR /app

# Install serve globally
RUN npm install -g serve

# Copy built files from the build stage
COPY --from=build --chown=appuser:appgroup /app/dist /app/dist

# Expose ports (both dev port 5173 and production port 8080)
EXPOSE 5173 8080

# Switch to non-root user
USER appuser

# Define healthcheck - will use 5173 for dev mode, 8080 for production
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -q -O- http://localhost:${PORT:-5173} || exit 1

# Use PORT environment variable with default to 5173 for development
ENV PORT=5173
CMD ["sh", "-c", "serve -s dist -l ${PORT}"]
