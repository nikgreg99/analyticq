#!/bin/bash

# SAST Tools Docker Image Builder - Enhanced Version with Timeout Handling
# Builds Docker images for SAST tools in the sast-tools directory

set -euo pipefail  # Exit on error, undefined variables, and pipe failures

# Configuration
BASE_DIR="./sast-tools"
LOG_FILE="build.log"
TIMEOUT_MINUTES=10
VERBOSE=false
FORCE=false
HELP=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Logging functions
log() {
    local level="${2:-INFO}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local message="[$timestamp] [$level] $1"

    # Console output with colors
    case "$level" in
        "ERROR")
            echo -e "${RED}$message${NC}" ;;
        "SUCCESS")
            echo -e "${GREEN}$message${NC}" ;;
        "WARNING")
            echo -e "${YELLOW}$message${NC}" ;;
        "VERBOSE")
            if [[ "$VERBOSE" == true ]]; then
                echo -e "${CYAN}$message${NC}"
            fi ;;
        "DOCKER")
            echo -e "${MAGENTA}$message${NC}" ;;
        *)
            echo -e "${BLUE}$message${NC}" ;;
    esac

    # Write to log file
    echo "$message" >> "$LOG_FILE"
}

# Simple Docker availability test
test_docker_available() {
    log "Checking Docker availability..."

    if ! command -v docker &> /dev/null; then
        log "Docker command not found in PATH" "ERROR"
        return 1
    fi

    if ! docker version --format "{{.Server.Version}}" &> /dev/null; then
        log "Docker is not available or daemon is not running" "ERROR"
        return 1
    fi

    log "Docker is available and running" "SUCCESS"
    return 0
}

# Check if image exists
test_image_exists() {
    local image_name="$1"

    if docker inspect "$image_name" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Build Docker image with progress monitoring
build_docker_image() {
    local tool_path="$1"
    local image_name="$2"
    local force="$3"

    local full_path="${BASE_DIR}/${tool_path}"
    local dockerfile_path="${full_path}/Dockerfile"

    log "Processing: $image_name"
    log "Source: $full_path" "VERBOSE"

    # Check if Dockerfile exists
    if [[ ! -f "$dockerfile_path" ]]; then
        log "Dockerfile not found in $full_path" "ERROR"
        return 1
    fi

    # Check if image exists
    if test_image_exists "$image_name"; then
        if [[ "$force" != true ]]; then
            log "Image $image_name already exists (use --force to rebuild)" "WARNING"
            echo "SKIPPED"
            return 0
        fi
    fi

    # Show Dockerfile content if verbose
    if [[ "$VERBOSE" == true ]]; then
        log "Dockerfile content:" "VERBOSE"
        while IFS= read -r line; do
            log "  $line" "VERBOSE"
        done < "$dockerfile_path"
    fi

    # Build the image
    log "Building image: $image_name" "DOCKER"
    local build_start=$(date +%s)

    # Use timeout command if available
    local timeout_cmd=""
    if command -v timeout &> /dev/null; then
        timeout_cmd="timeout ${TIMEOUT_MINUTES}m"
    fi

    local build_output
    local build_success=false

    if build_output=$($timeout_cmd docker build -t "$image_name" "$full_path" 2>&1); then
        build_success=true
    fi

    local build_end=$(date +%s)
    local build_duration=$((build_end - build_start))
    local duration_formatted=$(printf "%02d:%02d" $((build_duration / 60)) $((build_duration % 60)))

    if [[ "$build_success" == true ]]; then
        log "Successfully built: $image_name (took $duration_formatted)" "SUCCESS"

        # Show image info if verbose
        if [[ "$VERBOSE" == true ]]; then
            local image_info=$(docker images "$image_name" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}")
            log "Image info: $image_info" "VERBOSE"
        fi

        return 0
    else
        log "Failed to build: $image_name (took $duration_formatted)" "ERROR"
        if [[ "$VERBOSE" == true ]]; then
            log "Build output:" "ERROR"
            echo "$build_output" | while IFS= read -r line; do
                log "  $line" "ERROR"
            done
        fi
        return 1
    fi
}

# Main build process
start_build_process() {
    local force="$1"

    declare -A stats=(
        ["built"]=0
        ["skipped"]=0
        ["failed"]=0
        ["total"]=0
    )

    local start_time=$(date +%s)
    log "Starting SAST tools build process"
    log "Base directory: $BASE_DIR"

    if [[ "$force" == true ]]; then
        log "Force rebuild enabled"
    fi

    # Check base directory
    if [[ ! -d "$BASE_DIR" ]]; then
        log "Base directory $BASE_DIR does not exist" "ERROR"
        return 1
    fi

    # Find all language directories
    local language_dirs=()
    while IFS= read -r -d '' dir; do
        language_dirs+=("$dir")
    done < <(find "$BASE_DIR" -maxdepth 1 -type d -not -path "$BASE_DIR" -print0 2>/dev/null || true)

    if [[ ${#language_dirs[@]} -eq 0 ]]; then
        log "No language directories found in $BASE_DIR" "WARNING"
        return 0
    fi

    log "Found ${#language_dirs[@]} language directory(ies)"

    # Process each language directory
    for lang_dir in "${language_dirs[@]}"; do
        local language=$(basename "$lang_dir")
        log "Processing language: $language"

        local tool_dirs=()
        while IFS= read -r -d '' dir; do
            tool_dirs+=("$dir")
        done < <(find "$lang_dir" -maxdepth 1 -type d -not -path "$lang_dir" -print0 2>/dev/null || true)

        if [[ ${#tool_dirs[@]} -eq 0 ]]; then
            log "No tools found in $language" "WARNING"
            continue
        fi

        log "Found ${#tool_dirs[@]} tool(s) in $language"

        for tool_dir in "${tool_dirs[@]}"; do
            local tool_name=$(basename "$tool_dir")
            local tool_path="$language/$tool_name"
            local image_name="${tool_name}:latest"

            ((stats["total"]++))

            local result
            if result=$(build_docker_image "$tool_path" "$image_name" "$force"); then
                if [[ "$result" == "SKIPPED" ]]; then
                    ((stats["skipped"]++))
                else
                    ((stats["built"]++))
                fi
            else
                ((stats["failed"]++))
            fi

            # Progress update
            local processed=$((stats["built"] + stats["skipped"] + stats["failed"]))
            log "Progress: $processed/${stats["total"]} - Built: ${stats["built"]}, Skipped: ${stats["skipped"]}, Failed: ${stats["failed"]}"
        done
    done

    # Final summary
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local duration_formatted=$(printf "%02d:%02d:%02d" $((duration / 3600)) $(((duration % 3600) / 60)) $((duration % 60)))

    log "Build process completed"
    log "Duration: $duration_formatted"
    log "Built: ${stats["built"]}" "SUCCESS"
    log "Skipped: ${stats["skipped"]}" "WARNING"

    if [[ ${stats["failed"]} -gt 0 ]]; then
        log "Failed: ${stats["failed"]}" "ERROR"
    else
        log "Failed: ${stats["failed"]}"
    fi

    # Show all images if verbose
    if [[ "$VERBOSE" == true ]] && [[ $((stats["built"] + stats["skipped"])) -gt 0 ]]; then
        log "Available images:" "VERBOSE"
        docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}" | grep ":latest" | while IFS= read -r line; do
            log "  $line" "VERBOSE"
        done
    fi

    if [[ ${stats["failed"]} -gt 0 ]]; then
        return 1
    else
        return 0
    fi
}

# Show help
show_help() {
    cat << 'EOF'
SAST Tools Docker Builder

Usage: ./build-sast-tools.sh [OPTIONS]

This script builds Docker images for SAST tools in the './sast-tools' directory.

Expected directory structure:
  sast-tools/
  ├── language1/
  │   ├── tool1/
  │   │   └── Dockerfile
  │   └── tool2/
  │       └── Dockerfile
  └── language2/
      └── tool3/
          └── Dockerfile

Options:
  -h, --help              Show this help
  -v, --verbose           Show detailed output
  -f, --force             Force rebuild existing images
  -t, --timeout MINUTES   Build timeout in minutes (default: 10)

Examples:
  ./build-sast-tools.sh
  ./build-sast-tools.sh --verbose
  ./build-sast-tools.sh --force
  ./build-sast-tools.sh --force --verbose --timeout 15

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                HELP=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -f|--force)
                FORCE=true
                shift
                ;;
            -t|--timeout)
                if [[ -n "${2:-}" ]] && [[ "$2" =~ ^[0-9]+$ ]]; then
                    TIMEOUT_MINUTES="$2"
                    shift 2
                else
                    echo "Error: --timeout requires a numeric argument" >&2
                    exit 1
                fi
                ;;
            *)
                echo "Error: Unknown option $1" >&2
                echo "Use --help for usage information" >&2
                exit 1
                ;;
        esac
    done
}

# Main execution
main() {
    # Parse command line arguments
    parse_args "$@"

    log "SAST Tools Docker Builder started"

    if [[ "$HELP" == true ]]; then
        show_help
        exit 0
    fi

    # Initialize log file
    echo "SAST Tools Docker Build Log - $(date)" > "$LOG_FILE"

    # Test Docker availability
    if ! test_docker_available; then
        log "Please ensure Docker Desktop is running" "ERROR"
        exit 1
    fi

    # Run build process
    local exit_code=0
    if ! start_build_process "$FORCE"; then
        exit_code=1
    fi

    log "Script completed with exit code: $exit_code"
    exit $exit_code
}

# Execute main function
main "$@"
