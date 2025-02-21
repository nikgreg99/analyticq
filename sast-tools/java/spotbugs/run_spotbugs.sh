#!/bin/sh

CODE_DIR="/code"
OUTPUT_DIR="/output"
SARIF_FILE="$OUTPUT_DIR/spotbugs-report.sarif"

mkdir -p "$OUTPUT_DIR"


# Check SpotBugs version
if command -v spotbugs >/dev/null 2>&1; then
    echo "SpotBugs version: $(spotbugs -version)"
else
    echo "Error: SpotBugs is not installed or not in PATH."
    exit 1
fi

if find "$CODE_DIR" -name "*.jar" | grep -q .; then
    echo "JAR files found . Analyzing "
    for jar in "$CODE_DIR"/*.jar; do
        echo " Analyzing JAR: $jar"
        spotbugs -textui --effort:max -low -sarif="$SARIF_FILE" target/*.jar
    done
elif ls *.java 1> /dev/null 2>&1; then
     echo "Compiling and analyzing Java source files..."
     mkdir -p "$CODE_DIR/target/classes"
     javac -d "$CODE_DIR/target/classes" "$CODE_DIR"/*.java
     spotbugs -textui -effort:max -low -maxHeap=512 -sarif="$SARIF_FILE" $CODE_DIR/target/classes
else
    echo "No Java files or modules found to analyze!"
    exit 1
fi

echo " Analysis complete. Results saved to $SARIF_FILE"
