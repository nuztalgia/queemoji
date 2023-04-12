"""The main package for `queemoji-scripts` (https://github.com/nuztalgia/queemoji)."""
import os
import re


def get_script_name(module_file: str | os.PathLike) -> str:
    """Returns the user-friendly name of the script defined in the given module file."""
    if module_match := re.search(r"\W([a-z_]+)\.py$", str(module_file)):
        return module_match[1].replace("_", "-")
    else:
        raise ValueError(f"Invalid module file: '{module_file}'")


__all__ = [
    "get_script_name",
]
