#!/bin/sh

# Universal JavaScript ESLint Analysis Script
# Works with any JavaScript repository structure

CODE_DIR="${CODE_DIR:-/code}"
OUTPUT_DIR="${OUTPUT_DIR:-/output}"
ESLINT_CONFIG="$CODE_DIR/eslint.config.cjs"
JSON_FILE="$OUTPUT_DIR/eslint-report.json"
HTML_FILE="$OUTPUT_DIR/eslint-report.html"

# Color output for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo "[$(date)] $1"
}

log_error() {
    echo "${RED}[$(date)] ERROR: $1${NC}" >&2
}

log_success() {
    echo "${GREEN}[$(date)] SUCCESS: $1${NC}"
}

log_warning() {
    echo "${YELLOW}[$(date)] WARNING: $1${NC}"
}

# Check ESLint installation
log_info "Checking ESLint version..."
if ! command -v eslint >/dev/null 2>&1; then
    log_error "ESLint is not installed or not in PATH!"
    log_info "Install with: npm install -g eslint"
    exit 1
else
    ESLINT_VERSION=$(eslint -v 2>/dev/null || echo "unknown")
    log_info "ESLint version: $ESLINT_VERSION"
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Handle ESLint configuration
if [ -f "$CODE_DIR/eslint.config.js" ] || [ -f "$CODE_DIR/eslint.config.mjs" ] || [ -f "$CODE_DIR/eslint.config.cjs" ]; then
    log_info "Using existing ESLint config from repository"
    ESLINT_CONFIG=""
elif [ -f "$CODE_DIR/.eslintrc.js" ] || [ -f "$CODE_DIR/.eslintrc.json" ] || [ -f "$CODE_DIR/.eslintrc.yml" ]; then
    log_info "Using legacy ESLint config from repository"
    ESLINT_CONFIG=""
elif [ -f "/eslint/eslint.config.js" ]; then
    log_info "Copying default ESLint config to $ESLINT_CONFIG..."
    cp /eslint/eslint.config.js "$ESLINT_CONFIG"
else
    log_warning "No ESLint config found. Creating basic config..."
    cat > "$ESLINT_CONFIG" << 'EOF'
module.exports = [
    {
        languageOptions: {
            ecmaVersion: "latest",
            sourceType: "module"
        },
        rules: {
            "no-unused-vars": "warn",
            "no-undef": "error",
            "no-console": "warn",
            "semi": ["error", "always"],
            "quotes": ["error", "single"]
        }
    }
];
EOF
fi

# Find JavaScript files with comprehensive patterns
log_info "Scanning for JavaScript files..."
JS_FILES=$(find "$CODE_DIR" \
    -type f \
    \( -name "*.js" -o -name "*.mjs" -o -name "*.cjs" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" \) \
    ! -path "*/node_modules/*" \
    ! -path "*/dist/*" \
    ! -path "*/build/*" \
    ! -path "*/.git/*" \
    ! -path "*/coverage/*" \
    ! -name "*.min.js" \
    2>/dev/null)

if [ -z "$JS_FILES" ]; then
    log_error "No JavaScript/TypeScript files found in $CODE_DIR to analyze!"
    log_info "Searched for: *.js, *.mjs, *.cjs, *.jsx, *.ts, *.tsx"
    log_info "Excluded: node_modules, dist, build, .git, coverage, *.min.js"
    exit 1
else
    FILE_COUNT=$(echo "$JS_FILES" | wc -l)
    log_info "Found $FILE_COUNT files to lint:"
    echo "$JS_FILES" | head -10
    if [ "$FILE_COUNT" -gt 10 ]; then
        log_info "... and $((FILE_COUNT - 10)) more files"
    fi
fi

# Change to code directory
cd "$CODE_DIR" || {
    log_error "Cannot change to directory: $CODE_DIR"
    exit 1
}

# Build ESLint command
ESLINT_CMD="npx eslint"

# Add config parameter if we have a custom config
if [ -n "$ESLINT_CONFIG" ] && [ -f "$ESLINT_CONFIG" ]; then
    ESLINT_CMD="$ESLINT_CMD --config $ESLINT_CONFIG"
fi

# Add file extensions
ESLINT_CMD="$ESLINT_CMD --ext .js,.mjs,.cjs,.jsx,.ts,.tsx"

# Add output format and target
ESLINT_CMD="$ESLINT_CMD -f json ./"

log_info "Running ESLint analysis..."
log_info "Command: $ESLINT_CMD"

# Run ESLint and capture output
if eval "$ESLINT_CMD" > "$JSON_FILE" 2>&1; then
    EXIT_CODE=0
else
    EXIT_CODE=$?
fi

# Always try to generate reports if JSON file exists and has content
if [ -f "$JSON_FILE" ] && [ -s "$JSON_FILE" ]; then
    # Count issues
    ERROR_COUNT=$(grep -o '"severity":2' "$JSON_FILE" | wc -l || echo "0")
    WARNING_COUNT=$(grep -o '"severity":1' "$JSON_FILE" | wc -l || echo "0")

    log_info "Analysis complete!"
    log_info "Errors: $ERROR_COUNT, Warnings: $WARNING_COUNT"
    log_info "JSON report saved to: $JSON_FILE"

    # Generate HTML report if possible
    if command -v node >/dev/null 2>&1; then
        log_info "Generating HTML report..."
        npx eslint -f html ./ > "$HTML_FILE" 2>/dev/null || true
        if [ -f "$HTML_FILE" ] && [ -s "$HTML_FILE" ]; then
            log_info "HTML report saved to: $HTML_FILE"
        fi
    fi

    # Summary
    if [ $EXIT_CODE -eq 0 ]; then
        if [ "$ERROR_COUNT" -eq 0 ] && [ "$WARNING_COUNT" -eq 0 ]; then
            log_success "No issues found! Code looks clean."
        else
            log_success "Analysis completed with $WARNING_COUNT warnings."
        fi
    else
        log_warning "Analysis completed with issues (exit code: $EXIT_CODE)"
        log_info "Errors: $ERROR_COUNT, Warnings: $WARNING_COUNT"
    fi
else
    log_error "ESLint analysis failed with exit code: $EXIT_CODE"
    log_error "No output file generated or file is empty"
    if [ -f "$JSON_FILE" ]; then
        log_info "Partial output may be in: $JSON_FILE"
    fi
    exit 1
fi

# Exit with original ESLint exit code
exit $EXIT_CODE
