import importlib
import inspect

# --- Configuration ---
# Add the names of the modules you want to "star import" to this list.
# These are the local module names (the .py file names without extension).
MODULES_TO_IMPORT = [
    "gentools",
    "sigfig",
    "weakacid",
    "stats",
    "reload",
    "uncertainvalue",
]
# ---------------------

def imports():
    """
    Explicitly imports members from a predefined list of modules
    (sigfig, weakacid) into the global namespace of the caller's session.

    This provides a controlled way to reduce typing during interactive
    sessions without the risks of a wide-open dynamic import.

    WARNING: For interactive convenience only. Do not use in production scripts.

    Usage in an interactive terminal:
        >>> import dp_chem
        >>> dp_chem.imports()
        # Functions and classes from sigfig and weakacid are now available.
        >>> calculate_pH()
    """
    # Get the frame of the function that called this one (the interactive session)
    try:
        caller_frame = inspect.stack()[1].frame
        caller_globals = caller_frame.f_globals
    except IndexError:
        print("❌ Error: imports() must be called from another script or an interactive session.")
        return

    package_name = __name__.split('.')[0]
    print(f"--- Importing members from '{package_name}' into global scope ---")

    for module_name in MODULES_TO_IMPORT:
        full_module_name = f"{package_name}.{module_name}"
        
        try:
            # Dynamically import the specific module
            module = importlib.import_module(full_module_name)
            
            # Find all public names in the module (names not starting with '_')
            names_to_import = [name for name in dir(module) if not name.startswith('_')]
            
            print(f"  -> From '{module_name}': importing {len(names_to_import)} members...")

            for name in names_to_import:
                # Check for name collisions before overwriting
                if name in caller_globals and caller_globals[name] is not getattr(module, name):
                    print(f"      ⚠️  Warning: Overwriting existing global name '{name}'")
                
                # Get the actual object (function, class, etc.)
                obj = getattr(module, name)
                # Inject it into the caller's global namespace
                caller_globals[name] = obj

        except ModuleNotFoundError:
            print(f"  ❌ Error: Module '{full_module_name}' not found. Skipping.")
        except Exception as e:
            print(f"  ❌ Failed to import from {module_name}: {e}")

    print("--- Imports complete. Members are now in your session. ---")
