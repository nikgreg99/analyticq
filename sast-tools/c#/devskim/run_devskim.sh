#!/bin/sh

CODE_DIR="/code"
OUTPUT_DIR="/output"
REPORT_FILE="$OUTPUT_DIR/devskim-report.sarif"

echo "[$(date)] Checking DevSkim version..."

if ! command -v devskim > /dev/null; then
    echo "DevSkim is not installed or not in PATH!"
    echo "Install it using: dotnet tool install --global Microsoft.CST.DevSkim.CLI"
    exit 1
else
    DEVSKIM_VERSION=$(devskim --version 2>&1 | head -n 1)
    echo "DevSkim version $DEVSKIM_VERSION"
fi

mkdir -p "$OUTPUT_DIR"

# Check for .NET files specifically
if ! find "$CODE_DIR" \( -name "*.cs" -o -name "*.vb" -o -name "*.fs" -o -name "*.csproj" -o -name "*.vbproj" -o -name "*.fsproj" \) | grep -q .; then
    echo "No .NET files found in $CODE_DIR to analyze!"
    exit 1
fi

echo "[$(date)] Running DevSkim analysis..."
devskim analyze \
    -I "$CODE_DIR" \
    -O "$REPORT_FILE" \
    -f sarif \

# Check if DevSkim ran successfully
if [ $? -eq 0 ]; then
    echo "[$(date)] Analysis complete. SARIF report saved to: $REPORT_FILE"


    if command -v jq > /dev/null; then
        ISSUE_COUNT=$(jq '.runs[].results | length' "$REPORT_FILE" 2>/dev/null || echo "Unknown")
        echo "Found $ISSUE_COUNT potential security issues."
    fi

    exit 0
else
    echo "DevSkim analysis failed!"
    exit 1
fi
