from typing import Dict, List, Optional

from pydantic import BaseModel, field_validator


class AnalyticQFileInfoModel(BaseModel):
    """
    A Pydantic model representing file information for AnalyticQ.


    Attributes:
        file_path (str): The full path to the file
        loc (int): Lines of code in the file
        size (int): Size of the file in bytes

    Config:
        from_attributes (bool): Enables ORM mode allowing model to be created from attributes
    """
    file_path: str
    loc: int
    size: int

    class Config:
        from_attributes = True


class AnalyticQCodebaseLanguageStatistics(BaseModel):
    """A data model representing statistical information about a specific programming language in a codebase.

    This model captures various metrics and statistics about files written in a particular programming language,
    including counts, sizes, and statistical measures.

    Attributes:
        file_count (int): The total number of files in this language.
        total_size (int): The total size of all files in bytes.
        largest_file (Dict[str, str | int]): Information about the largest file, containing filename and size.
        smallest_file (Dict[str, str | int]): Information about the smallest file, containing filename and size.
        average_size (float): The mean file size in bytes, rounded to 2 decimal places.
        median_size (float): The median file size in bytes, rounded to 2 decimal places.
        std_size (float): The standard deviation of file sizes in bytes, rounded to 2 decimal places.
        percentage_files (float): The percentage of files in this language relative to all files, rounded to 2 decimal places.

    Note:
        All float values (average_size, median_size, std_size, percentage_files) are automatically rounded
        to 2 decimal places during validation.
    """
    file_count: int
    total_size: int
    largest_file: Dict[str, str | int]
    smallest_file: Dict[str, str | int]
    average_size: float
    median_size: float
    std_size: float
    percentage_files: float

    class Config:
        from_attributes = True

    @field_validator("average_size", "median_size", "std_size", "percentage_files", mode="before")
    def round_float(cls, value):
        return round(value, 2)


class AnalyticQExcludedFilesModel(BaseModel):
    """
    A model representing excluded files during processing.

    This class inherits from BaseModel and provides information about files that were
    excluded during the processing pipeline.

    Attributes:
        count (int): The number of files that were excluded
        total_size (int): The total size in bytes of all excluded files
        files (List[str]): List of file paths that were excluded

    """
    count: int
    total_size: int
    files: List[str]

    class Config:
        from_attributes = True


class AnalyticQStatsModel(BaseModel):
    """
    A model representing preprocessing analysis of a codebase.

    Stores information about analyzed files, language statistics, and exclusion details.

    Attributes:
        files (Dict[str, List[AnalyticQFileInfoModel]]): Dictionary mapping file paths to their metadata
            information.
        language_statistics (Dict[str, AnalyticQCodebaseLanguageStatistics]): Statistics about programming
            languages used in the codebase, keyed by language name.
        total_files_scanned (int): Total number of files analyzed during preprocessing.
        total_size_scanned (int): Total size in bytes of all scanned files.
        excluded_directories (List[str]): List of directory paths that were excluded from analysis.
        excluded_files (AnalyticQExcludedFilesModel): Information about files that were excluded from
            the analysis.
    """
    id: Optional[int] = None
    context_id: Optional[int] = None
    excluded_files_id: Optional[int] = None
    files: Dict[str, List[AnalyticQFileInfoModel]]
    language_statistics: Dict[str, AnalyticQCodebaseLanguageStatistics]
    total_files_scanned: int
    total_size_scanned: int
    excluded_directories: List[str]
    excluded_files: AnalyticQExcludedFilesModel

    class Config:
        from_attributes = True
