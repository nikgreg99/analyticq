#!/bin/sh

CODE_DIR="/code"
OUTPUT_DIR="/output"
SARIF_FILE="$OUTPUT_DIR/checkstyle-report.sarif"
CONFIG_FILE="/checkstyle/sun_checks.xml"

mkdir -p "$OUTPUT_DIR"

# Check if Checkstyle jar exists
if [ ! -f "/checkstyle/checkstyle.jar" ]; then
    echo "Error: Checkstyle JAR is not found."
    exit 1
fi

echo "Checkstyle version: $(java -jar /checkstyle/checkstyle.jar --version)"

# Check if we have a custom config file in the code directory
if [ -f "$CODE_DIR/checkstyle.xml" ]; then
    echo "Using custom configuration file from $CODE_DIR/checkstyle.xml"
    CONFIG_FILE="$CODE_DIR/checkstyle.xml"
else
    echo "Using default Sun Checks configuration"
    # Download Sun Checks if not present
    if [ ! -f "$CONFIG_FILE" ]; then
        wget -O "$CONFIG_FILE" "https://raw.githubusercontent.com/checkstyle/checkstyle/master/src/main/resources/sun_checks.xml"
    fi
fi

if find "$CODE_DIR" -name "*.java" | grep -q .; then
    echo "Analyzing Java source files with Checkstyle..."

    # Run Checkstyle with direct SARIF output
    java -jar /checkstyle/checkstyle.jar \
        -c "$CONFIG_FILE" \
        -f sarif \
        -o "$SARIF_FILE" \
        "$CODE_DIR"

    echo "Checkstyle analysis completed. Results saved to $SARIF_FILE"
    exit 0
else
    echo "No Java files found to analyze!"
    exit 1
fi
