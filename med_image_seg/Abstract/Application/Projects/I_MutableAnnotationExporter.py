from __future__ import annotations

from typing import TYPE_CHECKING

from .I_AnnotationExporter import I_AnnotationExporter

if TYPE_CHECKING:
    from ...Storage.Masks.I_MedicalMaskWriter import I_MedicalMaskWriter
from abc import abstractmethod


# 在导出查询契约上增加写入器配置入口，允许替换文件格式适配器。
class I_MutableAnnotationExporter(I_AnnotationExporter):
    # 记录掩码写入服务。
    @abstractmethod
    def setWriter(self, value: I_MedicalMaskWriter) -> None: ...
