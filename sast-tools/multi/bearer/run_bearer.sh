#!/bin/bash
set -e

CODE_DIR="/code"
OUTPUT_DIR="/output"
REPORT_FILE="$OUTPUT_DIR/bearer-report.json"

mkdir -p "$OUTPUT_DIR"

# Check if Bearer CLI is installed
if ! command -v bearer ; then
  echo "Error: Bearer CLI is not installed or not in PATH."
  exit 1
fi

detect_language_files() {
  ruby_files=$(find "$CODE_DIR" -name "*.rb" | wc -l)
  js_files=$(find "$CODE_DIR" \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" \) | wc -l)
  java_files=$(find "$CODE_DIR" -name "*.java" | wc -l)
  php_files=$(find "$CODE_DIR" -name "*.php" | wc -l)
  go_files=$(find "$CODE_DIR" -name "*.go" | wc -l)
  python_files=$(find "$CODE_DIR" \( -name "*.py" -o -name "*.pyw" \) | wc -l)

  echo "Detected files:"
  echo "  Ruby: $ruby_files"
  echo "  JavaScript/TypeScript: $js_files"
  echo "  Java: $java_files"
  echo "  PHP: $php_files"
  echo "  Go: $go_files"
  echo "  Python: $python_files"
}

detect_language_files


if find "$CODE_DIR" \( -name "*.rb" -o -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.java" -o -name "*.php" -o -name "*.go" -o -name "*.py" -o -name "*.pyw" \) | grep -q .; then

  echo "Supported language files found. Running Bearer analysis..."
  # Run Bearer CLI with appropriate flags for each language
  bearer scan  \
    --debug  \
    --format=json \
    --output="$REPORT_FILE" \
    --scanner=sast \
    --exit-code=0 \
    "$CODE_DIR"

  # Check if the analysis was successful
  if [ $? -eq 0 ]; then
    echo "Bearer analysis completed successfully."
    echo "Report generated at: $REPORT_FILE"
    cat $REPORT_FILE
  else
    echo "Bearer analysis failed."
    exit 1
  fi

  exit 0
else
  echo "No supported language files found to analyze!"
  echo "Bearer CLI supports Ruby, JavaScript/TypeScript, Java, PHP, Go, and Python."
  exit 1
fi
