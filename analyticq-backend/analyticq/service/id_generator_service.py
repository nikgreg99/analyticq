import hashlib
from datetime import datetime
from threading import Lock

from analyticq.engine import AnalyticQScanContext


class AnalyticQIDGeneratorService:

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, prefix: str = "S"):
        if not hasattr(self, "initialized"):
            self.prefix = prefix
            self.initizialed = True

    def generate_scan_id(self, scan_context: AnalyticQScanContext):
        """
        Generate a unique scan ID based on the provided scan context.
        The ID is constructed by combining:
        - A prefix
        - Repository name (cleaned and lowercase)
        - Short commit hash (first 7 characters)
        - Current timestamp
        Args:
            scan_context (AnalyticQScanContext): Context object containing repository and commit information
        Returns:
            str: A unique scan ID in the format "{prefix}-{repo_name}-{commit_hash}-{timestamp}"
        Example:
            >>> generate_scan_id(scan_context)
            'scan-myrepo-a1b2c3d-20240215123456'
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        commit_short = scan_context.last_commit_hash[:7]
        repo_clean = scan_context.repo_name.replace('-', '').lower()

        return f"{self.prefix}-{repo_clean}-{commit_short}-{timestamp}"

    def generate_issue_id(self, scan_id, issue_content: str) -> str:
        """
        Generates a unique issue ID by combining a scan ID with a hash of the issue content.

        Args:
            scan_id: The ID of the scan associated with the findinf
            issue_content (str): The content of the issue to be hashed

        Returns:
            str: A unique finding ID in the format "scan_id-issue_hash" where issue_hash
                 is an 8-character hexadecimal hash of the issue content

        Example:
            >>> generate_issue_id("scan123", "Critical security vulnerability found")
            'scan123-a1b2c3d4'
        """
        issue_hash = hashlib.sha256(issue_content.encode()).hexdigest()[:8]
        return f"{scan_id}-{issue_hash}"

    def parse_scan_id(self, scan_id: str) -> dict:
        """
        Parse a scan ID string and extract its components.
        The scan ID format should be: prefix-repo-commit_short-timestamp-suffix
        Example: 'an-myrepo-a1b2c3d-20240215123456-suffix'
        Args:
            scan_id (str): The scan ID string to parse.
        Returns:
            dict: A dictionary containing the parsed components:
                - prefix (str): The identifier prefix
                - repo (str): The repository name
                - commit_short (str): The short commit hash
                - timestamp (datetime): The timestamp as a datetime object
        Raises:
            ValueError: If the scan ID format is invalid or cannot be parsed
        """
        try:
            id_parts = scan_id.split("-")
            if len(id_parts) != 4:
                raise ValueError("Invalid scan ID format")

            return {
                "prefix": id_parts[0],
                "repo": id_parts[1],
                "commit_short": id_parts[2],
                "timestamp": datetime.strptime(id_parts[3], "%Y%m%d%H%M%S")
            }

        except Exception as e:
            raise ValueError(f"Invalid scan ID format: {str(e)}")
