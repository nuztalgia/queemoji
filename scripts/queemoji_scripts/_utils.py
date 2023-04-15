import logging
import os
import re
from collections.abc import Callable, Iterable
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
        show_path=False,
        markup=True,
        rich_tracebacks=True,
    )
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(message)s",
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


def get_valid_files(
    paths: Iterable[Path],
    *allowed_exts: str,
    warn: Callable[[str], None] = print,
) -> list[Path]:
    """Returns a sorted list of file paths that are valid according to the given params.

    Args:
        paths:
            File and/or directory `Path` objects to be considered for inclusion in the
            resulting list. Directories will be scanned non-recursively for files.
        *allowed_exts:
            Strings representing the file extensions to match (case-insensitive).
            If omitted, **all** file extensions will be considered valid.
        warn:
            A function that accepts a warning string to be logged/printed.
            If omitted, the built-in `print` function will be used.
    """
    valid_files = set()
    source_paths = {path.resolve() for path in paths}
    allowed_suffixes = {f".{ext}".lower() for ext in allowed_exts}

    def populate_valid_files(potential_paths: Iterable[Path]) -> None:
        for path in potential_paths:
            if path in valid_files:
                warn(f"Ignoring duplicate file: {get_display_path(path)}")
            elif not path.exists():
                warn(f"Skipping nonexistent path: {get_display_path(path)}")
            elif path.is_dir():
                # Call this function recursively, but ignore further subdirectories.
                # Files with invalid suffixes are filtered out by the next elif clause.
                populate_valid_files(
                    potential_path
                    for potential_path in path.iterdir()
                    if potential_path.is_file()
                )
            elif (not allowed_suffixes) or (path.suffix.lower() in allowed_suffixes):
                valid_files.add(path)
            elif path in source_paths:
                # Only log a warning if this file was explicitly specified by the user.
                warn(f"Skipping file of invalid type: {get_display_path(path)}")

    populate_valid_files(source_paths)
    return sorted(valid_files)
