#!/bin/bash
set -e

# === CONFIGURATION ===
CODE_DIR="/code"
OUTPUT_DIR="/output"
TARGET_DIR=""
JAR_FILE=""
SARIF_FILE="$OUTPUT_DIR/spotbugs-report.sarif"
DEBUG=true

# === INITIAL SETUP ===
mkdir -p "$OUTPUT_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

debug_log() {
    if [ "$DEBUG" = true ]; then
        echo "[DEBUG] $*"
    fi
}

error_exit() {
    echo "❌ $1" >&2
    exit 1
}

# === DIAGNOSTICS ===
log "🔧 Starting SpotBugs analysis script with enhanced debugging"
log "📂 CODE_DIR is set to: $CODE_DIR"
log "📂 OUTPUT_DIR is set to: $OUTPUT_DIR"

if [ ! -d "$CODE_DIR" ]; then
    error_exit "CODE_DIR '$CODE_DIR' does not exist or is not a directory"
fi

debug_log "Contents of CODE_DIR:"
if [ "$DEBUG" = true ]; then
    ls -la "$CODE_DIR" 2>/dev/null || echo "  (Unable to list directory contents)"
fi

# === IMPROVED POM.XML DETECTION ===
find_pom() {
    log "🔍 Searching for pom.xml files..."

    # 1. Direct location check
    if [ -f "$CODE_DIR/pom.xml" ]; then
        debug_log "Found pom.xml at $CODE_DIR/pom.xml"
        echo "$CODE_DIR/pom.xml"
        return
    fi

    # 2. Parent directory check
    if [ -f "$CODE_DIR/../pom.xml" ]; then
        debug_log "Found pom.xml at $CODE_DIR/../pom.xml"
        echo "$CODE_DIR/../pom.xml"
        return
    fi

    # 3. Search with increasing depth
    for depth in 2 3 5 10; do
        debug_log "Searching for pom.xml with depth $depth..."
        local pom_file=$(find "$CODE_DIR" -maxdepth $depth -type f -name "pom.xml" -print -quit 2>/dev/null)
        if [ -n "$pom_file" ]; then
            debug_log "Found pom.xml at $pom_file (depth $depth)"
            echo "$pom_file"
            return
        fi
    done

    # 4. Full recursive search without depth limit
    debug_log "Performing full recursive search for pom.xml..."
    local pom_file=$(find "$CODE_DIR" -type f -name "pom.xml" -print -quit 2>/dev/null)
    if [ -n "$pom_file" ]; then
        debug_log "Found pom.xml at $pom_file (full search)"
        echo "$pom_file"
        return
    fi

    # 5. Search in all subdirectories and display results
    if [ "$DEBUG" = true ]; then
        log "Listing all files named pom.xml (for diagnostic purposes):"
        find / -name "pom.xml" 2>/dev/null | head -10 || echo "  (Unable to search globally)"
    fi

    debug_log "No pom.xml found"
    echo ""
}

# === CHECK FOR SPOTBUGS ===
if ! command -v spotbugs > /dev/null; then
    error_exit "SpotBugs is not installed or not in PATH."
fi

log "🔍 SpotBugs version: $(spotbugs -version)"

# === DETECT BUILD SYSTEM ===
PARENT_POM=$(find_pom)
if [ -n "$PARENT_POM" ]; then
    log "📌 Found Maven POM at: $PARENT_POM"
    BUILD_ROOT=$(dirname "$PARENT_POM")
    BUILD_TYPE="maven"

    # Verify it's a valid POM
    if ! grep -q '<project' "$PARENT_POM"; then
        log "⚠️ Found file named pom.xml but missing <project> tag"
        BUILD_TYPE="manual"
    fi
else
    log "ℹ️ No pom.xml found in codebase"
    BUILD_TYPE="manual"
fi

# === COMPILE SOURCE CODE ===
case "$BUILD_TYPE" in
    maven)
        if ! command -v mvn >/dev/null; then
            log "⚠️ Maven not found in PATH, falling back to manual compilation"
            BUILD_TYPE="manual"
        else
            log "🏗️ Building with Maven..."

            # Try to build with Maven
            if ! mvn -f "$PARENT_POM" clean compile -Dmaven.test.skip=true; then
                log "⚠️ Maven build failed, attempting manual compilation"
                BUILD_TYPE="manual"
            else
                TARGET_DIR="$BUILD_ROOT/target/classes"
                log "✅ Maven build successful - classes in $TARGET_DIR"
            fi
        fi
        ;;&  # Continue to manual case if Maven fails

    manual)
        [ "$BUILD_TYPE" = "manual" ] && log "🔧 Starting manual compilation..."
        TARGET_DIR="${TARGET_DIR:-/tmp/classes}"
        rm -rf "$TARGET_DIR" && mkdir -p "$TARGET_DIR"

        # Find all Java sources (handling spaces in paths)
        log "🔍 Searching for Java source files..."
        JAVA_SOURCES=()
        while IFS= read -r -d $'\0' file; do
            JAVA_SOURCES+=("$file")
        done < <(find -L "$CODE_DIR" -type f -name "*.java" -print0 2>/dev/null)

        if [ ${#JAVA_SOURCES[@]} -eq 0 ]; then
            error_exit "No Java source files found in $CODE_DIR"
        fi

        log "📝 Found ${#JAVA_SOURCES[@]} Java source files"
        if [ "$DEBUG" = true ] && [ ${#JAVA_SOURCES[@]} -lt 10 ]; then
            log "Java files:"
            for src in "${JAVA_SOURCES[@]}"; do
                log "  $src"
            done
        fi

        # Build classpath from discovered JARs
        log "🔍 Building classpath from JARs..."
        CLASSPATH=""
        JAR_COUNT=0
        while IFS= read -r -d $'\0' jar_file; do
            [ -n "$CLASSPATH" ] && CLASSPATH="$CLASSPATH:"
            CLASSPATH="$CLASSPATH$jar_file"
            JAR_COUNT=$((JAR_COUNT + 1))
        done < <(find -L "$CODE_DIR" -type f -name "*.jar" -print0 2>/dev/null)

        [ -n "$CLASSPATH" ] && log "📦 Found $JAR_COUNT JARs for classpath"

        log "🛠️ Compiling ${#JAVA_SOURCES[@]} Java files..."
        if ! javac -d "$TARGET_DIR" ${CLASSPATH:+-cp "$CLASSPATH"} "${JAVA_SOURCES[@]}"; then
            error_exit "Java compilation failed"
        fi

        log "✅ Compilation successful - classes in $TARGET_DIR"
        ;;
esac

# === VERIFY COMPILED CLASSES ===
if [ ! -d "$TARGET_DIR" ]; then
    error_exit "No compiled classes directory found at $TARGET_DIR"
fi

CLASS_COUNT=$(find "$TARGET_DIR" -type f -name "*.class" | wc -l)
if [ "$CLASS_COUNT" -eq 0 ]; then
    error_exit "No compiled .class files found in $TARGET_DIR"
fi
log "📊 Found $CLASS_COUNT compiled class files"

# === PACKAGE AND ANALYZE ===
if command -v jar >/dev/null; then
    JAR_FILE="/tmp/analysis.jar"
    log "📦 Creating analysis JAR..."
    (cd "$TARGET_DIR" && jar cf "$JAR_FILE" .) || error_exit "JAR creation failed"
    ANALYZE_TARGET="$JAR_FILE"
    log "📦 Analysis JAR created at $JAR_FILE"
else
    ANALYZE_TARGET="$TARGET_DIR"
    log "📂 Using class directory for analysis: $TARGET_DIR"
fi

log "🔍 Running SpotBugs..."
spotbugs -textui -effort:max -low -sarif "$SARIF_FILE" "$ANALYZE_TARGET" 2>&1 || {
    if [ -s "$SARIF_FILE" ]; then
        log "⚠️ Analysis completed with warnings"
    else
        error_exit "Analysis failed (empty report)"
    fi
}

# === REPORT SUMMARY ===
if [ -s "$SARIF_FILE" ]; then
    ISSUES=$(grep -c "\"level\":" "$SARIF_FILE" || echo "0")
    log "🐞 Found approximately $ISSUES potential issues"
else
    log "✅ No issues found"
fi

log "✅ Success - Report saved to $SARIF_FILE"
