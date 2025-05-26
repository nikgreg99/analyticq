import threading
from functools import lru_cache
from typing import Dict, List, Set, Type

from .sast_tool import AnalyticQSASTTool


class AnalyticQSASToolRegistry:

    _registered_tool_classes: Dict[str, Type['AnalyticQSASTTool']] = {}
    _tools_by_language: Dict[str, List[str]] = {}
    _lock = threading.Lock()

    @classmethod
    def register_tool(cls, tool_name: str, tool_class) -> None:
        """
        Register a new tool in the tool registry.
        This class method adds a new tool to the registry and updates the language mappings
        for supported languages of the tool.
        Args:
            tool_name (str): The unique identifier name for the tool
            tool_class: The class of the tool to be registered
        Returns:
            None
        Note:
            The tool_class must have a 'supported_languages' attribute defining which
            programming languages the tool supports.
        """
        if not issubclass(tool_class, AnalyticQSASTTool):
            raise ValueError(f"Tool class {tool_class.__name__} must be a subclass of AnalyticQSASTTool")

        if not hasattr(tool_class, 'supported_languages') or not tool_class.supported_languages:
            raise ValueError(f"Tool {tool_name} must define non-empty 'supported_languages'")

        with cls._lock:
            if tool_name in cls._registered_tool_classes:
                raise ValueError(f"Tool {tool_name} is already registered")

            cls._registered_tool_classes[tool_name] = tool_class

            # Update language mappings based on the tool's supported languages
            for language in tool_class.supported_languages:
                if language not in cls._tools_by_language:
                    cls._tools_by_language[language] = []
                if tool_name not in cls._tools_by_language[language]:
                    cls._tools_by_language[language].append(tool_name)

    @classmethod
    def unregister_tool(cls, tool_name: str) -> bool:
        """
        Unregisters a tool from the registry.

        This method removes a tool from both the registered tool classes and language mappings.
        It also clears the tool instance cache.

        Args:
            tool_name (str): The name of the tool to unregister.

        Returns:
            bool: True if the tool was successfully unregistered, False if the tool was not found in registry.

        Thread Safety:
            This method is thread-safe as it uses a lock for synchronization.

        Example:
            >>> ToolRegistry.unregister_tool("my_tool")
            True
        """
        with cls._lock:
            if tool_name not in cls._registered_tool_classes:
                return False

            # Remove the tool from tool classes
            tool_class = cls._registered_tool_classes.pop(tool_name)

            # Remove the tool from language mappings
            for language in tool_class.supported_languages:
                if language in cls._tools_by_language and tool_name in cls._tools_by_language[language]:
                    cls._tools_by_language[language].remove(tool_name)
                    # Clean up empty language entries
                    if not cls._tools_by_language[language]:
                        del cls._tools_by_language[language]

            cls.get_tool_instance.cache_clear()

            return True

    @classmethod
    def get_tools_for_language(cls, language: str) -> List[str]:
        """
        Get a list of tool names that support a specific programming language.

        Args:
            language (str): The programming language to get tools for

        Returns:
            List[str]: A list of tool names that support the specified language.
                      Returns an empty list if no tools are registered for that language.
        """
        with cls._lock:
            return cls._tools_by_language.get(language, [])

    @classmethod
    def get_all_tools_info(cls) -> Dict[str, Set[str]]:
        """
        Returns a dictionary containing all registered tools and their supported languages.

        This class method retrieves information about all tools that have been registered in the tool registry.
        Each tool's name is mapped to a set of programming languages that the tool supports.

        Returns:
            Dict[str, Set[str]]: A dictionary where:
                - keys are tool names (str)
                - values are sets of supported programming languages (Set[str])
        """
        with cls._lock:
            tools_info = {}
            for tool_name, tool_class in cls._registered_tool_classes.items():
                tools_info[tool_name] = tool_class.supported_languages
            return tools_info

    @classmethod
    def get_supported_languages(cls) -> Set[str]:
        """
        Returns a set of supported programming languages.

        This class method retrieves all programming languages that have registered tools
        in the tool registry.

        Returns:
            Set[str]: A set containing the names of all supported programming languages.
        """
        with cls._lock:
            return set(cls._tools_by_language.keys())

    @classmethod
    def is_tool_registered(cls, tool_name: str) -> bool:
        """
        Check if a tool is registered in the tool registry.

        Args:
            tool_name (str): The name of the tool to check

        Returns:
            bool: True if the tool is registered, False otherwise

        Thread Safety:
            This method is thread-safe as it uses a lock for synchronization
        """
        with cls._lock:
            return tool_name in cls._registered_tool_classes

    @classmethod
    @lru_cache(maxsize=256, typed=True)
    def get_tool_instance(cls, tool_name: str):
        """
        Gets an instance of a tool by its name.
        This class method retrieves and instantiates a tool class based on the provided tool name.
        If the tool is not registered, it raises a ValueError.
        Args:
            tool_name (str): The name of the tool to instantiate.
        Returns:
            object: An instance of the requested tool class.
        Raises:
            ValueError: If the tool_name is not found in the registry.
        Example:
            tool = ToolRegistry.get_tool_instance("my_tool")
        """
        with cls._lock:
            if tool_name not in cls._registered_tool_classes:
                raise ValueError(f"Unknown tool: {tool_name}")

            tool_class = cls._registered_tool_classes[tool_name]

            return tool_class()

    @classmethod
    def reset_registry(cls) -> None:
        """
        Reset all registered tools and clear associated caches.

        The operation is thread-safe as it uses a lock during execution.

        Returns:
            None
        """
        with cls._lock:
            cls._registered_tool_classes.clear()
            cls._tools_by_language.clear()
            cls.get_tool_instance.cache_clear()
