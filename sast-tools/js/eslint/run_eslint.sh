#!/bin/sh
# Simple ESLint JSON Analysis Script with Root Config

CODE_DIR="${CODE_DIR:-/code}"
OUTPUT_DIR="${OUTPUT_DIR:-/output}"
JSON_FILE="$OUTPUT_DIR/eslint-report.json"
CONFIG_FILE="eslint/eslint.config.js"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Check if ESLint is available
if ! command -v npx >/dev/null 2>&1; then
    echo "ERROR: npx not found!"
    exit 1
fi

# Change to code directory
cd "$CODE_DIR" || {
    echo "ERROR: Cannot access directory: $CODE_DIR"
    exit 1
}


echo "Using config file: $CONFIG_FILE"
npx eslint --ext .js,.mjs,.cjs,.jsx,.ts,.tsx -f json ./ > "$JSON_FILE" 2>&1

EXIT_CODE=$?

# Check if output was generated and is valid JSON
if [ -f "$JSON_FILE" ] && [ -s "$JSON_FILE" ]; then
    # Try to validate JSON format
    if command -v node >/dev/null 2>&1; then
        if ! node -e "JSON.parse(require('fs').readFileSync('$JSON_FILE', 'utf8'))" 2>/dev/null; then
            echo "ERROR: Generated file is not valid JSON"
            echo "ESLint output:"
            cat "$JSON_FILE"
            exit 1
        fi
    fi
    echo "JSON report successfully saved to: $JSON_FILE"
    echo "ESLint exit code: $EXIT_CODE"
else
    echo "ERROR: No output generated or file is empty"
    if [ -f "$JSON_FILE" ]; then
        echo "ESLint output:"
        cat "$JSON_FILE"
    fi
    exit 1
fi

exit 0
