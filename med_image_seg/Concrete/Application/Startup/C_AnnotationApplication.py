from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Application.Startup.I_MutableAnnotationApplication import (
    I_MutableAnnotationApplication,
)
from ....Abstract.Domain.Collections.I_MutableImageCollection import (
    I_MutableImageCollection,
)
from ....Abstract.Domain.Defaults.E_DefaultValue import E_DefaultValue
from ....Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
from ....Abstract.Domain.Records.I_RecordFieldList import I_RecordFieldList
from ....Abstract.Storage.Paths.I_FilePath import I_FilePath

if TYPE_CHECKING:
    from ....Abstract.Domain.Collections.I_MutableImageCollection import (
        I_MutableImageCollection,
    )
    from ....Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
from dataclasses import dataclass
from typing import final


# 应用启动配置：保存语言、标注间距和影像集合，不依赖界面框架。
@final
@dataclass(slots=True, frozen=False, init=False)
class C_AnnotationApplication(I_MutableAnnotationApplication):
    _state_spacing_mm: float
    _state_language: str
    _state_sources: I_MutableImageCollection

    # 保存语言、间距和影像集合，使用默认集合填补未传入参数。
    def __init__(
        self,
        spacing_mm: float = 0.8,
        language: str = "en",
        sources: I_MutableImageCollection | E_DefaultValue = E_DefaultValue.Unset,
    ) -> None:
        from ...Domain.Collections.C_ImageCollection import C_ImageCollection

        object.__setattr__(self, "_state_spacing_mm", spacing_mm)
        object.__setattr__(self, "_state_language", language)
        object.__setattr__(
            self,
            "_state_sources",
            C_ImageCollection() if sources is E_DefaultValue.Unset else sources,
        )
        self.__post_init__()

    # 返回 LPS 网格间距，单位为毫米。
    def getSpacingMm(self) -> float:
        return self._state_spacing_mm

    # 记录LPS 网格间距，单位为毫米。
    def setSpacingMm(self, value: float) -> None:
        self._state_spacing_mm = value

    # 返回当前中英界面语言代码。
    def getLanguage(self) -> str:
        return self._state_language

    # 记录当前中英界面语言代码。
    def setLanguage(self, value: str) -> None:
        self._state_language = value

    # 通过集合接口访问影像，支持按数量、索引和指纹查询。
    def getSources(self) -> I_MutableImageCollection:
        return self._state_sources

    # 设置应用使用的影像集合接口，不暴露集合内部的存储结构。
    def setSources(self, value: I_MutableImageCollection) -> None:
        self._state_sources = value

    # 返回有序的记录字段名，供序列化读取。
    def getRecordFields(self) -> I_RecordFieldList:
        from ...Domain.Records.C_RecordFieldList import C_RecordFieldList

        return C_RecordFieldList(("spacing_mm", "language", "sources"))

    # 校验启动间距与语言，拒绝不支持的应用配置。
    def __post_init__(self) -> None:
        from ...Localization.C_Localizer import C_Localizer

        if self.getSpacingMm() <= 0:
            raise ValueError("spacing_mm must be greater than zero")
        self.setLanguage(C_Localizer().normalize_language(self.getLanguage()))

    # 从路径创建影像源并加入应用的去重集合。
    def add_image(self, path: str | I_FilePath) -> I_ImageSource:
        return self.getSources().add(path)

    # 把已配置的影像集合、间距和语言交给界面宿主运行。
    def run(self) -> int:
        from .C_Qt_ApplicationHost import C_Qt_ApplicationHost

        return C_Qt_ApplicationHost().run(
            sources=self.getSources(),
            spacing_mm=self.getSpacingMm(),
            language=self.getLanguage(),
        )
