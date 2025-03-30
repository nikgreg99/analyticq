from typing import Dict

from pydantic import BaseModel


class FileInfoResponse(BaseModel):
    file_path: str
    loc: int
    size: int


class LanguageStatsResponse(BaseModel):
    file_count: int
    total_size: int
    largest_file: Dict[str, str | int]
    smallest_file: Dict[str, str | int]
    average_size: float
    median_size: float
    std_size: float
    percentage_files: float
