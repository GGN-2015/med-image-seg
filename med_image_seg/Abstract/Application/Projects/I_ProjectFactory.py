from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Domain.Annotations.I_MutableAnnotationProject import (
        I_MutableAnnotationProject,
    )
    from ...Domain.Imaging.I_MedicalVolume import I_MedicalVolume
from abc import ABC, abstractmethod


# 以当前影像及网格创建标注项目，统一新项目的几何信息。
class I_ProjectFactory(ABC):
    # 按影像来源、体素尺寸、间距和原点创建新的标注项目。
    @abstractmethod
    def create(
        self, *, image_id: str, source_fingerprint: str, volume: I_MedicalVolume
    ) -> I_MutableAnnotationProject: ...
