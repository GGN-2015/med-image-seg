from __future__ import annotations

import json
from typing import final

import numpy as np
import SimpleITK as sitk
from numpy.typing import NDArray

from med_image_seg.Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

from ...Abstract.Storage.I_ExternalMaskReaderFixtures import (
    I_ExternalMaskReaderFixtures,
)


# 构造参考网格及掩码文件，供物理坐标对齐测试使用。
@final
class C_ExternalMaskReaderFixtures(I_ExternalMaskReaderFixtures):
    # 创建具有已知尺寸、间距和原点的参考影像，用于掩码对齐测试。
    def reference(
        self,
        tmp_path: I_FilePath,
        shape: tuple[int, int, int] = (6, 5, 4),
        spacing: tuple[float, float, float] = (1.0, 1.0, 1.0),
    ) -> I_MedicalVolume:
        from med_image_seg.Concrete.Domain.Imaging.C_MedicalVolume import (
            C_MedicalVolume,
        )
        from med_image_seg.Concrete.Domain.Imaging.C_Metadata import C_Metadata

        return C_MedicalVolume(
            data=np.zeros(shape, dtype=np.float32),
            spacing_mm=spacing,
            origin_lps_mm=(10.0, -20.0, 30.0),
            metadata=C_Metadata(json.dumps({})),
            source=tmp_path / "scan.nii",
        )

    # 按后缀写入具有指定间距和原点的测试掩码。
    def write(
        self,
        path: I_FilePath,
        data: NDArray[np.generic],
        reference: I_MedicalVolume,
        *,
        spacing: tuple[float, float, float] | None = None,
        origin: tuple[float, float, float] | None = None,
        direction: tuple[float, ...] | None = None,
    ) -> None:
        image = sitk.GetImageFromArray(np.transpose(data, (2, 1, 0)))
        image.SetSpacing(spacing or reference.getSpacingMm())
        image.SetOrigin(origin or reference.getOriginLpsMm())
        if direction is not None:
            image.SetDirection(direction)
        sitk.WriteImage(image, str(path))
