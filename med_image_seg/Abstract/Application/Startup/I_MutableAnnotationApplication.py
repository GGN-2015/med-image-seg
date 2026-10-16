from __future__ import annotations

from typing import TYPE_CHECKING

from ...Domain.Collections.I_MutableImageCollection import I_MutableImageCollection
from .I_AnnotationApplication import I_AnnotationApplication

if TYPE_CHECKING:
    from ...Domain.Imaging.I_ImageSource import I_ImageSource
    from ...Storage.Paths.I_FilePath import I_FilePath
from abc import abstractmethod


# 在只读启动配置上增加语言、间距和影像集合的修改入口。
class I_MutableAnnotationApplication(I_AnnotationApplication):
    # 记录LPS 网格间距，单位为毫米。
    @abstractmethod
    def setSpacingMm(self, value: float) -> None: ...

    # 记录当前中英界面语言代码。
    @abstractmethod
    def setLanguage(self, value: str) -> None: ...

    # 设置应用使用的影像集合接口，不暴露集合内部的存储结构。
    @abstractmethod
    def setSources(self, value: I_MutableImageCollection) -> None: ...

    # 从路径创建影像源并加入应用的去重集合。
    @abstractmethod
    def add_image(self, path: str | I_FilePath) -> I_ImageSource: ...

    # 把已配置的影像集合、间距和语言交给界面宿主运行。
    @abstractmethod
    def run(self) -> int: ...
