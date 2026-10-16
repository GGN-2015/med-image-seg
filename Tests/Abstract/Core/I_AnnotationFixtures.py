from __future__ import annotations

from abc import ABC, abstractmethod

from med_image_seg.Abstract.Domain.Annotations import (
    I_MutableAnnotationProject,
)
from med_image_seg.Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume


# 构造轮廓、关键层和项目样本，供标注算法测试复用。
class I_AnnotationFixtures(ABC):
    # 构造与测试影像源对应的体素和几何信息。
    @abstractmethod
    def volume(self) -> I_MedicalVolume: ...

    # 构造与测试影像几何匹配的标注项目。
    @abstractmethod
    def project(self) -> I_MutableAnnotationProject: ...
