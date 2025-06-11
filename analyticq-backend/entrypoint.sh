#!/bin/bash

set -e

echo "=== Docker-in-Docker Setup ==="

# Function to wait for Docker daemon to be ready
wait_for_docker_daemon() {
    echo "=== Waiting for Docker Daemon ==="

    MAX_WAIT=120
    WAIT_TIME=0
    INTERVAL=2

    # Check if docker command is available
    if ! command -v docker >/dev/null 2>&1; then
        echo "ERROR: Docker command not found"
        exit 1
    fi

    until docker info >/dev/null 2>&1; do
        if [ $WAIT_TIME -ge $MAX_WAIT ]; then
            echo "ERROR: Docker daemon not ready after ${MAX_WAIT}s"
            echo ""
            echo "=== Debugging Information ==="
            echo "Docker version:"
            docker version 2>&1 || echo "Failed to get Docker version"
            echo ""
            echo "Docker info:"
            docker info 2>&1 || echo "Failed to get Docker info"
            echo ""
            echo "Environment variables:"
            env | grep -i docker || echo "No Docker environment variables"
            echo ""
            echo "Process list:"
            ps aux | grep docker || echo "No Docker processes found"
            echo "=========================="
            exit 1
        fi

        echo "Docker daemon not ready, waiting... (${WAIT_TIME}s/${MAX_WAIT}s)"
        sleep $INTERVAL
        WAIT_TIME=$((WAIT_TIME + INTERVAL))
    done

    echo "✅ Docker daemon is ready (waited ${WAIT_TIME}s)"
}

# Function to authenticate with private registry
authenticate_registry() {
    if [ -n "$DOCKER_REGISTRY_TOKEN" ] && [ -n "$DOCKER_REGISTRY_USER" ]; then
        echo "Authenticating with private registry..."
        echo "$DOCKER_REGISTRY_TOKEN" | docker login "$DOCKER_REGISTRY" -u "$DOCKER_REGISTRY_USER" --password-stdin
        echo "Successfully authenticated with registry"
    elif [ -f "/tmp/registry-token" ]; then
        echo "Authenticating with private registry using token file..."
        cat /tmp/registry-token | docker login "$DOCKER_REGISTRY" -u "$DOCKER_REGISTRY_USER" --password-stdin
        echo "Successfully authenticated with registry"
    else
        echo "Warning: No registry credentials provided. Attempting anonymous access..."
    fi
}

# Function to extract simple name from full image name
get_simple_name() {
    local full_image=$1
    # Extract just the tool name from the full path
    # e.g., "ghcr.io/nikgreg99/analyticq/bearer:latest" -> "bearer:latest"
    echo "$full_image" | sed 's|.*/||'
}

# Function to check if image exists locally and pull/rename if needed
check_pull_and_rename_image() {
    local full_image=$1
    local simple_name=$(get_simple_name "$full_image")

    echo "Processing image: $full_image -> $simple_name"

    # Check if the simple name already exists
    if docker image inspect "$simple_name" >/dev/null 2>&1; then
        echo "Image $simple_name already exists locally, skipping"
        return 0
    fi

    # Check if full name exists locally
    if docker image inspect "$full_image" >/dev/null 2>&1; then
        echo "Full image $full_image exists, tagging as $simple_name"
        docker tag "$full_image" "$simple_name"
        # Optionally remove the original tag to save space
        # docker rmi "$full_image" >/dev/null 2>&1 || true
        return 0
    fi

    # Pull the image
    echo "Pulling $full_image..."
    if ! docker pull "$full_image"; then
        echo "Warning: Failed to pull $full_image"
        return 1
    fi

    # Tag with simple name
    echo "Tagging $full_image as $simple_name"
    docker tag "$full_image" "$simple_name"

    # Optionally remove the original tag to save space
    # Uncomment the next line if you want to remove the full registry path after tagging
    # docker rmi "$full_image" >/dev/null 2>&1 || true

    return 0
}

# Function to pull and rename SAST tool images
pull_and_rename_sast_images() {
    echo "Checking, pulling, and renaming SAST tool images..."

    # List of SAST tool images with their full registry paths
    declare -A SAST_IMAGES=(
        ["ghcr.io/nikgreg99/analyticq/bearer:latest"]="bearer:latest"
        ["ghcr.io/nikgreg99/analyticq/eslint:latest"]="eslint:latest"
        ["ghcr.io/nikgreg99/analyticq/njjscan:latest"]="njjscan:latest"
        ["ghcr.io/nikgreg99/analyticq/gosec:latest"]="gosec:latest"
        ["ghcr.io/nikgreg99/analyticq/staticcheck:latest"]="staticcheck:latest"
        ["ghcr.io/nikgreg99/analyticq/cppcheck:latest"]="cppcheck:latest"
        ["ghcr.io/nikgreg99/analyticq/flawfinder:latest"]="flawfinder:latest"
        ["ghcr.io/nikgreg99/analyticq/bandit:latest"]="bandit:latest"
        ["ghcr.io/nikgreg99/analyticq/pyright:latest"]="pyright:latest"
        ["ghcr.io/nikgreg99/analyticq/pylint:latest"]="pylint:latest"
        ["ghcr.io/nikgreg99/analyticq/flake8:latest"]="flake8:latest"
        ["ghcr.io/nikgreg99/analyticq/brakeman:latest"]="brakeman:latest"
        ["ghcr.io/nikgreg99/analyticq/rubocop:latest"]="rubocop:latest"
        ["ghcr.io/nikgreg99/analyticq/spotbugs:latest"]="spotbugs:latest"
        ["ghcr.io/nikgreg99/analyticq/checkstyle:latest"]="checkstyle:latest"
        ["ghcr.io/nikgreg99/analyticq/phpstan:latest"]="phpstan:latest"
    )

    # Process images sequentially to avoid overwhelming the system
    failed_images=()
    for full_image in "${!SAST_IMAGES[@]}"; do
        if ! check_pull_and_rename_image "$full_image"; then
            failed_images+=("$full_image")
        fi
    done

    if [ ${#failed_images[@]} -gt 0 ]; then
        echo "Warning: Failed to process the following images:"
        printf '%s\n' "${failed_images[@]}"
    fi

    echo "SAST tool images processing completed"
    echo ""
    echo "Available SAST tools (simple names):"
    for full_image in "${!SAST_IMAGES[@]}"; do
        simple_name=$(get_simple_name "$full_image")
        if docker image inspect "$simple_name" >/dev/null 2>&1; then
            echo "  ✅ $simple_name"
        else
            echo "  ❌ $simple_name (failed)"
        fi
    done
}

# Function to cleanup old/unused images
cleanup_images() {
    if [ "${CLEANUP_IMAGES:-false}" = "true" ]; then
        echo "Cleaning up unused images..."
        docker image prune -f
        echo "Image cleanup completed"
    fi
}

# Main execution
main() {
    echo "Current user: $(whoami)"
    echo "Current directory: $(pwd)"

    # Wait for Docker daemon to be ready
    wait_for_docker_daemon

    # Show Docker info
    echo "Docker daemon info:"
    docker version --format 'Client: {{.Client.Version}}, Server: {{.Server.Version}}'

    # Authenticate with registry
    authenticate_registry

    # Pull and rename SAST images
    pull_and_rename_sast_images

    # Optional cleanup
    cleanup_images

    echo "Starting AnalyticQ Backend..."
    exec python start.py
}

# Run main function
main
