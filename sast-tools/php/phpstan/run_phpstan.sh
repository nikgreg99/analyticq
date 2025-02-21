#!/bin/bash

CODE_DIR="/code"
OUTPUT_DIR="/output"
JSON_FILE="$OUTPUT_DIR/phpstan-report.json"
PHPSTAN_CONFIG="$CODE_DIR/phpstan.neon"

echo "[$(date)] Checking PHPStan version..."

if ! command -v phpstan &>/dev/null; then
    echo "PHPStan is not installed or not in PATH!" >&2
    exit 1
fi

# Crea la directory di output se non esiste
mkdir -p "$OUTPUT_DIR"

# Verifica la presenza di file PHP
if ! find "$CODE_DIR" -name "*.php" | grep -q .; then
    echo "No PHP files found in $CODE_DIR to analyze!" >&2
    exit 1
fi

# Check if the PHPStan config file exists
if [ ! -f "$PHPSTAN_CONFIG" ]; then
    echo "PHPStan configuration file ($PHPSTAN_CONFIG) not found!" >&2
    exit 1
fi

echo "[$(date)] Running PHPStan analysis..."
phpstan analyse -c="$PHPSTAN_CONFIG" --error-format=json "$CODE_DIR" > "$JSON_FILE"

# Check if PHPStan ran successfully
if [ $? -ne 0 ]; then
    echo "PHPStan analysis failed!" >&2
    exit 1
fi

echo "[$(date)] Analysis complete. JSON report saved to: $JSON_FILE"
