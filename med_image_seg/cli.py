"""Command line interface for med-image-seg."""

from __future__ import annotations

import argparse
from pathlib import Path

from .application import launch_annotation_app
from .localization import SUPPORTED_LANGUAGES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="med-image-seg",
        description="Annotate medical image volumes with editable polygons.",
    )
    parser.add_argument(
        "images",
        nargs="*",
        type=Path,
        help="initial DICOM directories/files, NIfTI files, or UBD files",
    )
    parser.add_argument(
        "--image",
        action="append",
        default=[],
        type=Path,
        metavar="PATH",
        help="open this image on startup; repeat to add an image collection",
    )
    parser.add_argument(
        "--spacing",
        type=float,
        default=0.8,
        help="isotropic annotation grid in mm (default: 0.8)",
    )
    parser.add_argument(
        "--language",
        choices=SUPPORTED_LANGUAGES,
        default="en",
        help="interface language: en or zh (default: en)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return launch_annotation_app(
        [*args.image, *args.images],
        spacing_mm=args.spacing,
        language=args.language,
    )


if __name__ == "__main__":
    raise SystemExit(main())
