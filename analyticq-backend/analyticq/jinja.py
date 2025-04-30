import json
from datetime import datetime
from pathlib import Path
from typing import Dict

from analyticq.manager.jinja_manager import JinjaManager
from fastapi import FastAPI


def common_filters() -> Dict[str, callable]:
    """Get common Jinja2 filters to register."""
    return {
        "format_datetime": lambda dt, fmt="%Y-%m-%d %H:%M:%S": dt.strftime(fmt) if dt else "",
        "to_json": lambda obj: json.dumps(obj, default=str, indent=2),
        "pluralize": lambda count, singular, plural=None: singular if count == 1 else (plural or f"{singular}s"),
        "severity_class": lambda severity: severity.lower() if hasattr(severity, "lower") else "unknown"
    }


def setup_jinja(app: FastAPI):
    """Sets up Jinja2 template engine for the FastAPI application.
    This function initializes the Jinja2 template engine with custom filters and global variables
    for use throughout the application.
    Args:
        app (FastAPI): The FastAPI application instance to set up Jinja2 for.
    Note:
        The function configures the following:
        - Common template filters
        - Global variables including app name, current year and version
        - Template directory path
    Example:
        ```
        app = FastAPI()
        setup_jinja(app)
        ```
    """

    filters = common_filters()

    globals = {
        "app_name": "AnalyticQ",
        "current_year": datetime.now().year,
        "version": "1.0.0"
    }

    JinjaManager.initialize(
        app=app,
        template_dir=Path(__file__).parent / "templates",
        filters=filters,
        globals=globals,
    )

    return app
