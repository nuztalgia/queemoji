import re
import sys
from argparse import ArgumentParser
from importlib import import_module
from pathlib import Path
from typing import Any, Final, IO, cast

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from queemoji_scripts import get_script_name


class RootParser(ArgumentParser):
    """An `ArgumentParser` for organizing and printing all of the program's commands."""

    def __init__(self, pkg: str, *header_lines: tuple[str, str], **kwargs: Any) -> None:
        """Initializes a new `RootParser` instance.

        Args:
            pkg:
                The name of this package (i.e. `queemoji-scripts`, unless it changes).
            *header_lines:
                Lines of text to display at the top of the `--help` menu for the primary
                entry point. Each argument should be a tuple of two strings. The first
                string should contain the plain text content, and the second string
                should correspond to the `rich` style to be applied to the first string.
            **kwargs:
                Keyword arguments to be forwarded to the `ArgumentParser` constructor.
        """
        version = kwargs.pop("version") or "?.?.?"
        super().__init__(**kwargs)

        self.subparsers: Final[Any] = self.add_subparsers(parser_class=ArgumentParser)
        self.command_info: Final[list[tuple[str, str]]] = []
        self.header: Final[list[Text]] = [Text(*args) for args in header_lines[:-1]]

        last_line, last_color = header_lines[-1]
        match = cast(re.Match, re.search(r"^([ |_]+\|)( +)(\|[_| ]+)$", last_line))
        prefix, subtitle_space, postfix = match.groups()
        subtitle = f"{pkg} {version}".center(len(subtitle_space))

        last_line_text = Text.assemble(
            (prefix, last_color), (subtitle, "bright_black"), (postfix, last_color)
        )
        self.header.append(last_line_text)

    def add_command(self, module_path: Path) -> None:
        """Adds a command to this parser, making it usable through `queemoji <name>`.

        Args:
            module_path:
                The path to the module in which the command/script is defined.
                The module must contain a function named `main` that accepts a list of
                strings (the remaining command-line arguments) and returns an integer
                representing an exit code (e.g. 0 to indicate success, or 1 otherwise).
        """
        name = get_script_name(module_path)
        module = import_module(f"{__package__}.{module_path.stem}")
        main_function = getattr(module, "main")
        description = (getattr(main_function, "__doc__") or "").split("\n")[0].strip()

        subparser = self.subparsers.add_parser(name, help=description, add_help=False)
        subparser.set_defaults(callback=main_function)
        self.command_info.append((name, description))

    def print_help(self, file: IO[str] | None = None) -> None:
        """Outputs a message containing information about the program and its commands.

        Args:
            file:
                A writeable object to which the help message will be sent.
                If omitted, `sys.stdout` is assumed.
        """
        console = Console(file=file or sys.stdout)
        total_width = min(console.width, 68)
        header_width = total_width - 4
        help_elements = []

        for line in self.header[:-1]:
            line.align("center", header_width)
            help_elements.append(line)

        left_padding = cast(re.Match, re.match(r" +", help_elements[-1].plain))[0]
        help_elements.append(Text(left_padding).append_text(self.header[-1]))

        if self.description:
            help_elements.append(Text(f"\n{self.description}", justify="center"))

        table = Table(title=" ", box=None, expand=True, header_style="bright_magenta")
        help_elements.append(table)

        table.add_column("Command", style="bright_cyan")
        table.add_column("Description")

        for command, description in self.command_info:
            table.add_row(command, description)

        console.print(Panel(Group(*help_elements), width=total_width))
