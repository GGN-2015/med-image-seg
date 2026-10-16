from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Domain.Snapshots.I_ProjectCopy import I_ProjectCopy

if TYPE_CHECKING:
    from ....Abstract.Domain.Annotations.I_MutableAnnotationProject import (
        I_MutableAnnotationProject,
    )
from typing import final


# 复制项目并替换网格尺寸，保留已有切片、元数据和编辑记录。
@final
class C_ProjectCopy(I_ProjectCopy):
    # 以新网格尺寸构造项目副本，保留切片标注和其余项目字段。
    def withShape(
        self, project: I_MutableAnnotationProject, shape: tuple[int, int, int]
    ) -> I_MutableAnnotationProject:
        from ..Annotations.C_AnnotationProject import C_AnnotationProject

        return C_AnnotationProject(
            image_id=project.getImageId(),
            source_fingerprint=project.getSourceFingerprint(),
            shape_lps=shape,
            spacing_lps_mm=project.getSpacingLpsMm(),
            origin_lps_mm=project.getOriginLpsMm(),
            slices={
                _entry_index: project.annotation(_entry_index)
                for _entry_index in project.iterSliceIndices()
            },
            metadata=project.getMetadata(),
            edit_counter=project.getEditCounter(),
            schema_version=project.getSchemaVersion(),
            updated_at=project.getUpdatedAt(),
        )
