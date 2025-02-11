class ScanTimeoutException(Exception):
    """
    Exception raised when a scan operation exceeds its time limit.

    This exception is thrown when a scanning process does not complete within
    the specified timeout period. It helps in handling situations where scans
    might hang or take longer than expected.

    """
    pass


class ScanConfigurationException(Exception):
    """Exception raised when there is an error in scan configuration.

    This exception is thrown when there are issues with the configuration
    settings for scanning operations, such as invalid parameters or
    missing required configuration values.
    """
    pass


class ScanParserException(Exception):
    """
    A custom exception class raised when parsing scan data fails.

    This exception is raised when there are issues parsing or processing scan-related data,
    such as invalid scan formats, missing required fields, or corrupted scan data.

    """
    pass
