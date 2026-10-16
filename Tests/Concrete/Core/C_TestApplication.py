from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ...Abstract.Core.I_TestApplication import I_TestApplication

if TYPE_CHECKING:
    from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath
from typing import final
from unittest.mock import patch

import pytest


# 验证启动配置、语言选择和命令行参数到界面的传递。
@final
class C_TestApplication(I_TestApplication):
    # 为当前测试类配置离屏 Qt 环境。
    @pytest.fixture(autouse=True, name="configure_environment")
    def _configure_environment_fixture(self) -> None:
        from ..Environment.C_TestEnvironment import C_TestEnvironment

        C_TestEnvironment().configure()

    # 验证应用接收并保留初始影像集合。
    def test_application_accepts_initial_collection(self, tmp_path: I_FilePath) -> None:
        from med_image_seg.Concrete.Application.Startup import (
            C_ApplicationFactory,
        )

        first = tmp_path / "first.nii.gz"
        second = tmp_path / "second.ubd.npz"
        first.write_bytes(b"first")
        second.write_bytes(b"second")
        application = C_ApplicationFactory().from_paths([first], spacing_mm=0.7)
        application.add_image(second)
        assert application.getSpacingMm() == 0.7
        assert application.getLanguage() == "en"
        assert len(application.getSources()) == 2

    # 验证应用接受中文配置并拒绝未知语言。
    def test_application_accepts_chinese_and_rejects_unknown_language(self) -> None:
        from med_image_seg.Concrete.Application.Startup import (
            C_AnnotationApplication,
        )

        assert C_AnnotationApplication(language="zh").getLanguage() == "zh"
        with pytest.raises(ValueError, match="unsupported language"):
            C_AnnotationApplication(language="fr")

    # 验证命令行允许无初始影像或多个影像路径。
    def test_cli_allows_empty_or_multiple_initial_images(self) -> None:
        from med_image_seg.Concrete.CommandLine.C_CommandLine import C_CommandLine
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        parser = C_CommandLine().build_parser()
        assert list(parser.parse_args([]).iterImages()) == []
        args = parser.parse_args(["one.nii.gz", "two.nii.gz", "--spacing", "1.0"])
        assert list(args.iterImages()) == [
            C_FilePath("one.nii.gz"),
            C_FilePath("two.nii.gz"),
        ]
        assert args.getSpacing() == 1.0
        assert args.getLanguage() == "en"

    # 验证重复影像选项可以传入一个或多个初始影像。
    def test_cli_image_option_accepts_one_or_more_initial_images(self) -> None:
        from med_image_seg.Concrete.CommandLine.C_CommandLine import C_CommandLine
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        args = (
            C_CommandLine()
            .build_parser()
            .parse_args(["--image", "first.nii.gz", "--image", "second.nii.gz"])
        )
        assert list(args.iterExtraImages()) == [
            C_FilePath("first.nii.gz"),
            C_FilePath("second.nii.gz"),
        ]
        assert list(args.iterImages()) == []

    # 验证命令行可以选择中文界面。
    def test_cli_accepts_chinese_interface(self) -> None:
        from med_image_seg.Concrete.CommandLine.C_CommandLine import C_CommandLine

        assert (
            C_CommandLine()
            .build_parser()
            .parse_args(["--language", "zh"])
            .getLanguage()
            == "zh"
        )

    # 验证命令行选择的影像传递到应用启动流程。
    def test_cli_image_option_launches_selected_image(self) -> None:
        from med_image_seg.Concrete.CommandLine.C_CommandLine import C_CommandLine
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        with patch(
            (
                "med_image_seg.Concrete.Application.Startup.C_ApplicationLa"
                "uncher.C_ApplicationLauncher.launch"
            ),
            return_value=0,
        ) as launch:
            status = C_CommandLine().run(["--image", "scan.nii.gz", "--spacing", "1.0"])
        assert status == 0
        launch.assert_called_once_with(
            [C_FilePath("scan.nii.gz")], spacing_mm=1.0, language="en"
        )

    # 把 pytest 临时目录转换为路径接口，供业务测试复用。
    @pytest.fixture(name="tmp_path")
    def _adapt_path(self, tmp_path: Path) -> I_FilePath:
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        return C_FilePath(tmp_path)
