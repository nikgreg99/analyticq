import argparse
import logging
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Argument parser
parser = argparse.ArgumentParser(description="Run Bandit SAST tool.")
parser.add_argument(
    "target_dir",
    type=str,
    help="The root directory of the Python codebase to scan."
)
args = parser.parse_args()

# Validate target directory
target_dir = Path(args.target_dir)
if not target_dir.exists():
    logger.error(f"Target directory does not exist: {target_dir}")
    sys.exit(1)

code_path = Path("/code")

if not code_path.exists() or not any(code_path.iterdir()):
    logger.error("Directory /code is empty or not mounted correctly.")
    sys.exit(1)
else:
    logger.info(f"Files in /code: {list(code_path.iterdir())}")


# Bandit command and parameters
bandit_command = [
    "bandit",
    "-r", str(target_dir),  # Recursive scan of the target directory
    "-f", "json",           # Output format
    "-o", "/output/bandit-report.json",  # Output file
]

# Add config file if it exists
config_path = Path("bandit.yaml")
if config_path.exists():
    bandit_command.extend(["-c", str(config_path)])

logger.info(f"Running command: {' '.join(bandit_command)}")
# Run Bandit on container docker
logger.info(f"Running Bandit on {target_dir}...")
result = subprocess.run(
    bandit_command,
    text=True,
    capture_output=True
)
if result.returncode > 1:
    logger.info(f"True Bandit Error: {result.stderr}")
    sys.exit(1)
else:
    logger.info("Bandit completed successfully. Output saved to /output/bandit-report.json")
    sys.exit(0)
