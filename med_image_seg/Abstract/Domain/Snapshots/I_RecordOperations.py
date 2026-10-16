from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..Annotations.I_AnnotationProject import I_AnnotationProject
    from ..Annotations.I_PolygonAnnotation import I_PolygonAnnotation
    from ..Annotations.I_SliceAnnotation import I_SliceAnnotation
    from .I_RecordSnapshot import I_RecordSnapshot
from abc import ABC, abstractmethod


# 将项目、切片或轮廓转换为 JSON 快照，保留现有磁盘字段结构。
class I_RecordOperations(ABC):
    # 序列化为保留原有字段结构的 JSON 快照，而不是返回可变字典。
    @abstractmethod
    def asdict(
        self, record: I_AnnotationProject | I_PolygonAnnotation | I_SliceAnnotation
    ) -> I_RecordSnapshot: ...
