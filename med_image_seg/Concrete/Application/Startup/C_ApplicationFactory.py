from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Application.Startup.I_ApplicationFactory import I_ApplicationFactory
from ....Abstract.Application.Startup.I_MutableAnnotationApplication import (
    I_MutableAnnotationApplication,
)

if TYPE_CHECKING:
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
from collections.abc import Iterable
from typing import final


# 构造应用配置，集中选择影像集合和默认参数的实现。
@final
class C_ApplicationFactory(I_ApplicationFactory):
    # 按输入顺序创建影像集合，并按来源指纹去重。
    def from_paths(
        self,
        paths: Iterable[str | I_FilePath],
        *,
        spacing_mm: float = 0.8,
        language: str = "en",
    ) -> I_MutableAnnotationApplication:
        from ...Domain.Collections.C_ImageCollection import C_ImageCollection
        from .C_AnnotationApplication import C_AnnotationApplication

        return C_AnnotationApplication(
            spacing_mm=spacing_mm, language=language, sources=C_ImageCollection(paths)
        )
