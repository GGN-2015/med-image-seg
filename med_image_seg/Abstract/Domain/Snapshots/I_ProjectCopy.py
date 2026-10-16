from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..Annotations.I_MutableAnnotationProject import I_MutableAnnotationProject
from abc import ABC, abstractmethod


# 复制项目并替换网格尺寸，保留已有切片、元数据和编辑记录。
class I_ProjectCopy(ABC):
    # 以新网格尺寸构造项目副本，保留切片标注和其余项目字段。
    @abstractmethod
    def withShape(
        self, project: I_MutableAnnotationProject, shape: tuple[int, int, int]
    ) -> I_MutableAnnotationProject: ...
