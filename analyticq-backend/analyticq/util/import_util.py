import importlib
import pkgutil


class ImportUtil:

    @staticmethod
    def discover_modules(package):
        """
        Recursively discovers all modules and submodules within a given package.

        Args:
            package: A Python package object to search for modules within.
                    Must be an imported package with a __path__ attribute.

        Returns:
            list: A list of strings containing the fully qualified names of all discovered modules
                  and submodules. Includes both regular modules and packages.

        Example:
            >>> import mypackage
            >>> modules = discover_modules(mypackage)
            >>> print(modules)
            ['mypackage.module1', 'mypackage.subpackage1', 'mypackage.subpackage1.module2']
        """
        modules = []
        for _, modname, ispkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            modules.append(modname)
            if ispkg:  # If it's a subpackage, import it and continue searching
                subpackage = importlib.import_module(modname)
                modules.extend(ImportUtil.discover_modules(subpackage))
        return modules
