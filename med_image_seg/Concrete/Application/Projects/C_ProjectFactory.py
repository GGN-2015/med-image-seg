from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Application.Projects.I_ProjectFactory import I_ProjectFactory

if TYPE_CHECKING:
    from ....Abstract.Domain.Annotations.I_MutableAnnotationProject import (
        I_MutableAnnotationProject,
    )
    from ....Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
from typing import final


# 以当前影像及网格创建标注项目，统一新项目的几何信息。
@final
class C_ProjectFactory(I_ProjectFactory):
    # 按影像来源、体素尺寸、间距和原点创建新的标注项目。
    def create(
        self, *, image_id: str, source_fingerprint: str, volume: I_MedicalVolume
    ) -> I_MutableAnnotationProject:
        from ...Domain.Annotations.C_AnnotationProject import C_AnnotationProject

        return C_AnnotationProject(
            image_id=image_id,
            source_fingerprint=source_fingerprint,
            shape_lps=(
                int(volume.getData().shape[0]),
                int(volume.getData().shape[1]),
                int(volume.getData().shape[2]),
            ),
            spacing_lps_mm=volume.getSpacingMm(),
            origin_lps_mm=volume.getOriginLpsMm(),
        )
