import logging
import os
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ["TMPDIR"] = "/tmp"
# Check Pylint version
result = subprocess.run(["pylint", "--version"], capture_output=True, text=True)
logger.info(result.stderr)
logger.info(f"Return code: {result.returncode}")
logger.info(f"Pylint version: {result.stdout}")

# Define paths
code_path = Path("/code")
output_path = Path("/output/pylint-report.json")

# Check if /code directory exists and is not empty
if not code_path.exists() or not any(code_path.iterdir()):
    logger.error("Directory /code is empty or not mounted correctly.")
    sys.exit(1)

# Find all Python files
files_to_scan = [str(f) for f in code_path.rglob("*.py")]

# Check if it's a Python module (contains __init__.py or has at least one Python file)
is_python_module = any(f.name == "__init__.py" for f in code_path.rglob("__init__.py")) or bool(files_to_scan)

if not is_python_module:
    logger.error("No valid Python module found in the directory.")
    sys.exit(1)

logger.info(f"Files to scan : {files_to_scan}")

# Form Pylint command
pylint_command = ["pylint", "--output-format=json"] + files_to_scan

logger.info(f"Running command: {' '.join(pylint_command)}")

try:
    # Run Pylint
    logger.info("Running Pylint...")
    result = subprocess.run(
        pylint_command,
        capture_output=True,
        text=True,
    )

    # Log Pylint output
    logger.info(f"Pylint stdout: {result.stdout}")
    if result.stderr:
        logger.error(f"Pylint stderr: {result.stderr}")

    # Save output to file
    output_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure output directory exists
    output_path.write_text(result.stdout)
    logger.info(f"Pylint output saved to {output_path}")

    # Log Pylint return code
    logger.info(f"Pylint return code: {result.returncode}")

    # Exit with 0 (success) regardless of Pylint findings
    sys.exit(0)

except subprocess.CalledProcessError as e:
    logger.error(f"Failed to run Pylint: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    sys.exit(1)
