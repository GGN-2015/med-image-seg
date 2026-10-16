from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable

from ...Storage.Paths.I_FilePath import I_FilePath
from ..Imaging.I_ImageSource import I_ImageSource
from .I_ImageCollection import I_ImageCollection


# 在只读影像查询上增加逐项导入，保留指纹去重和输入顺序。
class I_MutableImageCollection(I_ImageCollection):
    # 按指纹添加影像；重复来源复用已有项，首次导入保持顺序。
    @abstractmethod
    def add(self, source: str | I_FilePath | I_ImageSource) -> I_ImageSource: ...

    # 逐项导入并去重，保持新增影像的首次出现顺序。
    @abstractmethod
    def extend(self, sources: Iterable[str | I_FilePath | I_ImageSource]) -> None: ...
