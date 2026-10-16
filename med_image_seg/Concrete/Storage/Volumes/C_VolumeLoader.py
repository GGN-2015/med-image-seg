from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from ....Abstract.Storage.Volumes.I_VolumeLoader import I_VolumeLoader

if TYPE_CHECKING:
    from ....Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
from typing import final


# 按指定间距加载医学影像，将读取器的构造细节留在存储层。
@final
class C_VolumeLoader(I_VolumeLoader):
    # 按指定间距读取并重采样医学影像，返回体积接口。
    def load_volume(
        self,
        path: str | I_FilePath,
        spacing_mm: float = 0.8,
        *,
        interpolation: Literal["linear", "nearest"] = "linear",
    ) -> I_MedicalVolume:
        from .C_MedicalVolumeReader import C_MedicalVolumeReader

        return C_MedicalVolumeReader(spacing_mm).read(path, interpolation=interpolation)
