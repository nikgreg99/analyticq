import logging
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check Pylint version
result = subprocess.run(["sqlfluff", "version"], capture_output=True, text=True)
logger.info(f"Return code: {result.returncode}")

logger.info(f"SQLFluff version: {result.stdout}")

# Define paths
code_path = Path("/code")
output_path = Path("/output/sqlfluff-report.json")

# Check if /code directory exists and is not empty
if not code_path.exists() or not any(code_path.iterdir()):
    logger.error("Directory /code is empty or not mounted correctly.")
    sys.exit(1)

# Find all Python files
files_to_scan = [str(f) for f in code_path.rglob("*.sql")]

logger.info(f"Files to scan : {files_to_scan}")

# Form SQLFluff command
sqlfluff_command = ["sqlfluff", "lint"] + files_to_scan + ["--dialect ansi"]

logger.info(f"Running command: {' '.join(sqlfluff_command)}")

try:
    # Run Pylint
    logger.info("Running SQLFluff...")
    result = subprocess.run(
        sqlfluff_command,
        capture_output=True,
        text=True,
    )

    # Log Pylint output
    logger.info(f"SQLFluff stdout: {result.stdout}")
    if result.stderr:
        logger.error(f"SQLFluff stderr: {result.stderr}")

    # Save output to file
    output_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure output directory exists
    output_path.write_text(result.stdout)
    logger.info(f"SQLFluff output saved to {output_path}")

    # Log Pylint return code
    logger.info(f"SQLFluff return code: {result.returncode}")

    # Exit with 0 (success) regardless of Pylint findings
    sys.exit(0)

except subprocess.CalledProcessError as e:
    logger.error(f"Failed to run SQLFluff: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    sys.exit(1)
