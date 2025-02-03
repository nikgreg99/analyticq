import importlib
import pkgutil


class ImportUtil:

    @staticmethod
    def discover_modules(package):
        modules = []
        for _, modname, ispkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            modules.append(modname)
            if ispkg:  # If it's a subpackage, import it and continue searching
                subpackage = importlib.import_module(modname)
                modules.extend(ImportUtil.discover_modules(subpackage))
        return modules
