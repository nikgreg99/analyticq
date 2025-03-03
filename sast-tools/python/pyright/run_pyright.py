import json
import logging
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Check flake8 version
result = subprocess.run(["pyright", "--version"], capture_output=True, text=True)
logger.info(f"Return code: {result.returncode}")
logger.info(f"pyright version: {result.stdout}")
if result.stderr:
    logger.info(f"stderr: {result.stderr}")

# Define paths
code_path = Path("/code")
output_path = Path("/output/pyright-report.json")

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

logger.info(f"Files to scan: {files_to_scan}")

# Form pyright command - using --outputjson for JSON output
pyright_command = ["pyright", "--outputjson", "--level", "warning"] + files_to_scan

logger.info(f"Running command: {' '.join(pyright_command)}")

try:
    # Run pyright
    logger.info("Running pyright...")
    result = subprocess.run(
        pyright_command,
        capture_output=True,
        text=True,
    )

    # Log pyright output
    logger.info(f"pyright stdout: {result.stdout}")
    if result.stderr:
        logger.error(f"pyright stderr: {result.stderr}")

    # Save output to file
    output_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure output directory exists

    # The output might be an empty string if no issues were found
    if result.stdout.strip():
        # Validate JSON output
        try:
            json.loads(result.stdout)
            output_path.write_text(result.stdout)
            logger.info(f"pyright output saved to {output_path}")
        except json.JSONDecodeError:
            logger.error("pyright output is not valid JSON. Saving raw output.")
            output_path.write_text(result.stdout)
    else:
        # Write empty JSON array if no issues found
        output_path.write_text("[]")
        logger.info(f"No issues found. Empty JSON array saved to {output_path}")

    # Log flake8 return code
    logger.info(f"pyrigth return code: {result.returncode}")

    # Exit with 0 (success) regardless of flake8 findings
    sys.exit(0)

except subprocess.CalledProcessError as e:
    logger.error(f"Failed to run flake8: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    sys.exit(1)
