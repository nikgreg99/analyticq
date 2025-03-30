class CodebaseUnknownTypeException(Exception):
    """
    Exception raised when an unknown codebase type is encountered during preprocessing.

    This exception is raised when the system encounters a codebase type that it cannot
    recognize or process during the preprocessing phase.

    Example:
        >>> if codebase_type not in supported_types:
        ...     raise CodebaseUnknownTypeException()
    """
    pass


class CodebaseNotFoundException(Exception):
    """
    Exception raised when the specified codebase directory is not found.

    This exception is raised when attempting to access or process a codebase directory
    that does not exist or cannot be located in the file system.

    Attributes:
        None

    Example:
        >>> if not os.path.exists(codebase_path):
        ...     raise CodebaseNotFoundException()
    """
    pass


class CloneRemoteRepositoryException(Exception):
    """Exception raised when cloning a remote repository fails.

    This exception is thrown when there are issues during the process of cloning
    a remote Git repository, such as network problems, invalid repository URL,
    authentication failures, or insufficient permissions.
    """
    pass


class CloneLocalRepositoryException(Exception):
    """Exception raised when cloning a local repository fails.

    This exception is thrown when there are issues during the process of
    cloning a local Git repository, such as permission errors, invalid paths,
    or network connectivity problems.
    """
    pass


class CloneLocalScriptException(Exception):
    """Exception raised when cloning a local script fails.

    This exception is raised when there are issues during the process of cloning
    or copying a local script to a target location.
    """
    pass


class CleanupErrorException(Exception):
    """
    Exception raised when cleanup operation fails during data preprocessing.

    This exception is thrown when there is an error or failure during the data cleanup
    phase of preprocessing, such as removing duplicates, handling missing values,
    or other data cleaning operations.

    """
    pass


class ExtractArchiveException(Exception):
    """
    Exception raised when there is an error during archive extraction.

    This exception is used to handle errors that occur during the process of extracting
    files from an archive (e.g., zip, tar, etc.).

    """
    pass
