class DockerNotFoundException(Exception):
    """Exception raised when Docker is not found on the system.

    This exception is thrown when the system cannot detect a running Docker daemon
    or when Docker is not properly installed on the machine.

    Raises:
        DockerNotFoundException: When Docker is not available or accessible.
    """
    pass
