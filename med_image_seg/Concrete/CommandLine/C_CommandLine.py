from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from ...Abstract.CommandLine.I_CommandLine import I_CommandLine

if TYPE_CHECKING:
    from ...Abstract.CommandLine.I_CommandOptions import I_CommandOptions
    from ...Abstract.CommandLine.T_CommandParser import T_CommandParser
import argparse
from typing import final


# 协调参数解析与应用启动，并返回进程退出码。
@final
class C_CommandLine(I_CommandLine):
    # 配置位置参数、重复影像选项、间距和语言的命令行解析规则。
    def build_parser(self) -> T_CommandParser[I_CommandOptions]:
        from ..Localization.C_Localizer import C_Localizer
        from ..Storage.Paths.C_FilePath import C_FilePath
        from .C_CommandParser import C_CommandParser

        parser = argparse.ArgumentParser(
            prog="med-image-seg",
            description="Annotate medical image volumes with editable polygons.",
        )
        parser.add_argument(
            "images",
            nargs="*",
            type=C_FilePath,
            help="initial DICOM directories/files, NIfTI files, or UBD files",
        )
        parser.add_argument(
            "--image",
            action="append",
            default=[],
            type=C_FilePath,
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
            choices=C_Localizer().getSupportedLanguages(),
            default="en",
            help="interface language: en or zh (default: en)",
        )
        return C_CommandParser(parser)

    # 解析参数后启动应用，并返回界面宿主的退出码。
    def run(self, argv: Iterable[str] | None = None) -> int:
        from ..Application.Startup.C_ApplicationLauncher import C_ApplicationLauncher

        args = C_CommandLine().build_parser().parse_args(argv)
        return C_ApplicationLauncher().launch(
            [*args.iterExtraImages(), *args.iterImages()],
            spacing_mm=args.getSpacing(),
            language=args.getLanguage(),
        )
