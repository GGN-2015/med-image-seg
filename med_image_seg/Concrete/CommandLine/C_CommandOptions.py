from __future__ import annotations

from typing import TYPE_CHECKING

from ...Abstract.CommandLine.I_CommandOptions import I_CommandOptions

if TYPE_CHECKING:
    from ...Abstract.Storage.Paths.I_FilePath import I_FilePath
import argparse
from typing import final


# 保存解析后的启动选项，按项提供初始影像路径。
@final
class C_CommandOptions(I_CommandOptions):
    # 保存解析后的影像路径、网格间距和语言选项。
    def __init__(self, namespace: argparse.Namespace) -> None:
        self._namespace = namespace

    # 返回启动时指定的标注网格间距。
    def getSpacing(self) -> float:
        return self._namespace.spacing

    # 返回当前中英界面语言代码。
    def getLanguage(self) -> str:
        return self._namespace.language

    # 返回命令行位置参数中的影像数量。
    def getImageCount(self) -> int:
        return len(self._namespace.images)

    # 按索引取得命令行位置参数指定的影像路径。
    def getImage(self, index: int) -> I_FilePath:
        return self._namespace.images[index]

    # 返回命令行影像选项指定的额外路径数量。
    def getExtraImageCount(self) -> int:
        return len(self._namespace.image)

    # 按索引取得命令行影像选项指定的额外路径。
    def getExtraImage(self, index: int) -> I_FilePath:
        return self._namespace.image[index]
