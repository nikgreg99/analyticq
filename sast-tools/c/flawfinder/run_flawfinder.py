import logging
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Check Pylint version
result = subprocess.run(["flawfinder", "--version"], capture_output=True, text=True)
logger.info(f"FlawFinder version: {result.stdout}")

# Define paths
code_path = Path("/code")
output_path = Path("/output/flawfinder-report.csv")

# Check if /code directory exists and is not empty
if not code_path.exists() or not any(code_path.iterdir()):
    logger.error("Directory /code is empty or not mounted correctly.")
    sys.exit(1)

# Find all C/C++ source and header files
files_to_scan = [str(f) for f in code_path.rglob("*") if f.suffix in {".c", ".cpp", ".h", ".hpp"}]

# Check if it's a C/C++ project (contains source files or a recognized build system)
is_cpp_project = any(f.name in {"Makefile", "CMakeLists.txt"} for f in code_path.rglob("*")) or bool(files_to_scan)
if not is_cpp_project:
    logger.error("No valid C source found in the directory.")
    sys.exit(1)

logger.info(f"Files to scan : {files_to_scan}")

# Form FlawFinder command
flaw_finder_command = ["flawfinder", "--csv"] + files_to_scan

logger.info(f"Running command: {' '.join(flaw_finder_command)}")

try:
    # Run FlawFinder
    logger.info("Running FlawFinder...")
    result = subprocess.run(
        flaw_finder_command,
        capture_output=True,
        text=True,
    )

    # Log FlawFinder output
    logger.info(f"FlawFinder stdout: {result.stdout}")
    if result.stderr:
        logger.error(f"FlawFinder stderr: {result.stderr}")

    # Save output to file
    output_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure output directory exists
    output_path.write_text(result.stdout)
    logger.info(f"FlawFinder output saved to {output_path}")

    # Log FlaqFinder return code
    logger.info(f"FlawFinder return code: {result.returncode}")

    # Exit with 0 (success) regardless of FlawFinder findings
    sys.exit(0)

except subprocess.CalledProcessError as e:
    logger.error(f"Failed to run FlawFinder.py: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    sys.exit(1)
