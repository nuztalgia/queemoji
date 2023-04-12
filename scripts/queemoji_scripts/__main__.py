from importlib.metadata import metadata
from pathlib import Path
from typing import Final

from queemoji_scripts._root_parser import RootParser

_HEADER_LINES: Final[tuple[tuple[str, str], ...]] = (
    ("                                        __ __ ", "bright_magenta"),
    (".-----.--.--.-----.-----.--------.-----|__|__|", "bright_magenta"),
    ("|  _  |  |  |  -__|  -__|  .  .  |  _  |  |  |", "bright_yellow"),
    ("|__   |_____|_____|_____|__|__|__|_____|  |__|", "bright_cyan"),
    ("   |__|                              |____|   ", "bright_cyan"),
)
_PACKAGE_NAME: Final[str] = "queemoji-scripts"


def main() -> int:
    """Primary entry point. Parses args and calls the appropriate script/callback."""
    get_metadata = metadata(_PACKAGE_NAME).json.get
    parser = RootParser(
        _PACKAGE_NAME,
        *_HEADER_LINES,
        version=get_metadata("version"),
        description=get_metadata("summary"),
    )
    parser.set_defaults(callback=parser.print_help)

    for module_path in Path(__file__).parent.glob("*.py"):
        if not module_path.stem.startswith("_"):
            parser.add_command(module_path)

    expected_args, extra_args = parser.parse_known_args()
    return expected_args.callback(extra_args) or 0


if __name__ == "__main__":
    raise SystemExit(main())
