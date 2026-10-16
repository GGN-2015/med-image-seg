from __future__ import annotations

from typing import TYPE_CHECKING

from .I_MutableAnnotationApplication import I_MutableAnnotationApplication

if TYPE_CHECKING:
    from ...Storage.Paths.I_FilePath import I_FilePath
from abc import ABC, abstractmethod
from collections.abc import Iterable


# 构造应用配置，集中选择影像集合和默认参数的实现。
class I_ApplicationFactory(ABC):
    # 按输入顺序创建影像集合，并按来源指纹去重。
    @abstractmethod
    def from_paths(
        self,
        paths: Iterable[str | I_FilePath],
        *,
        spacing_mm: float = 0.8,
        language: str = "en",
    ) -> I_MutableAnnotationApplication: ...
