from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, final

if TYPE_CHECKING:
    from ..Storage.Paths.I_FilePath import I_FilePath
from abc import ABC, abstractmethod


# 保存解析后的启动选项，按项提供初始影像路径。
class I_CommandOptions(ABC):
    # 返回启动时指定的标注网格间距。
    @abstractmethod
    def getSpacing(self) -> float: ...

    # 返回当前中英界面语言代码。
    @abstractmethod
    def getLanguage(self) -> str: ...

    # 返回命令行位置参数中的影像数量。
    @abstractmethod
    def getImageCount(self) -> int: ...

    # 按索引取得命令行位置参数指定的影像路径。
    @abstractmethod
    def getImage(self, index: int) -> I_FilePath: ...

    # 按输入顺序迭代命令行的位置参数影像路径。
    @final
    def iterImages(self) -> Iterator[I_FilePath]:
        for index in range(self.getImageCount()):
            yield self.getImage(index)

    # 返回命令行影像选项指定的额外路径数量。
    @abstractmethod
    def getExtraImageCount(self) -> int: ...

    # 按索引取得命令行影像选项指定的额外路径。
    @abstractmethod
    def getExtraImage(self, index: int) -> I_FilePath: ...

    # 按命令行顺序迭代通过影像选项指定的额外路径。
    @final
    def iterExtraImages(self) -> Iterator[I_FilePath]:
        for index in range(self.getExtraImageCount()):
            yield self.getExtraImage(index)
