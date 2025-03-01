#!/bin/sh

CODE_DIR="/code"
OUTPUT_DIR="/output"
JSON_FILE="$OUTPUT_DIR/rubocop-report.json"

echo "[$(date)] Checking RuboCop version..."

if ! command -v rubocop; then
    echo "Rubocop is not installed or not in PATH!"
    exit 1
else
    echo "Rubcop version $(rubocop -v)"
fi

mkdir -p "$OUTPUT_DIR"

if ! find "$CODE_DIR" -name "*.rb" | grep -q .; then
    echo "No Ruby files found in $CODE_DIR to analyze!"
    exit 1
fi

rubocop --format json --out "$JSON_FILE" "$CODE_DIR"

if [ $? -eq 0 ]; then
    echo "Rubocop analysis failed"
    exit 1
else
   echo "[$(date)] Analysis complete. JSON report saved to: $JSON_FILE"
    exit 0
fi
