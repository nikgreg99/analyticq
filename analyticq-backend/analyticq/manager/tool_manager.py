import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from analyticq.engine.core import AnalyticQSASToolRegistry
from analyticq.preprocessing import CodebasePreprocessor
from analyticq.repository.context_repository import AnalyticQContextRepository
from analyticq.repository.scan_repository import (
    AnalyticQSASTScanResultModel, AnalyticQScanResultRepository)
from analyticq.service import AnalyticQContextService, AnalyticQScanService

logger = logging.getLogger(__name__)


class AnalyticQSASTManager:
    """
    A manager class for coordinating static analysis security testing (SAST) tools in AnalyticQ.
    This class handles the registration, configuration, and execution of multiple SAST tools
    across different programming languages. It provides functionality to scan codebases using
    specified tools or language-specific tools.
    Attributes:
        registry (AnalyticQSASToolRegistry): Registry containing all available SAST tools.
    Methods:
        scan_codebase: Executes SAST tools on a given codebase based on specified parameters.
    """

    def __init__(self):
        self.registry = AnalyticQSASToolRegistry()
        self.codebase_preprocesseor = CodebasePreprocessor()
        self.context_service = AnalyticQContextService(AnalyticQContextRepository())
        self.scan_service = AnalyticQScanService(AnalyticQScanResultRepository())

    async def save_scan_for_codebase(
            self,
            path: Path,
            scan: AnalyticQSASTScanResultModel,
            original_path: Optional[str] = None
    ) -> None:

        try:
            if original_path is not None:
                repo_name = original_path
            else:
                # Remove any suffixes that are not part of the repository name
                repo_name = path.name

            context = await self.context_service.get_context_by_repo_name(repo_name)
            context_id = context.id
            scan.context_id = context_id
            logger.info(f"Scan saved for context repository: {repo_name}")
            await self.scan_service.create_scan(scan)
        except Exception as e:
            logger.error(f"Failed to save scan for codebase at {path}: {str(e)}")

    async def scan_codebase(
            self,
            codebase_path: str,
            config_paths: Optional[Dict[str, str]] = None,
            timeout: Optional[int] = None,
            branch="main",
            original_path: Optional[str] = None
    ) -> Dict[str, Any]:

        logger.info("Original path: %s", original_path)
        # Preprocess the codebase to gather file and language information
        codebase_data = await self.codebase_preprocesseor.preprocess_codebase(codebase_url=codebase_path, branch=branch, original_path=original_path)

        # Identify root folders for each language
        language_to_root_folders = self.identify_root_folders(codebase_data)

        # Get supported languages from the registry
        supported_languages = self.registry.get_supported_languages()

        # Initialize results dictionary
        scan_results = {}

        for language, root_folders in language_to_root_folders.items():

            # Map the JSON language to a supported language
            tool_language = self.map_lang_to_supported(language, supported_languages)

            if not tool_language:
                logger.info(f"No supported language mapping found for: {language}")
                continue

            # Map the JSON language to a supported language
            tools_for_language = self.registry.get_tools_for_language(tool_language)

            if not tools_for_language:
                logger.info(f"No tools found to language {language}")
                continue

            # Run the tools on the root folders for this language
            language_results = {}
            for tool_name in tools_for_language:
                try:
                    tool = self.registry.get_tool_instance(tool_name)
                    await tool.install()

                    config_paths = config_paths.get(tool_name) if config_paths else None

                    # Run the tool on each root folder
                    folder_results = {}
                    for folder in root_folders:
                        result = await tool.run_scan(
                            codebase_path=folder,
                            timeout=timeout
                        )
                        await self.save_scan_for_codebase(Path(codebase_path), result, original_path=original_path)
                        folder_results[folder] = result

                    language_results[tool_name] = {
                        "folders_scanned": list(folder_results.keys()),
                        "results": folder_results
                    }

                    language_stats = codebase_data.get("language_statistics", {}).get(language, {})

                    scan_results[language] = {
                        "tools_run": list(tools_for_language),
                        "root_folders": root_folders,
                        "file_count": len(codebase_data["files"].get(language, [])),
                        "statistics": language_stats,
                        "results": language_results,
                    }

                except Exception as e:
                    logger.error(f"Error running {tool_name} tool on {language} files: {str(e)}")
                    language_results[tool_name] = {"error": str(e)}
        return scan_results

    def identify_root_folders(self, file_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Identifies the root folders for each programming language in the provided file data.
        This method analyzes file paths grouped by programming language and determines the minimal
        set of root folders that contain all files for each language. It eliminates redundant
        nested folders to find the most efficient folder structure representation.
        Args:
            file_data (List[str]): A dictionary containing files grouped by programming language.
                Expected format: {
                    "files": {
                        "language1": [{"file_path": "path/to/file"}, ...],
                        "language2": [{"file_path": "path/to/file"}, ...],
                    }
                }
        Returns:
            Dict[str, List[str]]: A dictionary mapping programming languages to their respective
            root folders. Format: {
                "language1": ["root/folder1", "root/folder2"],
                "language2": ["root/folder3"]
            }
        Example:
            file_data = {
                "files": {
                    "python": [
                        {"file_path": "src/main/utils.py"},
                        {"file_path": "src/main/helpers.py"}
                    ]
                }
            }
            result = identify_root_folders(file_data)
            # Returns: {"python": ["src/main"]}
        """
        # Step 1: Group file paths by language and track folders
        language_to_folders = defaultdict(set)
        for language, files in file_data["files"].items():
            for file_info in files:
                folder = os.path.dirname(file_info["file_path"])
                language_to_folders[language].add(folder)

        # Step 2: For each language, find the minimal set of root folders
        language_to_root_folders = {}
        for language, folders in language_to_folders.items():
            # Find the common parent folder for all folders of this language
            common_parent = os.path.commonpath(folders) if folders else ""

            # If a common parent exists, use it as the root folder
            if common_parent:
                language_to_root_folders[language] = [common_parent]
            else:
                # If no common parent exists, use the individual folders
                language_to_root_folders[language] = list(folders)

        return language_to_root_folders

    def map_lang_to_supported(self, json_lang: str, supported_languages: Set[str]) -> Optional[str]:
        """Maps a language string from JSON to a supported language format.
        This function attempts to match a given language string to a set of supported languages
        Args:
            json_lang (str): The language string to map from JSON input
            supported_languages (Set[str]): Set of supported language strings to map to
        Returns:
            Optional[str]: The matched supported language if found, None otherwise
        Examples:
            >>> map_lang_to_supported("en-US", {"en", "fr", "de"})
            'en'
            >>> map_lang_to_supported("C++", {"cpp", "python", "java"})
            'cpp'
            >>> map_lang_to_supported("unknown", {"en", "fr", "de"})
            None
        """
        common_mappings = {
            "Python": "python",
            "JavaScript": "js",
            "TypeScript": "typescript",
            "C++": "c++",
            "C": "c",
            "Go": "go",
            "Java": "java",
            "Ruby": "ruby",
            "PHP": "php",
        }

        # Try direct mapping from common mappings
        if json_lang in common_mappings:
            mapped = common_mappings[json_lang]
            if mapped in supported_languages:
                return mapped

        # Try lowercase version
        if json_lang.lower() in supported_languages:
            return json_lang.lower()

        # Try removing spaces and special characters
        cleaned = "".join(c.lower() for c in json_lang if c.isalnum())
        if cleaned in supported_languages:
            return cleaned

        # No mapping language found
        return None
