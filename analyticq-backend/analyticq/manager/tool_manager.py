import asyncio
import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from analyticq.engine.core import AnalyticQSASToolRegistry
from analyticq.preprocessing import CodebasePreprocessor
from analyticq.repository.context_repository import AnalyticQContextRepository
from analyticq.repository.scan_repository import (
    AnalyticQSASTScanResultModel, AnalyticQScanResultRepository)
from analyticq.service import AnalyticQContextService, AnalyticQScanService

logger = logging.getLogger(__name__)


COMMON_MAPPINGS = {
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


class AnalyticQSASTManager:
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
            repo_name = original_path or path.name
            context = await self.context_service.get_context_by_repo_name(repo_name)
            scan.context_id = context.id
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

        codebase_data = await self.codebase_preprocesseor.preprocess_codebase(
            codebase_url=codebase_path,
            branch=branch,
            original_path=original_path
        )

        language_to_root_folders = self.identify_root_folders(codebase_data)
        supported_languages = self.registry.get_supported_languages()
        scan_results = {}

        for language, root_folders in language_to_root_folders.items():
            tool_language = self.map_lang_to_supported(language, supported_languages)
            if not tool_language:
                logger.info(f"No supported language mapping found for: {language}")
                continue

            tools_for_language = self.registry.get_tools_for_language(tool_language)
            if not tools_for_language:
                logger.info(f"No tools found for language {language}")
                continue

            language_stats = codebase_data.get("language_statistics", {}).get(language, {})
            files_for_lang = codebase_data["files"].get(language, [])

            results = await asyncio.gather(*[
                self.run_tools_concurrently(
                    tool_name=tool_name,
                    root_folders=root_folders,
                    codebase_path=codebase_path,
                    timeout=timeout,
                    config_paths=config_paths,
                    original_path=original_path
                )
                for tool_name in tools_for_language
            ])

            tool_results = {tool_name: res for tool_name, res in results}

            scan_results[language] = {
                "tools_run": tools_for_language,
                "root_folders": root_folders,
                "file_count": len(files_for_lang),
                "statistics": language_stats,
                "results": tool_results,
            }

        return scan_results

    async def run_tools_concurrently(
        self,
        tool_name: str,
        root_folders: List[str],
        codebase_path: str,
        timeout: Optional[int],
        config_paths: Optional[Dict[str, str]],
        original_path: Optional[str]
    ) -> Tuple[str, Dict[str, Any]]:
        try:
            tool = self.registry.get_tool_instance(tool_name)
            await tool.install()

            config_path = config_paths.get(tool_name) if config_paths else None

            async def scan_folder(folder: str):
                result = await tool.run_scan(codebase_path=folder, timeout=timeout, config_path=config_path)
                await self.save_scan_for_codebase(Path(codebase_path), result, original_path)
                return folder, result

            folder_results = dict(await asyncio.gather(*[
                scan_folder(folder) for folder in root_folders
            ]))

            return tool_name, {
                "folders_scanned": list(folder_results.keys()),
                "results": folder_results
            }

        except Exception as e:
            logger.error(f"Error running {tool_name}: {str(e)}")
            return tool_name, {"error": str(e)}

    def identify_root_folders(self, file_data: Dict[str, Any]) -> Dict[str, List[str]]:
        language_to_folders: Dict[str, Set[str]] = defaultdict(set)

        for language, files in file_data.get("files", {}).items():
            for file_info in files:
                folder = os.path.dirname(file_info["file_path"])
                language_to_folders[language].add(folder)

        language_to_root_folders : Dict[str, List[str]] = {}

        # Compute common root folder for each language
        for language, folders in language_to_folders.items():
            if not folders:
                language_to_root_folders[language] = []
                continue

            common_parent = os.path.commonpath(folders) if folders else ""
            language_to_root_folders[language] = [common_parent] if common_parent else list(folders)

        return language_to_root_folders

    def map_lang_to_supported(self, json_lang: str, supported_languages: Set[str]) -> Optional[str]:

        mapped = COMMON_MAPPINGS.get(json_lang)
        if mapped and mapped in supported_languages:
            return mapped

        lower_lang = json_lang.lower()
        if lower_lang in supported_languages:
            return lower_lang

        cleaned = "".join(c.lower() for c in json_lang if c.isalnum())
        if cleaned in supported_languages:
            return cleaned

        return None
