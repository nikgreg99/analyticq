import inspect

from analyticq.config.di import AnalyticQContainer


def inject_task_dependecies(func):
    """
    A decorator that injects dependencies into a function using dependency injection container.
    This decorator automatically wires dependencies from the AnalyticQContainer into the decorated
    function's parameters. It inspects the function signature and injects any matching dependencies
    that are available in the container.
    Args:
        func: The function to be decorated
    Returns:
        wrapper: A wrapped function with injected dependencies
    Example:
        @inject_task_dependecies
        def my_task(database_service, logger):
            # database_service and logger will be automatically injected
            # if they are available in the AnalyticQContainer
            pass
    """
    def wrapper(*args, **kwargs):
        container = AnalyticQContainer()
        container.wire(modules=[func.__module__])

        sig = inspect.signature(func)
        for name, param in sig.parameters.items():
            if name not in kwargs:
                if hasattr(container, name):
                    provider = getattr(container, name)
                    kwargs[name] = provider()

        return func(*args, **kwargs)
    return wrapper
