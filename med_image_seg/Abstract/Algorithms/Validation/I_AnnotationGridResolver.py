from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Domain.Imaging.I_ImageSource import I_ImageSource
from abc import ABC, abstractmethod


# 选择影像加载网格；已有兼容标注优先使用其保存间距，新项目使用界面请求值。
class I_AnnotationGridResolver(ABC):
    # 返回当前编号应使用的等距网格；标注缺失、不可信或非等距时保留请求值。
    @abstractmethod
    def resolve(
        self, source: I_ImageSource, annotation_index: int, requested_spacing_mm: float
    ) -> float: ...
