from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray

from med_image_seg.Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath


# 构造参考网格及掩码文件，供物理坐标对齐测试使用。
class I_ExternalMaskReaderFixtures(ABC):
    # 创建具有已知尺寸、间距和原点的参考影像，用于掩码对齐测试。
    @abstractmethod
    def reference(
        self,
        tmp_path: I_FilePath,
        shape: tuple[int, int, int] = (6, 5, 4),
        spacing: tuple[float, float, float] = (1.0, 1.0, 1.0),
    ) -> I_MedicalVolume: ...

    # 按后缀写入具有指定间距和原点的测试掩码。
    @abstractmethod
    def write(
        self,
        path: I_FilePath,
        data: NDArray[np.generic],
        reference: I_MedicalVolume,
        *,
        spacing: tuple[float, float, float] | None = None,
        origin: tuple[float, float, float] | None = None,
        direction: tuple[float, ...] | None = None,
    ) -> None: ...
