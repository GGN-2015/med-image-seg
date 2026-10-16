from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Application.Projects.I_MutableAnnotationExporter import (
    I_MutableAnnotationExporter,
)

if TYPE_CHECKING:
    from ....Abstract.Domain.Annotations.I_AnnotationProject import I_AnnotationProject
    from ....Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from ....Abstract.Storage.Masks.I_MedicalMaskWriter import I_MedicalMaskWriter
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
from typing import final


# 协调项目保存和三维掩码导出，让界面不直接处理文件格式。
@final
class C_AnnotationExporter(I_MutableAnnotationExporter):
    # 返回掩码写入服务。
    def getWriter(self) -> I_MedicalMaskWriter:
        return self._state_writer

    # 记录掩码写入服务。
    def setWriter(self, value: I_MedicalMaskWriter) -> None:
        self._state_writer = value

    # 保存掩码写入服务，使导出流程不依赖具体文件格式实现。
    def __init__(self, writer: I_MedicalMaskWriter | None = None) -> None:
        from ...Storage.Masks.C_MedicalMaskWriter import C_MedicalMaskWriter

        self.setWriter(writer or C_MedicalMaskWriter())

    # 按指定输出路径生成包含插值的三维掩码，再交给写入器保存。
    def export(
        self,
        project: I_AnnotationProject,
        volume: I_MedicalVolume,
        output_path: str | I_FilePath,
        *,
        interpolate: bool = True,
    ) -> I_FilePath:
        project.validate_volume(volume)
        return self.getWriter().write(
            output_path, project.to_mask(interpolate=interpolate), volume
        )
