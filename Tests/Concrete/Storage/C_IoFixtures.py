from __future__ import annotations

from typing import TYPE_CHECKING

from ...Abstract.Storage.I_IoFixtures import I_IoFixtures

if TYPE_CHECKING:
    from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath
from typing import final

import numpy as np
import SimpleITK as sitk


# 生成测试 DICOM 和 NIfTI 文件，集中管理格式库的测试适配。
@final
class C_IoFixtures(I_IoFixtures):
    # 生成已知体素及物理几何的 NIfTI 测试文件。
    def write_test_nifti(self, path: I_FilePath) -> None:
        array = np.arange(4 * 5 * 6, dtype=np.float32).reshape(4, 5, 6)
        image = sitk.GetImageFromArray(array)
        image.SetSpacing((1.0, 1.0, 1.0))
        image.SetOrigin((1.0, 2.0, 3.0))
        sitk.WriteImage(image, str(path))

    # 生成带完整几何标签的 DICOM 测试序列。
    def write_test_dicom_series(self, directory: I_FilePath) -> None:
        directory.mkdir()
        writer = sitk.ImageFileWriter()
        writer.SetImageIO("GDCMImageIO")
        writer.KeepOriginalImageUIDOn()
        series_uid = "1.2.826.0.1.3680043.2.1125.20260923.1"
        study_uid = "1.2.826.0.1.3680043.2.1125.20260923"
        for index in range(4):
            array = np.full((12, 16), index * 100, dtype=np.int16)
            image = sitk.GetImageFromArray(array)
            image.SetSpacing((0.7, 0.8))
            tags = {
                "0008|0018": f"{series_uid}.{index + 1}",
                "0008|0060": "CT",
                "0018|0050": "1.2",
                "0020|000d": study_uid,
                "0020|000e": series_uid,
                "0020|0013": str(index + 1),
                "0020|0032": f"0\\0\\{index * 1.2}",
                "0020|0037": "1\\0\\0\\0\\1\\0",
                "0028|0030": "0.8\\0.7",
                "0028|1052": "0",
                "0028|1053": "1",
            }
            for tag, value in tags.items():
                image.SetMetaData(tag, value)
            writer.SetFileName(str(directory / f"slice-{index:03d}.dcm"))
            writer.Execute(image)
