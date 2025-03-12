#!/bin/sh

CODE_DIR="/code"
OUTPUT_DIR="/output"
JSON_FILE="$OUTPUT_DIR/brakeman-report.json"

echo "[$(date)] Checking Brakeman version..."

if ! command -v brakeman; then
    echo "Brakeman is not installed or not in PATH!"
    exit 1
else
    echo "Brakeman version $(brakeman --version)"
fi

mkdir -p "$OUTPUT_DIR"

# Check if it's a Rails application by looking for key Rails files
if [ ! -f "$CODE_DIR/config/application.rb" ] || [ ! -d "$CODE_DIR/app" ]; then
    echo "No Rails application found in $CODE_DIR to analyze!"
    exit 1
fi

# Run Brakeman with JSON output
brakeman -a  -p "$CODE_DIR"  -o /dev/stdout -o "$JSON_FILE" --no-exit-on-warn

# Note: Brakeman returns 0 on successful scan, 1+ for errors
# This is different from your RuboCop script logic
if [ $? -eq 0 ]; then
    echo "[$(date)] Analysis complete. JSON report saved to: $JSON_FILE"
    exit 0
else
    echo "Brakeman analysis failed"
    exit 1
fi
