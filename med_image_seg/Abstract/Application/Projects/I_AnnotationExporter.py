from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Domain.Annotations.I_AnnotationProject import I_AnnotationProject
    from ...Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from ...Storage.Masks.I_MedicalMaskWriter import I_MedicalMaskWriter
    from ...Storage.Paths.I_FilePath import I_FilePath
from abc import ABC, abstractmethod


# 协调项目保存和三维掩码导出，让界面不直接处理文件格式。
class I_AnnotationExporter(ABC):
    # 返回掩码写入服务。
    @abstractmethod
    def getWriter(self) -> I_MedicalMaskWriter: ...

    # 按指定输出路径生成包含插值的三维掩码，再交给写入器保存。
    @abstractmethod
    def export(
        self,
        project: I_AnnotationProject,
        volume: I_MedicalVolume,
        output_path: str | I_FilePath,
        *,
        interpolate: bool = True,
    ) -> I_FilePath: ...
