from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Algorithms.Validation.I_VolumeGeometryValidator import (
    I_VolumeGeometryValidator,
)

if TYPE_CHECKING:
    from ....Abstract.Domain.Annotations.I_MutableAnnotationProject import (
        I_MutableAnnotationProject,
    )
    from ....Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
from typing import final

import numpy as np


# 核对标注与影像的尺寸、间距和原点，防止掩码错位。
@final
class C_VolumeGeometryValidator(I_VolumeGeometryValidator):
    # 核对标注与影像的体素尺寸、间距和原点，拒绝几何不一致。
    def validate_volume(
        self, context: I_MutableAnnotationProject, volume: I_MedicalVolume
    ) -> None:
        if tuple(volume.getData().shape) != context.getShapeLps():
            raise ValueError("annotation shape does not match the loaded volume")
        if not np.allclose(volume.getSpacingMm(), context.getSpacingLpsMm()):
            raise ValueError("annotation spacing does not match the loaded volume")
        if not np.allclose(volume.getOriginLpsMm(), context.getOriginLpsMm()):
            raise ValueError("annotation origin does not match the loaded volume")
