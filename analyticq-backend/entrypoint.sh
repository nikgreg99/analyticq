#!/bin/bash

set -e

echo "=== Docker Permission Setup ==="

# Function to fix docker group permissions
fix_docker_permissions() {
    if [ -S /var/run/docker.sock ]; then
        echo "Docker socket found, checking permissions..."

        # Get the actual GID of the docker socket
        DOCKER_SOCKET_GID=$(stat -c '%g' /var/run/docker.sock)
        echo "Docker socket GID: $DOCKER_SOCKET_GID"

        # Get current user info
        CURRENT_USER=$(whoami)
        CURRENT_UID=$(id -u)
        CURRENT_GID=$(id -g)

        echo "Current user: $CURRENT_USER (UID: $CURRENT_UID, GID: $CURRENT_GID)"

        # Check if docker group exists and get its GID
        DOCKER_GROUP_GID=$(getent group docker | cut -d: -f3 2>/dev/null || echo "")

        if [ -n "$DOCKER_GROUP_GID" ] && [ "$DOCKER_GROUP_GID" != "$DOCKER_SOCKET_GID" ]; then
            echo "Docker group GID ($DOCKER_GROUP_GID) doesn't match socket GID ($DOCKER_SOCKET_GID)"
            echo "This is expected - the host's docker socket GID is different from container's docker group"
        fi

        # Check if user can access docker socket
        if groups $CURRENT_USER | grep -q docker; then
            echo "User $CURRENT_USER is in docker group"
        else
            echo "WARNING: User $CURRENT_USER is NOT in docker group"
        fi

        # Try to access docker - if it fails, we'll continue anyway as the socket might become available
        echo "Testing docker access..."
        if docker version >/dev/null 2>&1; then
            echo "✅ Docker access working"
        else
            echo "❌ Docker access failed - this might be normal if daemon isn't ready yet"
        fi
    else
        echo "⚠️  Docker socket not found at /var/run/docker.sock"
        echo "Make sure to mount it: -v /var/run/docker.sock:/var/run/docker.sock"
    fi
}

# Run the permission fix
fix_docker_permissions

echo "=== Waiting for Docker Daemon ==="

MAX_WAIT=120
WAIT_TIME=0
INTERVAL=2

until docker info >/dev/null 2>&1; do
    if [ $WAIT_TIME -ge $MAX_WAIT ]; then
        echo "ERROR: Docker daemon not ready after ${MAX_WAIT}s"
        echo ""
        echo "=== Debugging Information ==="
        echo "Docker socket permissions:"
        ls -la /var/run/docker.sock 2>/dev/null || echo "Socket not found"
        echo ""
        echo "Current user groups:"
        groups
        echo ""
        echo "Docker group info:"
        getent group docker 2>/dev/null || echo "Docker group not found"
        echo ""
        echo "Last docker error:"
        docker info 2>&1 || true
        echo "=========================="
        exit 1
    fi

    echo "Docker daemon not ready, waiting... (${WAIT_TIME}s/${MAX_WAIT}s)"
    sleep $INTERVAL
    WAIT_TIME=$((WAIT_TIME + INTERVAL))
done

echo "✅ Docker daemon is ready (waited ${WAIT_TIME}s)"

# Authenticate with private registry if credentials are provided
if [ -n "$DOCKER_REGISTRY_TOKEN" ] && [ -n "$DOCKER_REGISTRY_USER" ]; then
    echo "Authenticating with private registry..."
    echo "$DOCKER_REGISTRY_TOKEN" | docker login ghcr.io -u "$DOCKER_REGISTRY_USER" --password-stdin
    echo "Successfully authenticated with registry"
elif [ -f "/tmp/registry-token" ]; then
    echo "Authenticating with private registry using token file..."
    cat /tmp/registry-token | docker login ghcr.io -u "$DOCKER_REGISTRY_USER" --password-stdin
    echo "Successfully authenticated with registry"
else
    echo "Warning: No registry credentials provided. Attempting anonymous access..."
fi

echo "Checking and pulling SAST tool images..."

# Function to check if image exists locally
check_and_pull_image() {
    local image=$1
    if ! docker image inspect "$image" >/dev/null 2>&1; then
        echo "Pulling $image..."
        docker pull "$image"
    else
        echo "Image $image already exists locally, skipping pull"
    fi
}

# List of SAST tool images
SAST_IMAGES=(
    "ghcr.io/nikgreg99/analyticq/bearer:latest"
    "ghcr.io/nikgreg99/analyticq/eslint:latest"
    "ghcr.io/nikgreg99/analyticq/njjscan:latest"
    "ghcr.io/nikgreg99/analyticq/gosec:latest"
    "ghcr.io/nikgreg99/analyticq/staticcheck:latest"
    "ghcr.io/nikgreg99/analyticq/cppcheck:latest"
    "ghcr.io/nikgreg99/analyticq/flawfinder:latest"
    "ghcr.io/nikgreg99/analyticq/bandit:latest"
    "ghcr.io/nikgreg99/analyticq/pyright:latest"
    "ghcr.io/nikgreg99/analyticq/pylint:latest"
    "ghcr.io/nikgreg99/analyticq/flake8:latest"
    "ghcr.io/nikgreg99/analyticq/brakeman:latest"
    "ghcr.io/nikgreg99/analyticq/rubocop:latest"
    "ghcr.io/nikgreg99/analyticq/spotbugs:latest"
    "ghcr.io/nikgreg99/analyticq/checkstyle:latest"
    "ghcr.io/nikgreg99/analyticq/phpstan:latest"
)

# Pull images in parallel (only if they don't exist)
(
    for image in "${SAST_IMAGES[@]}"; do
        check_and_pull_image "$image" &
    done
    wait
    echo "SAST tool images check/pull completed"
) &

echo "Starting AnalyticQ Backend..."
exec python start.py
