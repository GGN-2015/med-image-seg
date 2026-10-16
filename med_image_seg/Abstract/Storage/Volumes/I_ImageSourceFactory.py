from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Domain.Imaging.I_ImageSource import I_ImageSource
    from ..Paths.I_FilePath import I_FilePath
from abc import ABC, abstractmethod


# 从输入路径识别影像类型，计算指纹并确定配套文件位置。
class I_ImageSourceFactory(ABC):
    # 从文件或目录创建影像源，确定类型、指纹及配套输出路径。
    @abstractmethod
    def from_path(self, path: str | I_FilePath) -> I_ImageSource: ...
