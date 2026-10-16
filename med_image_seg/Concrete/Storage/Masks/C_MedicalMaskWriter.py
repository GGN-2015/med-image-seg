from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Storage.Masks.I_MedicalMaskWriter import I_MedicalMaskWriter

if TYPE_CHECKING:
    from ....Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
import os
import shutil
from tempfile import TemporaryDirectory
from typing import final

import numpy as np
import SimpleITK as sitk
from numpy.typing import NDArray


# 写出 NIfTI 或 UBD 掩码，保留物理几何并通过英文临时路径兼容中文目录。
@final
class C_MedicalMaskWriter(I_MedicalMaskWriter):
    # 使用参考影像的间距和原点保存掩码，确保输出几何与原影像一致。
    def write(
        self,
        path: str | I_FilePath,
        mask: NDArray[np.generic],
        reference: I_MedicalVolume,
    ) -> I_FilePath:
        return self.write_geometry(
            path,
            mask,
            spacing_mm=reference.getSpacingMm(),
            origin_lps_mm=reference.getOriginLpsMm(),
        )

    # 根据扩展名写出掩码，NIfTI 先写英文临时路径再复制到目标目录。
    def write_geometry(
        self,
        path: str | I_FilePath,
        mask: NDArray[np.generic],
        *,
        spacing_mm: tuple[float, float, float],
        origin_lps_mm: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> I_FilePath:
        from ..Paths.C_FilePath import C_FilePath
        from .C_NiftiPathPolicy import C_NiftiPathPolicy

        output = C_FilePath(path).expanduser().resolve()
        array = np.asarray(mask, dtype=np.uint8)
        if array.ndim != 3:
            raise ValueError("mask must be a 3-D array")
        if not np.all((array == 0) | (array == 1)):
            raise ValueError("mask must contain only 0 and 1")
        output.getParent().mkdir(parents=True, exist_ok=True)
        if output.getName().lower().endswith(".ubd.npz"):
            from ct_mri_dicom_nii_reader import BodyData

            if not np.allclose(spacing_mm, spacing_mm[0]):
                raise ValueError("UBD output requires isotropic spacing")
            body_data = BodyData()
            body_data.from_array(array, "mask", float(spacing_mm[0]))
            body_data.save(str(output))
            return output
        if not output.getName().lower().endswith((".nii", ".nii.gz")):
            raise ValueError("output must end with .nii, .nii.gz, or .ubd.npz")
        image = sitk.GetImageFromArray(np.transpose(array, (2, 1, 0)))
        image.SetSpacing(C_NiftiPathPolicy().nifti_safe_spacing(spacing_mm))
        image.SetOrigin(tuple(float(value) for value in origin_lps_mm))
        image.SetDirection((1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0))
        suffix = ".nii.gz" if output.getName().lower().endswith(".nii.gz") else ".nii"
        with C_NiftiPathPolicy().ascii_temporary_directory() as temporary_directory:
            temporary_output = C_FilePath(temporary_directory) / f"mask{suffix}"
            sitk.WriteImage(image, str(temporary_output), useCompression=True)
            with TemporaryDirectory(
                prefix=".med-image-seg-", dir=output.getParent()
            ) as destination_directory:
                destination = C_FilePath(destination_directory) / "mask.tmp"
                shutil.copyfile(temporary_output, destination)
                os.replace(destination, output)
        return output
