#!/bin/sh

CODE_DIR="/code"
OUTPUT_DIR="/output"
ESLINT_CONFIG="$CODE_DIR/eslint.config.js"  # Path to config file
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
cp /eslint/eslint.config.js "$ESLINT_CONFIG"


# Check if there are JavaScript files in the /code directory
JS_FILES=$(find "$CODE_DIR" -name "*.js")
if [ -z "$JS_FILES" ]; then
    echo "No JavaScript files found in $CODE_DIR to analyze!"
    exit 1
else
    echo "[$(date)] Files to lint:"
    echo "$JS_FILES"
fi

cd "$CODE_DIR"
# Run ESLint
npx eslint  --debug -f json ./*.js > "$JSON_FILE"

if [ $? -eq 0 ]; then
    echo "[$(date)] Analysis complete. JSON report saved to: $JSON_FILE"
    exit 0
else
    echo "ESLint analysis failed"
    exit 1
fi
