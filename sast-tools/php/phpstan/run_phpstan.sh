#!/bin/sh

CODE_DIR="/code"
OUTPUT_DIR="/output"
JSON_FILE="$OUTPUT_DIR/phpstan-report.json"
PHPSTAN_CONFIG_FILE="/phpstan/phpstan.neon"

echo "[$(date)] Checking PHPStan version..."

if ! command -v phpstan ; then
    echo "PHPStan is not installed or not in PATH!"
    exit 1
else
    echo "PHPStan version $(phpstan --version)"
fi


mkdir -p "$OUTPUT_DIR"

if ! find "$CODE_DIR" -name "*.php" | grep -q .; then
    echo "No PHP files found in $CODE_DIR to analyze!"
    exit 1
fi

if [ ! -f "$PHPSTAN_CONFIG_FILE" ]; then
    echo "PHPStan configuration file ($PHPSTAN_CONFIG_FILE) not found!"
    exit 1
fi

echo "[$(date)] Running PHPStan analysis..."
phpstan analyse "$CODE_DIR" --configuration="$PHPSTAN_CONFIG_FILE" --error-format=prettyJson  > "$JSON_FILE"


# Check if PHPStan ran successfully
if [ $? -ne 0 ]; then
    echo "[$(date)] Analysis complete. JSON report saved to: $JSON_FILE"
    exit 0
else
    echo "PHPStan analysis failed!"
    exit 1
fi
