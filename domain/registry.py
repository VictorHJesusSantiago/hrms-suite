import importlib
import pkgutil
from pathlib import Path

from config import MODULE_LABELS


def resource_catalog() -> list[dict]:
    root = Path(__file__).parents[1] / "modules"
    resources = []
    for module_name in MODULE_LABELS:
        package = root / module_name
        if not package.exists():
            continue
        files = sorted(path.stem for path in package.glob("*.py") if path.stem != "__init__")
        resources.append({"key": module_name, "label": MODULE_LABELS[module_name], "resources": files, "count": len(files)})
    return resources


def load_resource(module_name: str, resource_name: str):
    return importlib.import_module(f"modules.{module_name}.{resource_name}")
