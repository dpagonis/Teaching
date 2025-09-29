import importlib
import sys
from pathlib import Path

def reload():
    """
    Dynamically finds and reloads all Python modules in this package.

    This function is designed for interactive development. When you call it,
    it scans the directory it lives in, identifies all other .py files
    (excluding __init__.py and itself), and reloads them.

    This means you can edit any module in the package, call this function,
    and immediately see your changes in your live Python session.
    """
    # Get the path of the current file (reload.py)
    current_file = Path(__file__)
    # Get the parent directory (the 'my_package' directory)
    package_dir = current_file.parent
    # Get the package name from the directory name
    package_name = package_dir.name

    print(f"--- Reloading modules in package: '{package_name}' ---")

    # Iterate over all files in the same directory as this script
    for module_path in package_dir.glob("*.py"):
        module_name = module_path.stem

        # Skip the __init__ file and the reload module itself
        if module_name == "__init__" or module_path == current_file:
            continue

        # Construct the full module import path (e.g., "my_package.core")
        full_module_name = f"{package_name}.{module_name}"

        # We only want to reload modules that have already been imported
        if full_module_name in sys.modules:
            try:
                # Get the module object from the cache of imported modules
                module_to_reload = sys.modules[full_module_name]
                # Reload it!
                importlib.reload(module_to_reload)
                print(f"  ✅ Reloaded: {module_name}")
            except Exception as e:
                print(f"  ❌ Failed to reload {module_name}: {e}")

    print("--- Reload complete ---")
