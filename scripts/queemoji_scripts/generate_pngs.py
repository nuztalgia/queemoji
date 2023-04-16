from collections.abc import Sequence
from pathlib import Path
from string import Template
from typing import Final, Literal, TypeAlias, get_args

from cairosvg import svg2png
from defusedxml import ElementTree

from queemoji_scripts._sub_parser import SubParser
from queemoji_scripts._utils import get_display_path, get_valid_files

_BorderStyle: TypeAlias = Literal["black", "white", "none"]
_BORDER_STYLES: Final[tuple[str, ...]] = tuple(str(bs) for bs in get_args(_BorderStyle))

_DEFAULT_INPUT_PATH: Final[Path] = Path.cwd() / "svg"
_DEFAULT_OUTPUT_TEMPLATE: Final[Template] = Template("./png/${input_name}")
_DEFAULT_BORDER: Final[str] = _BORDER_STYLES[0]
_DEFAULT_SIZE_PX: Final[int] = 128

_MIN_SIZE_PX: Final[int] = 16
_MAX_SIZE_PX: Final[int] = 1024


def generate_png(
    input_file: Path,
    output_path_template: Template = _DEFAULT_OUTPUT_TEMPLATE,
    *,
    border: _BorderStyle = _DEFAULT_BORDER,  # type: ignore[assignment]
    size: int = _DEFAULT_SIZE_PX,
    replace: bool = False,
) -> Path:
    """Converts the input SVG into a PNG and returns the output file path if successful.

    Args:
        input_file:
            A valid `Path` to the SVG file that should be converted into a PNG image.
        output_path_template:
            A `Template` representing the desired format for the output PNG file path
            relative to the current working directory. May include placeholders for
            `${input_name}`, `${border_label}`, and `${size}`, as per the parameters.
            Should not include the `.png` suffix, as this will be added automatically.
        border:
            The color to use for the `stroke` attribute on the first SVG element with
            the `border` class. Must be one of `"black"`, `"white"`, or `"none"`.
        size:
            The desired size for the resulting PNG image. Will determine both width and
            height. Must be an integer between 16 and 1024 (inclusive on both ends).
        replace:
            Whether to overwrite the output file if it already exists. If `False`,
            will raise a `FileExistsError` upon encountering an existing output file.
    """
    if (not input_file.is_file()) or (input_file.suffix != ".svg"):
        raise ValueError(f"Input must be an existing SVG file: {input_file}")

    input_svg_root = ElementTree.parse(input_file.resolve()).getroot()
    input_svg_root.find("./*[@class='border']").set("stroke", border)

    if border not in _BORDER_STYLES:
        raise ValueError(f"Border must be one of {'/'.join(_BORDER_STYLES)}: {border}")

    if (size < _MIN_SIZE_PX) or (size > _MAX_SIZE_PX):
        raise ValueError(
            f"Size must be a number between {_MIN_SIZE_PX} and {_MAX_SIZE_PX}: {size}"
        )

    output_path_string = output_path_template.substitute(
        border_label=("borderless" if (border == "none") else f"border-{border}"),
        input_name=input_file.stem,
        size=size,
    )
    output_file = (Path.cwd() / f"{output_path_string}.png").resolve()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    if output_file.exists() and not replace:
        display_path = get_display_path(output_file)
        raise FileExistsError(
            f"Output file already exists and '-r' was not specified: {display_path}"
        )

    svg2png(
        bytestring=ElementTree.tostring(input_svg_root),
        parent_width=size,
        parent_height=size,
        write_to=str(output_file),
    )
    return output_file


def _get_arg_parser() -> SubParser:
    """Creates and returns a `SubParser` for parsing this script's command-line args."""
    return (
        SubParser(__file__, description=main.__doc__)
        .add_positional_arg(
            "input_paths",
            description=(
                f"Path(s) to SVG files (or folders containing SVGs). "
                f"Will not recurse into sub-folders.\n[bright_black]  "
                f"╰─ Default:  {get_display_path(_DEFAULT_INPUT_PATH)}[/]"
            ),
            type=Path,
            metavar="paths",
        )
        .add_option(
            "output",
            description=(
                f"Output file path, relative to current dir.\n  [bright_black]"
                f"╰─ Default:  {_DEFAULT_OUTPUT_TEMPLATE.template}[/]"
            ),
            default=_DEFAULT_OUTPUT_TEMPLATE,
            type=Template,
            metavar="OUT",
            dest="output_path_template",
        )
        .add_option(
            "border",
            description=(
                f"Emoji border style(s). Defaults to {_DEFAULT_BORDER}.\n  "
                f"[bright_black]╰─ Choices:  {' / '.join(_BORDER_STYLES)}[/]"
            ),
            default=_DEFAULT_BORDER,
            choices=_BORDER_STYLES,
            nargs="*",
        )
        .add_option(
            "size",
            description=f"Size(s) of output PNGs. Defaults to {_DEFAULT_SIZE_PX}.",
            default=_DEFAULT_SIZE_PX,
            type=int,
            nargs="*",
        )
        .add_option(
            "replace",
            description="Allow existing PNG files to be overwritten.",
            action="store_true",
        )
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Creates PNG images from source SVG files."""
    args = _get_arg_parser().parse_args(argv)

    if not args.input_paths:
        default_path_info = f"Checking '{get_display_path(_DEFAULT_INPUT_PATH)}'."
        args.logger.debug(f"No input paths provided. {default_path_info}")
        args.input_paths.append(_DEFAULT_INPUT_PATH)

    for arg_name in ("border", "size"):
        raw_value = getattr(args, arg_name)
        set_value = set(raw_value) if isinstance(raw_value, list) else {raw_value}
        setattr(args, arg_name, sorted(set_value))

    input_files = get_valid_files(args.input_paths, "svg", warn=args.logger.warning)
    pngs_generated = 0

    if not (file_count := len(input_files)):
        args.logger.error("[bright_red]No valid SVG source files were detected.[/]")
        return 1

    args.logger.info(
        f"[bright_green]Detected {file_count} SVG source file"
        f"{'s' if (file_count != 1) else ''}. Starting PNG image creation.[/]"
    )

    for input_file in input_files:
        input_file_info = f"for input file: {get_display_path(input_file)}"
        for border in args.border:
            border_info = f"with {'no' if (border == 'none') else border} border"
            for size in args.size:
                try:
                    args.logger.debug(
                        f"Creating {size}px image {border_info} {input_file_info}"
                    )
                    output_path = generate_png(
                        input_file=input_file,
                        output_path_template=args.output_path_template,
                        border=border,
                        size=size,
                        replace=args.replace,
                    )
                    args.logger.info(
                        f"Successfully generated image: {get_display_path(output_path)}"
                    )
                    pngs_generated += 1
                except FileExistsError as error:
                    args.logger.info(error)

    args.logger.info(
        f"[bright_{'green' if (pngs_generated > 0) else 'yellow'}]Script complete. "
        f"Generated {pngs_generated} new file{'s' if (pngs_generated != 1) else ''}.[/]"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
