import importlib
import logging
import pkgutil

from .tool_registry import AnalyticQSASToolRegistry

logger = logging.getLogger(__name__)


class AnalyticQToolDiscoverer:

    @staticmethod
    def discover_and_register_tools():
        """
        Discovers and registers all tools in the analyticq.engine.tools package and its submodules.
        This function dynamically imports all modules and submodules under the base package path,
        registering any tools that are defined within them. Tools are expected to be classes
        that are registered with the AnalyticQSASToolRegistry.
        Returns:
            list[str]: A list of fully qualified module names that were successfully imported
        Example:
            >>> imported_tools = discover_and_register_tools()
            >>> print(f"Imported {len(imported_tools)} tool modules")
        Notes:
            - Tools must be properly decorated/registered to be detected
            - Failed imports are logged as warnings but don't stop the discovery process
            - Registered tools and their supported languages are logged at INFO level
        """

        base_package = "analyticq.engine.tools"

        importlib.import_module(base_package)

        imported_tools = []

        def import_submodules(package_name: str):
            """
            Recursively imports all submodules of a given package.
            This function traverses through all submodules and packages within the specified package
            and attempts to import them. Successfully imported modules are added to the imported_tools list.
            Args:
                package_name (str): The name of the package to import submodules from.
            Raises:
                ImportError: If a module cannot be imported. The error is logged as a warning.
            Note:
                The function uses the global 'imported_tools' list to track successfully imported modules.
                Failed imports are logged as warnings but do not stop the recursive import process.
            Example:
                import_submodules('my_package')
                # This will import all submodules under my_package and its subdirectories
            """
            package = importlib.import_module(package_name)

            if hasattr(package, "__path__"):
                for _, name, is_pkg in pkgutil.iter_modules(package.__path__):
                    full_name = f"{package_name}.{name}"
                    try:
                        module = importlib.import_module(full_name)
                        imported_tools.append(full_name)
                        if hasattr(module, f"{name.capitalize()}Tool"):
                            tool_class = getattr(module, f"{name.capitalize()}Tool")
                            if isinstance(tool_class, type):
                                AnalyticQSASToolRegistry.register_tool(name, tool_class)
                                logger.info(f"Registered tool: {name}")

                        if is_pkg:
                            import_submodules(full_name)
                    except ImportError as e:
                        logger.warning(f"Failed to import {full_name}: {e}")

        import_submodules(base_package)
        logger.info(f"Registered {len(AnalyticQSASToolRegistry._registered_tool_classes)} tool")

        for tool_name in AnalyticQSASToolRegistry._registered_tool_classes:
            tool_class = AnalyticQSASToolRegistry._registered_tool_classes[tool_name]
            languages = ", ".join(tool_class.supported_languages)
            logger.info(f"{tool_name}: supports {languages}")

        return imported_tools
