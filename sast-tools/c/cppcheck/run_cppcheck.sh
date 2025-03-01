#!/bin/bash

CODE_DIR="/code"
OUTPUT_DIR="/output"
REPORT_FILE_PATH="$OUTPUT_DIR/cppcheck-report.xml"

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

echo "[$(date)] Checking Cppcheck version..."
if ! command -v cppcheck &> /dev/null; then
    echo "Cppcheck is not installed or not in PATH!"
    exit 1
fi

echo "Cppcheck version: $(cppcheck --version)"

# Verify source files exist
if ! find "$CODE_DIR" -type f \( -name "*.c" -o -name "*.cpp" -o -name "*.h" -o -name "*.hpp" \) | grep -q .; then
    echo "No C/C++ source files found in $CODE_DIR!"
    exit 1
fi

echo "[$(date)] Running Cppcheck analysis..."
cppcheck --enable=all --xml --output-file="$REPORT_FILE_PATH" "$CODE_DIR"

# Check if Cppcheck executed successfully
if [ $? -eq 0 ]; then
    echo "[$(date)] Analysis complete. Report saved to: $REPORT_FILE_PATH"
else
    echo "Cppcheck analysis failed!"
    exit 1
fi
