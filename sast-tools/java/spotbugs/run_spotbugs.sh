#!/bin/bash
set -e

# Configuration
CODE_DIR="${CODE_DIR:-/code}"
OUTPUT_DIR="${OUTPUT_DIR:-/output}"
SARIF_FILE="$OUTPUT_DIR/spotbugs-report.sarif"
SCAN_DEPTH="${SCAN_DEPTH:-3}"
DEBUG="${DEBUG:-true}"

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}
debug_log() {
    [ "$DEBUG" = "true" ] && echo "[DEBUG] $*"
}
error_exit() {
    echo "Error: $1" >&2
    exit 1
}

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Tool verification
command -v spotbugs >/dev/null || error_exit "SpotBugs not found in PATH"
command -v mvn >/dev/null || error_exit "mvn not found in PATH"

log "Starting SpotBugs analysis on $CODE_DIR"
[ -d "$CODE_DIR" ] || error_exit "Code directory $CODE_DIR does not exist"

# Locate pom.xml
POM_FILE=""
if [ -f "$CODE_DIR/pom.xml" ]; then
    POM_FILE="$CODE_DIR/pom.xml"
    log "Found pom.xml in root of code directory"
else
    log "Searching for pom.xml in $CODE_DIR (max depth: $SCAN_DEPTH)..."
    POM_CANDIDATES=$(find "$CODE_DIR" -maxdepth "$SCAN_DEPTH" -name "pom.xml" -type f)
    debug_log "Found candidates:\n$POM_CANDIDATES"

    if [ -n "$POM_CANDIDATES" ]; then
        POM_FILE=$(echo "$POM_CANDIDATES" | head -n 1)
        log "Found pom.xml at $POM_FILE"
    else
        log "No pom.xml found, falling back to manual compilation"
    fi
fi

TARGET_DIR=""
if [ -n "$POM_FILE" ]; then
    PROJECT_DIR=$(dirname "$POM_FILE")
    log "Building project with Maven in $PROJECT_DIR"
    if mvn -f "$POM_FILE" clean compile -q -Dmaven.test.skip=true; then
        TARGET_DIR="$PROJECT_DIR/target/classes"
        log "Maven build successful"
    else
        log "Maven build failed, will try manual compilation"
    fi
fi

# Manual compilation
if [ -z "$TARGET_DIR" ]; then
    log "🔧 Manual compilation starting..."
    TARGET_DIR="/tmp/classes"
    mkdir -p "$TARGET_DIR"

    JAVA_FILES=$(find "$CODE_DIR" -name "*.java" -type f)
    debug_log "Found Java files:\n$JAVA_FILES"
    [ -n "$JAVA_FILES" ] || error_exit "No Java files found"

    CLASSPATH=$(find "$CODE_DIR" -name "*.jar" -type f | tr '\n' ':' | sed 's/:$//')
    debug_log "Classpath: $CLASSPATH"

    javac -d "$TARGET_DIR" ${CLASSPATH:+-cp "$CLASSPATH"} $JAVA_FILES || error_exit "Compilation failed"
    log "Manual compilation successful"
fi

# Verify compiled classes
[ -d "$TARGET_DIR" ] || error_exit "Compiled target directory $TARGET_DIR not found"
CLASS_COUNT=$(find "$TARGET_DIR" -name "*.class" | wc -l)
[ "$CLASS_COUNT" -gt 0 ] || error_exit "No .class files found after compilation"
debug_log "Compiled .class files count: $CLASS_COUNT"

# Prepare for SpotBugs
log "Running SpotBugs analysis..."
if command -v jar >/dev/null; then
    JAR_FILE="/tmp/analysis.jar"
    (cd "$TARGET_DIR" && jar cf "$JAR_FILE" .)
    ANALYZE_TARGET="$JAR_FILE"
    debug_log "Created JAR at $JAR_FILE"
else
    ANALYZE_TARGET="$TARGET_DIR"
    debug_log "Using directory $TARGET_DIR for analysis"
fi

log "Executing SpotBugs with SARIF output redirected to $SARIF_FILE"
spotbugs -textui -effort:max -low -sarif "$ANALYZE_TARGET" > "$SARIF_FILE" || {
    [ -s "$SARIF_FILE" ] || error_exit "SpotBugs analysis failed or SARIF report is empty"
}

# Check if report is generated
if [ -f "$SARIF_FILE" ]; then
    log "Analysis complete - report generated successfully"
    log "Report saved to $SARIF_FILE"
else
    error_exit "Analysis failed - no report generated"
fi
