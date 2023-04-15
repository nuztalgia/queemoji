import logging
import os
import re
from pathlib import Path

from rich.logging import RichHandler


def get_display_path(path: Path, relative_dir: Path | None = None) -> str:
    """Returns a string representing the given path relative to a specific directory.

    Args:
        path:
            The path to represent as a string.
        relative_dir:
            The path to the directory that will serve as the reference point.
            If omitted, the current working directory will be used.
    """
    relative_dir = relative_dir or Path.cwd()
    return (
        f".{os.path.sep}{path.relative_to(relative_dir)}"
        if path.is_relative_to(relative_dir)
        else str(path)
    )


def get_logger(verbose: bool = False) -> logging.Logger:
    """Returns a pre-configured logger that uses the standard settings for this package.

    Args:
        verbose:
            If set to `True`, will cause the logger to print `logging.DEBUG` messages.
            (By default, it only prints messages with a level of `logging.INFO` and up).
    """
    handler = RichHandler(
        omit_repeated_times=False,
        show_level=False,
        show_path=False,
        markup=True,
        rich_tracebacks=True,
    )
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
        datefmt="[%X]",
        handlers=[handler],
    )
    return logging.getLogger(__package__)


def get_script_name(module_file: str | os.PathLike) -> str:
    """Returns the user-friendly name of the script defined in the given module file.

    Args:
        module_file:
            A string or `PathLike` object representing the script/command module file.
    """
    if module_match := re.search(r"\W([a-z_]+)\.py$", str(module_file)):
        return module_match[1].replace("_", "-")
    else:
        raise ValueError(f"Invalid module file: '{module_file}'")
