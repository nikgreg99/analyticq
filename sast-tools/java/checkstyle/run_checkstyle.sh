#!/bin/sh
set -e

CODE_DIR="/code"
OUTPUT_DIR="/output"
CONFIG_FILE="/checkstyle/config.xml"
SARIF_FILE="$OUTPUT_DIR/checkstyle-report.sarif"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Check if code directory exists and is not empty
if [ ! -d "$CODE_DIR" ]; then
    echo "Error: Code directory '$CODE_DIR' does not exist."
    exit 1
fi

# Check if code directory contains any files
if [ -z "$(ls -A "$CODE_DIR")" ]; then
    echo "Error: Code directory '$CODE_DIR' is empty."
    exit 1
fi

# Check for checkstyle
if [ ! -f "/checkstyle/checkstyle-${CHECKSTYLE_VERSION}-all.jar" ]; then
    echo "Error: Checkstyle JAR not found at expected location."
    exit 1
fi

echo "CheckStyle version: ${CHECKSTYLE_VERSION}"

# Check if Java files exist
if find "$CODE_DIR" -name "*.java" | grep -q .; then
    echo "Java source files found. Analyzing..."

    # Count Java files for reporting
    java_files_count=$(find "$CODE_DIR" -name "*.java" | wc -l)
    echo "Found $java_files_count Java files to analyze"

    echo "Running CheckStyle analysis..."
    java -jar /checkstyle/checkstyle-${CHECKSTYLE_VERSION}-all.jar \
        -c "$CONFIG_FILE" \
        -f sarif \
        -o "$SARIF_FILE" \
        $(find "$CODE_DIR" -name "*.java")

    exit 0
else :
     echo "No Java files or JAR modules found to analyze!"
    exit 1
fi
