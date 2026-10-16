from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Domain.Annotations.I_MutableAnnotationProject import (
        I_MutableAnnotationProject,
    )
    from ...Domain.Imaging.I_MedicalVolume import I_MedicalVolume
from abc import ABC, abstractmethod


# 核对标注与影像的尺寸、间距和原点，防止掩码错位。
class I_VolumeGeometryValidator(ABC):
    # 核对标注与影像的体素尺寸、间距和原点，拒绝几何不一致。
    @abstractmethod
    def validate_volume(
        self, context: I_MutableAnnotationProject, volume: I_MedicalVolume
    ) -> None: ...
