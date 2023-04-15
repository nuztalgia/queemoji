from __future__ import annotations

import re
import sys
from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from typing import Any, Final, IO, NamedTuple

from rich.console import Console, ConsoleRenderable, Group
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from queemoji_scripts._utils import get_logger, get_script_name

_HELP_SUBTITLE_TEXT: Final[Text] = Text.assemble(
    ("qu", "bright_yellow"),
    ("ee", "bright_white"),
    ("mo", "magenta"),
    ("ji", "bright_black"),
)


class _Option(NamedTuple):
    """A `NamedTuple` containing information about an option for a `SubParser`."""

    abbreviation: str
    full_name: str
    description: str


class SubParser(ArgumentParser):
    """A specialized `ArgumentParser` for individual `queemoji-scripts` subcommands."""

    def __init__(self, module_file: str, **kwargs: Any) -> None:
        """Initializes a new `SubParser` instance.

        Args:
            module_file:
                A string containing the file path for the script/command module.
                Will be parsed to determine the name to display for the command.
            **kwargs:
                Keyword arguments to be forwarded to the `ArgumentParser` constructor.
        """
        super().__init__(prog=get_script_name(module_file), add_help=False, **kwargs)

        # This list is populated by add_option(). '-v' and '-h' are automatically added.
        self.options: Final[list[_Option]] = []

        # These attributes will be set if/when add_positional_arg() is called.
        self.arg_name: str = ""
        self.arg_description: str = ""
        self.arg_metavar: str = ""

    def add_positional_arg(
        self, name: str, description: str, **kwargs: Any
    ) -> SubParser:
        """Defines a positional argument with `nargs="*"` and adds it to the parser.

        This method should only be called a maximum of one time, in order to avoid user
        confusion. If it is called more than once, a `RuntimeError` will be raised.

        Args:
            name:
                A string containing the name of this argument. Must be non-empty.
                If the `metavar` keyword arg is provided, it will be shown instead of
                this name in the command-line `--help` menu.
            description:
                A string containing a description of this argument. Must be non-empty.
            **kwargs:
                Keyword args to be forwarded to the superclass `add_argument()` method.

        Returns:
            This `SubParser` instance, for chaining method calls.
        """
        self._validate_arg(name, description, positional=True)

        self.arg_name = name
        self.arg_description = description
        self.arg_metavar = kwargs.pop("metavar", name).upper()

        self.add_argument(name, help=description, nargs="*", **kwargs)
        return self

    def add_option(self, name: str, description: str, **kwargs: Any) -> SubParser:
        """Defines the behavior of a command-line option and adds it to the parser.

        Note that the `--verbose` and `--help` options are added automatically by
        `parse_args()`, so there's no need to manually add them using this method.

        Args:
            name:
                A string containing the full name of this option, without any prefix
                characters (i.e. 'force', not '--force'). Must be unique and non-empty.
            description:
                A string containing a description of this option. Must be non-empty.
            **kwargs:
                Keyword args to be forwarded to the superclass `add_argument()` method.

        Returns:
            This `SubParser` instance, for chaining method calls.
        """
        self._validate_arg(name, description)

        names = (f"-{name[0]}", f"--{name}")
        self.options.append(_Option(*names, description))

        self.add_argument(*names, help=description, **kwargs)
        return self

    def parse_args(  # type: ignore[override]
        self, argv: Sequence[str] | None = None
    ) -> Namespace:
        """Parses/processes the args, and returns a `Namespace` containing the results.

        The resulting `Namespace` object will include a `logging.Logger` attribute named
        `logger`, which will be initialized with the standard settings for this package.
        It will automatically account for the `-v` or `--verbose` command-line option.

        Args:
            argv:
                A sequence of strings representing the arguments to parse.
                If omitted, `sys.argv` is assumed.
        """
        self.add_option(
            "verbose", "Enable verbose console output.", action="store_true"
        ).add_option("help", "Show this help message.", action="help")

        args = super().parse_args(argv)
        setattr(args, "logger", get_logger(args.verbose))
        delattr(args, "verbose")

        return args

    def print_help(self, file: IO[str] | None = None) -> None:
        """Outputs a message containing information about the command and its options.

        Args:
            file:
                A writeable object to which the help message will be sent.
                If omitted, `sys.stdout` is assumed.
        """
        help_elements: list[ConsoleRenderable] = [
            Text(self.description, justify="center"),
            Text("\nUsage:", "bright_magenta"),
            self._get_usage_text(),
        ]

        def create_table(title: str) -> Table:
            title_text = Text(f"\n{title}:", "bright_magenta")
            table = Table(box=None, expand=True, padding=0)
            table.add_column(title_text, style="bright_cyan", ratio=1)
            table.add_column(ratio=2)
            help_elements.append(table)
            return table

        if self.arg_name:
            arguments_table = create_table("Arguments")
            arguments_table.add_row(
                f"  [bright_green]{self.arg_metavar}[/]", self.arg_description
            )

        options_table = create_table("Options")

        for option in self.options:
            option_text = Text.assemble(
                f"  {option.abbreviation}", (" | ", "bright_black"), option.full_name
            )
            options_table.add_row(option_text, option.description)

        console = Console(file=file or sys.stdout)
        panel = Panel(
            Group(*help_elements),
            title=Text(self.prog, "bright_yellow"),
            subtitle=_HELP_SUBTITLE_TEXT,
            subtitle_align="right",
            width=min(console.width, 69),
        )
        console.print(panel)

    def _get_usage_text(self) -> Text:
        """Returns a rich `Text` object for pretty-printing the command's usage info."""
        usage = self.format_usage().replace(self.arg_name, self.arg_metavar)
        usage = re.sub(r"(\B-[a-z] )\[.+?(\.{3}])]", r"\1\2", usage)
        usage = escape(re.sub(r" \.{3}(])$", r"\1", usage))

        usage_text = Text(f"  {usage[usage.index(self.prog):].strip()}")

        usage_text.highlight_words([self.prog], "bright_yellow")
        usage_text.highlight_words([self.arg_metavar], "bright_green")
        usage_text.highlight_regex(r"\B-[a-z]", "bright_cyan")
        usage_text.highlight_regex(r"[\[\]]", "bright_black")

        return usage_text

    def _validate_arg(
        self, name: str, description: str, positional: bool = False
    ) -> None:
        """Raises a `ValueError` or `RuntimeError` if the arg parameters are invalid."""
        if not (name and description):
            raise ValueError("Both 'name' and 'description' are required.")

        if not re.fullmatch(r"[a-z][a-z_]+" if positional else r"[a-z]+", name):
            raise ValueError("Argument name doesn't fit the required pattern.")

        if positional and self.arg_name:
            raise RuntimeError("Only one positional argument is allowed.")
