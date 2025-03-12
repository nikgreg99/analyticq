import json
import logging
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Check njsscan version
try:
    result = subprocess.run(["njsscan", "--version"], capture_output=True, text=True)
    logger.info(f"njsscan version: {result.stdout.strip()}")
    if result.stderr:
        logger.info(f"Version stderr: {result.stderr.strip()}")
except Exception as e:
    logger.error(f"Failed to get njsscan version: {e}")
    sys.exit(1)

# Define paths
code_path = Path("/code")
output_path = Path("/output/njsscan-report.json")

# Check if /code directory exists and is not empty
if not code_path.exists() or not any(code_path.iterdir()):
    logger.error("Directory /code is empty or not mounted correctly.")
    sys.exit(1)

# Find all JavaScript/Node.js files
js_extensions = ["*.js", "*.jsx", "*.ts", "*.tsx", "*.vue", "*.html", "*.hbs", "*.ejs"]
files_to_scan = []
for ext in js_extensions:
    files_to_scan.extend([str(f) for f in code_path.rglob(ext)])

# Check if any Node.js files are found
is_nodejs_project = bool(files_to_scan) or (code_path / "package.json").exists()

if not is_nodejs_project:
    logger.error("No valid Node.js/JavaScript files found in the directory.")
    sys.exit(1)

logger.info(f"Found {len(files_to_scan)} files to scan")

# Form njsscan command - we'll scan the whole directory instead of individual files
njsscan_command = ["njsscan", "--json", "-o", str(output_path), "--missing-controls", "-w", str(code_path)]

logger.info(f"Running command: {' '.join(njsscan_command)}")

try:
    # Run njsscan
    logger.info("Running njsscan...")
    result = subprocess.run(
        njsscan_command,
        capture_output=True,
        text=True,
    )

    # Log njsscan output
    if result.stderr:
        logger.error(f"njsscan stderr: {result.stderr.strip()}")

    # Save output to file
    output_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure output directory exists
    logger.info(f"njsscan output saved to {output_path}")

    # Log njsscan return code
    logger.info(f"njsscan return code: {result.returncode}")
    # Read and compress JSON output
    try:
        with open(output_path, "r") as f:
            json_output = json.load(f)
            compact_json = json.dumps(json_output, separators=(',', ':'))
            print(compact_json)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse njsscan JSON output: {e}")

    # Exit with 0 (success) regardless of njsscan findings
    sys.exit(0)

except subprocess.CalledProcessError as e:
    logger.error(f"Failed to run njsscan: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    sys.exit(1)
