from pathlib import Path
from string import Template
from typing import Final, Literal, TypeAlias, get_args

from cairosvg import svg2png
from defusedxml import ElementTree

from queemoji_scripts._utils import get_display_path

_BorderStyle: TypeAlias = Literal["black", "white", "none"]
_BORDER_STYLES: Final[tuple[str, ...]] = tuple(str(bs) for bs in get_args(_BorderStyle))

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
