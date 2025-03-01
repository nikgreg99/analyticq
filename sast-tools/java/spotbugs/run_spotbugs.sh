#!/bin/sh
set -e

CODE_DIR="/code"
TARGET_DIR="/target/classes"
OUTPUT_DIR="/output"
SARIF_FILE="$OUTPUT_DIR/spotbugs-report.sarif"

mkdir -p "$OUTPUT_DIR"
mkdir -p "$TARGET_DIR"

if ! command -v spotbugs > /dev/null; then
    echo "Error: SpotBugs is not installed or not in PATH."
    exit 1
fi

echo "SpotBugs version: $(spotbugs -version)"

if find "$CODE_DIR" -name "*.jar" | grep -q .; then
    echo "JAR files found. Analyzing..."
    for jar in "$CODE_DIR"/*.jar; do
        echo "Analyzing JAR: $jar"
        spotbugs -textui -effort:max -low -sarif="$SARIF_FILE" "$jar"
    done
    exit 0
fi

if find "$CODE_DIR" -name "*.java" | grep -q .; then
    echo "Compiling and analyzing Java source files..."

    if ! command -v javac > /dev/null; then
        echo "Error: javac is not installed or not in PATH."
        exit 1
    fi

    # Compile all Java files including those in subpackages
    find "$CODE_DIR" -name "*.java" | xargs javac -d "$TARGET_DIR"

    echo "Running SpotBugs analysis..."
    spotbugs -textui -effort:max -low -maxHeap 512 -sarif="$SARIF_FILE" "$TARGET_DIR"
    exit 0
else
    echo "No Java files or JAR modules found to analyze!"
    exit 1
fi
