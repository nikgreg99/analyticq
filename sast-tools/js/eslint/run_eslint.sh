#!/bin/sh

CODE_DIR="/code"
OUTPUT_DIR="/output"
ESLINT_CONFIG="$CODE_DIR/eslint.config.cjs"  # Changed extension to .cjs
JSON_FILE="$OUTPUT_DIR/eslint-report.json"

echo "[$(date)] Checking ESLint version..."

if ! command -v eslint; then
    echo "ESLint is not installed or not in PATH!"
    exit 1
else
    echo "ESLint version $(eslint -v)"
fi

mkdir -p "$OUTPUT_DIR"
echo "Copying ESLint config to $ESLINT_CONFIG..."
cp /eslint/eslint.config.js "$ESLINT_CONFIG"  # Copy to .cjs file

# Check if there are JavaScript files in the /code directory (all types)
JS_FILES=$(find "$CODE_DIR" -name "*.js" -o -name "*.mjs" -o -name "*.cjs")
if [ -z "$JS_FILES" ]; then
    echo "No JavaScript files found in $CODE_DIR to analyze!"
    exit 1
else
    echo "[$(date)] Files to lint:"
    echo "$JS_FILES"
fi

cd "$CODE_DIR"

# Run ESLint with support for all JavaScript file types
npx eslint --debug -f json --ext .js,.mjs,.cjs ./ --config "$ESLINT_CONFIG" > "$JSON_FILE"

# Check if the command succeeded
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(date)] Analysis complete. JSON report saved to: $JSON_FILE"
    exit 0
else
    echo "ESLint analysis failed with exit code: $EXIT_CODE"
    if [ -f "$JSON_FILE" ]; then
        echo "Check $JSON_FILE for error details"
    fi
    exit 1
fi
