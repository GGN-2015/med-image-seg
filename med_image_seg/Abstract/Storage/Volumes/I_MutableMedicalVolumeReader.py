from __future__ import annotations

from abc import abstractmethod

from .I_MedicalVolumeReader import I_MedicalVolumeReader


# 在读取器契约上增加目标网格间距的配置入口。
class I_MutableMedicalVolumeReader(I_MedicalVolumeReader):
    # 记录读取器使用的标注网格间距。
    @abstractmethod
    def setInternalSpacingMm(self, value: float) -> None: ...
