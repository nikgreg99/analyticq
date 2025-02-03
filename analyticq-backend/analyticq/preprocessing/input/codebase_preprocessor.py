from threading import Lock
from typing import Dict

from .codebase_cloner import CodebaseCloner
from .codebase_lang_scanner import CodebaseLangScanner


class CodebasePreprocessor:

    instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                _instance = super().__new__(cls)
        return _instance

    def __init__(self):
        self.cloner = CodebaseCloner()
        self.language_scanner = CodebaseLangScanner()

    async def preprocess_codebase(self, codebase_url: str, branch: str = None, tag: str = None, ssh_key_path: str = None) -> Dict:
        codebase_info = {
            "branch": branch,
            "tag": tag,
            "ssh_key_path": ssh_key_path
        }
        repo_path = await self.cloner.clone(codebase_url, codebase_info)
        self.language_scanner.scan_codebase_languages(repo_path)
        return self.language_scanner.generate_languge_report()
