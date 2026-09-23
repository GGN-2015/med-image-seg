from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from med_image_seg import AnnotationApplication
from med_image_seg.cli import build_parser, main


def test_application_accepts_initial_collection(tmp_path: Path) -> None:
    first = tmp_path / "first.nii.gz"
    second = tmp_path / "second.ubd.npz"
    first.write_bytes(b"first")
    second.write_bytes(b"second")

    application = AnnotationApplication.from_paths([first], spacing_mm=0.7)
    application.add_image(second)

    assert application.spacing_mm == 0.7
    assert application.language == "en"
    assert len(application.sources) == 2


def test_application_accepts_chinese_and_rejects_unknown_language() -> None:
    assert AnnotationApplication(language="zh").language == "zh"
    with pytest.raises(ValueError, match="unsupported language"):
        AnnotationApplication(language="fr")  # type: ignore[arg-type]


def test_cli_allows_empty_or_multiple_initial_images() -> None:
    parser = build_parser()

    assert parser.parse_args([]).images == []
    args = parser.parse_args(["one.nii.gz", "two.nii.gz", "--spacing", "1.0"])
    assert args.images == [Path("one.nii.gz"), Path("two.nii.gz")]
    assert args.spacing == 1.0
    assert args.language == "en"


def test_cli_image_option_accepts_one_or_more_initial_images() -> None:
    args = build_parser().parse_args(
        ["--image", "first.nii.gz", "--image", "second.nii.gz"]
    )

    assert args.image == [Path("first.nii.gz"), Path("second.nii.gz")]
    assert args.images == []


def test_cli_accepts_chinese_interface() -> None:
    assert build_parser().parse_args(["--language", "zh"]).language == "zh"


def test_cli_image_option_launches_selected_image() -> None:
    with patch("med_image_seg.cli.launch_annotation_app", return_value=0) as launch:
        status = main(["--image", "scan.nii.gz", "--spacing", "1.0"])

    assert status == 0
    launch.assert_called_once_with(
        [Path("scan.nii.gz")],
        spacing_mm=1.0,
        language="en",
    )
