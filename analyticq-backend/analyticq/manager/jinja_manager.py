import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from fastapi import FastAPI
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape

logger = logging.getLogger(__name__)


class JinjaManager:
    """
    A singleton class that manages Jinja2 templating functionality for FastAPI applications.

    This manager provides template rendering capabilities, template access, and environment configuration
    for Jinja2 templates. It follows the singleton pattern to ensure only one instance exists.

    Attributes:
        _instance (Optional[JinjaManager]): Singleton instance of the class
        _env (Optional[Environment]): Jinja2 Environment instance

        ```python
        # Initialize the manager with a FastAPI app
        app = FastAPI()
        jinja_manager = JinjaManager.initialize(app)

        # Render a template
        html = jinja_manager.render_template('index.html', title='Home')

        # Render from string
        result = jinja_manager.render_string('Hello {{ name }}!', name='World')
        ```
    """
    _instance = None
    _env: Optional[Environment] = None
    _initizalied = False

    def __new__(cls):
        """Implement singleton pattern for the template service."""
        if cls._instance is None:
            cls._instance = super(JinjaManager, cls).__new__(cls)
            cls._instance._env = None
            cls._instance._initizalied = False
        return cls._instance

    def __init__(self):
        if self._initizalied:
            return
        self._env = None
        self._initizalied = True

    @classmethod
    def initialize(
        cls,
        app: FastAPI,
        template_dir: Optional[str] = None,
        filters: Optional[Dict[str, Callable]] = None,
        globals: Optional[Dict[str, Any]] = None,
        **env_options
    ) -> 'JinjaManager':
        """
        Initialize the Jinja2 environment and attach it to the FastAPI app.

        Args:
            app: The FastAPI application instance
            template_dir: Path to templates directory (default: "templates" in app directory)
            filters: Custom Jinja2 filters to register
            globals: Global variables to add to the Jinja2 environment
        """
        instance = cls()

        if template_dir is None:
            # Default to a "templates" directory in the same directory as this file
            template_dir = Path(__file__).parent.parent / "templates"

        # Create template directory if it doesn't exist
        Path(template_dir).mkdir(parents=True, exist_ok=True)

        logger.info(f"Initializing Jinja2 environment with templates from: {template_dir}")

        # Create Jinja2 environment
        instance._env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True,
            **env_options
        )

        # Register custom filters if provided
        if filters:
            for name, func in filters.items():
                instance._env.filters[name] = func
                logger.debug(f"Registered Jinja2 filter: {name}")

        # Add global variables if provided
        if globals:
            for name, value in globals.items():
                instance._env.globals[name] = value
                logger.debug(f"Added Jinja2 global: {name}")

        # Store the template service in the FastAPI app state
        app.state.template_service = instance

        return instance

    @property
    def env(self) -> Environment:
        """
        Property that provides access to the Jinja2 Environment instance.

        Returns:
            Environment: The initialized Jinja2 Environment object used for template rendering.

        Raises:
            RuntimeError: If the template service has not been initialized by calling initialize() first.
        """
        if self._env is None:
            raise RuntimeError("Template service not initialized. Call initialize() first.")
        return self._env

    @classmethod
    def get_from_app(cls, app: FastAPI) -> 'JinjaManager':
        if not hasattr(app.state, 'template_service'):
            raise RuntimeError('JinjaManager not intizialed for this FastAPI app')
        return app.state.template_service

    @lru_cache(maxsize=32)
    def get_template(self, template_name: str) -> Template:
        """
        Retrieve a Jinja2 template by its name.

        Args:
            template_name (str): The name of the template file to retrieve.

        Returns:
            Template: The loaded Jinja2 template object.

        Raises:
            jinja2.exceptions.TemplateNotFound: If the template with the given name cannot be found.
        """
        return self.env.get_template(template_name)

    def render_template(self, template_name: str, **context) -> str:
        """
        Renders a template with the given context.

        This method takes a template name and context variables, then returns the rendered template as a string.

        Args:
            template_name (str): The name or path of the template file to render
            **context: Variable length keyword arguments that provide the context for template rendering

        Returns:
            str: The rendered template as a string

        Raises:
            jinja2.exceptions.TemplateNotFound: If the template file cannot be found
            jinja2.exceptions.TemplateError: If there are errors during template rendering

        Example:
            rendered = render_template('example.html', title='My Page', content='Hello World')
        """
        logger.debug(f"Rendering template: {template_name} with context keys: {list(context.keys())}")
        template = self.get_template(template_name)
        return template.render(**context)

    def render_string(self, temeplate_string: str, **context) -> str:
        """
        Renders a template from a string with the provided context.

        Args:
            temeplate_string (str): The template string to be rendered.
            **context: Variable length keyword arguments representing the context variables
                to be used in template rendering.

        Returns:
            str: The rendered template string with the context applied.

        Example:
            >>> jinja_manager = JinjaManager()
            >>> template = "Hello {{ name }}!"
            >>> context = {"name": "World"}
            >>> jinja_manager.render_string(template, **context)
            'Hello World!'
        """
        template = self.env.from_string(temeplate_string)
        return template.render(**context)

    def list_templates(self) -> list:
        """
        Lists all available templates in the Jinja2 environment.

        Returns:
            list: A list of template names available in the configured environment.
        """
        return self.env.list_templates()
