#!/bin/bash

# SAST Tools Image Puller - Download from GitHub Container Registry
# Downloads pre-built SAST tool images from GitHub private registry

set -euo pipefail

# Default configuration
REGISTRY="ghcr.io"
ORGANIZATION=""
TOKEN=""
CONFIG_FILE="sast-tools-config.json"
TIMEOUT_MINUTES=5
TOOL_FILTER=()
VERBOSE=false
FORCE=false
HELP=false

# Configuration
LOG_FILE="pull.log"

# Initialize log file
echo "SAST Tools Image Pull Log - $(date)" > "$LOG_FILE"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Logging functions
write_log() {
    local message="$1"
    local level="${2:-INFO}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local log_entry="[$timestamp] [$level] $message"

    # Console output with colors
    case "$level" in
        "ERROR")
            echo -e "${RED}$log_entry${NC}" >&2
            ;;
        "SUCCESS")
            echo -e "${GREEN}$log_entry${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}$log_entry${NC}"
            ;;
        "VERBOSE")
            if [[ "$VERBOSE" == "true" ]]; then
                echo -e "${CYAN}$log_entry${NC}"
            fi
            ;;
        "DOCKER")
            echo -e "${MAGENTA}$log_entry${NC}"
            ;;
        *)
            echo "$log_entry"
            ;;
    esac

    # Write to log file
    echo "$log_entry" >> "$LOG_FILE"
}

# Test Docker availability
test_docker_available() {
    write_log "Checking Docker availability..."

    if command -v docker >/dev/null 2>&1; then
        if docker version --format "{{.Server.Version}}" >/dev/null 2>&1; then
            write_log "Docker is available and running" "SUCCESS"
            return 0
        else
            write_log "Docker is not available or daemon is not running" "ERROR"
            return 1
        fi
    else
        write_log "Docker command not found" "ERROR"
        return 1
    fi
}

# Check if image exists locally
test_image_exists() {
    local image_name="$1"

    if docker inspect "$image_name" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Authenticate with GitHub Container Registry
connect_github_registry() {
    local token="$1"
    local registry="${2:-ghcr.io}"

    if [[ -z "$token" ]]; then
        write_log "No token provided, attempting without authentication" "WARNING"
        return 0
    fi

    write_log "Authenticating with $registry..."

    if echo "$token" | docker login "$registry" --username "token" --password-stdin >/dev/null 2>&1; then
        write_log "Successfully authenticated with $registry" "SUCCESS"
        return 0
    else
        write_log "Authentication failed with $registry" "ERROR"
        return 1
    fi
}

# Load configuration from JSON file
get_sast_tools_config() {
    local config_file="$1"

    if [[ ! -f "$config_file" ]]; then
        write_log "Config file $config_file not found, using default configuration" "WARNING"
        get_default_config
        return
    fi

    if command -v jq >/dev/null 2>&1; then
        if jq empty "$config_file" >/dev/null 2>&1; then
            write_log "Loaded configuration from $config_file"
            cat "$config_file"
        else
            write_log "Failed to parse config file with jq" "ERROR"
            write_log "Using default configuration" "WARNING"
            get_default_config
        fi
    else
        write_log "jq not available, using default configuration" "WARNING"
        get_default_config
    fi
}

# Default configuration
get_default_config() {
    cat << 'EOF'
{
  "tools": [
    {
      "name": "bandit",
      "language": "python",
      "image": "bandit",
      "tag": "latest"
    },
    {
      "name": "semgrep",
      "language": "multi",
      "image": "semgrep",
      "tag": "latest"
    },
    {
      "name": "eslint",
      "language": "javascript",
      "image": "eslint-security",
      "tag": "latest"
    },
    {
      "name": "sonarqube-scanner",
      "language": "multi",
      "image": "sonar-scanner",
      "tag": "latest"
    },
    {
      "name": "codeql",
      "language": "multi",
      "image": "codeql",
      "tag": "latest"
    }
  ]
}
EOF
}

# Pull Docker image
get_docker_image() {
    local tool_json="$1"
    local registry="$2"
    local organization="$3"
    local force="$4"

    local name=$(echo "$tool_json" | jq -r '.name')
    local language=$(echo "$tool_json" | jq -r '.language')
    local image=$(echo "$tool_json" | jq -r '.image')
    local tag=$(echo "$tool_json" | jq -r '.tag // "latest"')

    local local_image_name="${image}:${tag}"
    local remote_image_name="${registry}/${organization}/${image}:${tag}"

    write_log "Processing: $name ($language)"
    write_log "Remote image: $remote_image_name" "VERBOSE"

    # Check if image exists locally
    local image_exists=false
    if test_image_exists "$local_image_name"; then
        image_exists=true
    fi

    if [[ "$image_exists" == "true" && "$force" != "true" ]]; then
        write_log "Image $local_image_name already exists locally (use --force to re-pull)" "WARNING"
        echo "SKIPPED"
        return
    fi

    # Pull the image
    write_log "Pulling image: $remote_image_name" "DOCKER"
    local pull_start=$(date +%s)

    if timeout "${TIMEOUT_MINUTES}m" docker pull "$remote_image_name" 2>&1; then
        # Tag with local name if different
        if [[ "$remote_image_name" != "$local_image_name" ]]; then
            write_log "Tagging as: $local_image_name" "DOCKER"
            docker tag "$remote_image_name" "$local_image_name"
        fi

        local pull_end=$(date +%s)
        local pull_duration=$((pull_end - pull_start))
        local duration_formatted=$(printf "%02d:%02d" $((pull_duration / 60)) $((pull_duration % 60)))

        write_log "Successfully pulled: $local_image_name (took $duration_formatted)" "SUCCESS"

        # Show image info if verbose
        if [[ "$VERBOSE" == "true" ]]; then
            local image_info=$(docker images "$local_image_name" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}")
            write_log "Image info: $image_info" "VERBOSE"
        fi

        echo "SUCCESS"
    else
        local pull_end=$(date +%s)
        local pull_duration=$((pull_end - pull_start))
        local duration_formatted=$(printf "%02d:%02d" $((pull_duration / 60)) $((pull_duration % 60)))

        write_log "Failed to pull: $remote_image_name (took $duration_formatted)" "ERROR"
        echo "FAILED"
    fi
}

# Main pull process
start_pull_process() {
    local registry="$1"
    local organization="$2"
    local config_file="$3"
    local force="$4"

    local pulled=0
    local skipped=0
    local failed=0
    local total=0

    local start_time=$(date +%s)
    write_log "Starting SAST tools pull process"
    write_log "Registry: $registry"
    write_log "Organization: $organization"

    if [[ "$force" == "true" ]]; then
        write_log "Force re-pull enabled"
    fi

    # Load configuration
    local config
    config=$(get_sast_tools_config "$config_file")

    # Check if jq is available for processing
    if ! command -v jq >/dev/null 2>&1; then
        write_log "jq is required for JSON processing but not found" "ERROR"
        return 1
    fi

    # Get tools array
    local tools
    tools=$(echo "$config" | jq -c '.tools[]')

    # Filter tools if specified
    if [[ ${#TOOL_FILTER[@]} -gt 0 ]]; then
        local filter_query="select("
        for i in "${!TOOL_FILTER[@]}"; do
            if [[ $i -gt 0 ]]; then
                filter_query="$filter_query or "
            fi
            filter_query="$filter_query.name == \"${TOOL_FILTER[$i]}\" or .language == \"${TOOL_FILTER[$i]}\""
        done
        filter_query="$filter_query)"

        tools=$(echo "$config" | jq -c ".tools[] | $filter_query")
        write_log "Filtered tools: ${TOOL_FILTER[*]}"
    fi

    if [[ -z "$tools" ]]; then
        write_log "No tools found to process" "WARNING"
        return 0
    fi

    # Count total tools
    total=$(echo "$tools" | wc -l)
    write_log "Found $total tool(s) to process"

    # Process each tool
    while IFS= read -r tool; do
        local result
        result=$(get_docker_image "$tool" "$registry" "$organization" "$force")

        case "$result" in
            "SUCCESS")
                ((pulled++))
                ;;
            "FAILED")
                ((failed++))
                ;;
            "SKIPPED")
                ((skipped++))
                ;;
        esac

        # Progress update
        local processed=$((pulled + skipped + failed))
        write_log "Progress: $processed/$total - Pulled: $pulled, Skipped: $skipped, Failed: $failed"
    done <<< "$tools"

    # Final summary
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local duration_formatted=$(printf "%02d:%02d:%02d" $((duration / 3600)) $(((duration % 3600) / 60)) $((duration % 60)))

    write_log "Pull process completed"
    write_log "Duration: $duration_formatted"
    write_log "Pulled: $pulled" "SUCCESS"
    write_log "Skipped: $skipped" "WARNING"
    if [[ $failed -gt 0 ]]; then
        write_log "Failed: $failed" "ERROR"
    else
        write_log "Failed: $failed" "INFO"
    fi

    # Show all SAST images if verbose
    if [[ "$VERBOSE" == "true" && $((pulled + skipped)) -gt 0 ]]; then
        write_log "Available SAST tool images:" "VERBOSE"
        while IFS= read -r tool; do
            local image=$(echo "$tool" | jq -r '.image')
            local tag=$(echo "$tool" | jq -r '.tag // "latest"')
            local image_name="${image}:${tag}"

            if test_image_exists "$image_name"; then
                local image_info=$(docker images "$image_name" --format "{{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}")
                write_log "  $image_info" "VERBOSE"
            fi
        done <<< "$tools"
    fi

    if [[ $failed -gt 0 ]]; then
        return 1
    else
        return 0
    fi
}

# Create sample configuration file
create_config_file() {
    local config_file="$1"

    cat > "$config_file" << 'EOF'
{
  "tools": [
    {
      "name": "bandit",
      "language": "python",
      "image": "bandit",
      "tag": "latest"
    }
  ]
}
EOF

    write_log "Created sample configuration file: $config_file" "SUCCESS"
}

# Show help
show_help() {
    cat << 'EOF'
SAST Tools Image Puller

Usage: ./pull-sast-tools.sh [OPTIONS]

This script pulls pre-built SAST tool Docker images from GitHub Container Registry.

Options:
  -h, --help               Show this help
  -v, --verbose            Show detailed output
  -f, --force              Force re-pull existing images
  -r, --registry URL       Registry URL (default: ghcr.io)
  -o, --organization ORG   GitHub organization/username (required)
  -t, --token TOKEN        GitHub Personal Access Token for private registry
  -c, --config FILE        Configuration file path (default: sast-tools-config.json)
  --timeout MINUTES        Pull timeout in minutes (default: 5)
  --filter TOOL            Filter specific tools or languages (can be used multiple times)

Environment Variables:
  GITHUB_TOKEN        GitHub token (alternative to --token parameter)
  SAST_REGISTRY_ORG   GitHub organization (alternative to --organization)

Examples:
  # Basic usage
  ./pull-sast-tools.sh --organization "myorg" --token "ghp_xxxx"

  # Using environment variables
  export GITHUB_TOKEN="ghp_xxxx"
  export SAST_REGISTRY_ORG="myorg"
  ./pull-sast-tools.sh

  # Pull specific tools
  ./pull-sast-tools.sh --organization "myorg" --filter "bandit"

  # Force re-pull with verbose output
  ./pull-sast-tools.sh --organization "myorg" --force --verbose

Dependencies:
  - docker: Docker CLI tool
  - jq: JSON processor for configuration parsing
  - timeout: Command timeout utility (usually available by default)

Configuration File Format (sast-tools-config.json):
{
  "tools": [
    {
      "name": "bandit",
      "language": "python",
      "image": "bandit",
      "tag": "latest"
    }
  ]
}

EOF
}

# Parse command line arguments
parse_arguments() {
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
            -r|--registry)
                REGISTRY="$2"
                shift 2
                ;;
            -o|--organization)
                ORGANIZATION="$2"
                shift 2
                ;;
            -t|--token)
                TOKEN="$2"
                shift 2
                ;;
            -c|--config)
                CONFIG_FILE="$2"
                shift 2
                ;;
            --timeout)
                TIMEOUT_MINUTES="$2"
                shift 2
                ;;
            --filter)
                TOOL_FILTER+=("$2")
                shift 2
                ;;
            *)
                write_log "Unknown option: $1" "ERROR"
                write_log "Use --help for more information" "INFO"
                exit 1
                ;;
        esac
    done
}

# Main execution
main() {
    write_log "SAST Tools Image Puller started"

    # Parse arguments
    parse_arguments "$@"

    if [[ "$HELP" == "true" ]]; then
        show_help
        exit 0
    fi

    # Get organization from environment if not provided
    if [[ -z "$ORGANIZATION" ]]; then
        ORGANIZATION="${SAST_REGISTRY_ORG:-}"
        if [[ -z "$ORGANIZATION" ]]; then
            write_log "Organization must be specified via --organization parameter or SAST_REGISTRY_ORG environment variable" "ERROR"
            write_log "Use --help for more information" "INFO"
            exit 1
        fi
    fi

    # Get token from environment if not provided
    if [[ -z "$TOKEN" ]]; then
        TOKEN="${GITHUB_TOKEN:-}"
    fi

    write_log "Target: $REGISTRY/$ORGANIZATION"

    # Test Docker availability
    if ! test_docker_available; then
        write_log "Please ensure Docker is installed and running" "ERROR"
        exit 1
    fi

    # Authenticate with registry
    if ! connect_github_registry "$TOKEN" "$REGISTRY"; then
        write_log "Failed to authenticate with registry" "ERROR"
        exit 1
    fi

    # Create sample config if it doesn't exist
    if [[ ! -f "$CONFIG_FILE" ]]; then
        write_log "Configuration file not found, creating sample: $CONFIG_FILE" "WARNING"
        create_config_file "$CONFIG_FILE"
    fi

    # Run pull process
    if start_pull_process "$REGISTRY" "$ORGANIZATION" "$CONFIG_FILE" "$FORCE"; then
        exit_code=0
    else
        exit_code=1
    fi

    write_log "Script completed with exit code: $exit_code"
    exit $exit_code
}

# Execute main function with all arguments
main "$@"
