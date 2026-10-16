from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Storage.Masks.I_MedicalMaskReader import I_MedicalMaskReader

if TYPE_CHECKING:
    from ....Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
import gzip
import shutil
from itertools import product
from typing import final

import numpy as np
import SimpleITK as sitk
from numpy.typing import NDArray


# 读取 NIfTI 或 UBD 掩码，并按物理坐标对齐到参考影像网格。
@final
class C_MedicalMaskReader(I_MedicalMaskReader):
    # 委托掩码校验器检查三维数组并把非零标签转换为前景。
    def _binary_array(self, data: NDArray[np.generic]) -> NDArray[np.uint8]:
        from ...Algorithms.Masks.C_BinaryMaskValidator import C_BinaryMaskValidator

        return C_BinaryMaskValidator().validate(data)

    # 读取 NIfTI 或 UBD 掩码，以最近邻对齐参考网格并检查物理覆盖范围。
    def read(
        self, path: str | I_FilePath, reference: I_MedicalVolume
    ) -> NDArray[np.uint8]:
        from ...Numerics.Arrays.C_ArrayFactory import C_ArrayFactory
        from ..Paths.C_FilePath import C_FilePath
        from .C_NiftiPathPolicy import C_NiftiPathPolicy

        source = C_FilePath(path).expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(f"external mask not found: {source}")
        if source.getName().lower().endswith(".ubd.npz"):
            with np.load(source, allow_pickle=False) as archive:
                data = self._binary_array(archive["body_data"])
                spacing = float(archive["mmpd"].item())
            if not np.isfinite(spacing) or spacing <= 0:
                raise ValueError("UBD mask spacing must be finite and positive")
            mask_extent = np.asarray(data.shape) * spacing
            image_extent = (
                np.asarray(reference.getData().shape) * reference.getSpacingMm()
            )
            tolerance = max(spacing, *reference.getSpacingMm()) + 1e-05
            if not np.allclose(mask_extent, image_extent, rtol=1e-05, atol=tolerance):
                raise ValueError("UBD mask field of view does not match the image")
            image = sitk.GetImageFromArray(np.transpose(data, (2, 1, 0)))
            image.SetSpacing((spacing,) * 3)
            image.SetOrigin(
                tuple(
                    (
                        origin - target_spacing / 2 + spacing / 2
                        for origin, target_spacing in zip(
                            reference.getOriginLpsMm(),
                            reference.getSpacingMm(),
                            strict=True,
                        )
                    )
                )
            )
        elif source.getName().lower().endswith((".nii", ".nii.gz")):
            with source.open("rb") as header:
                compressed = header.read(2) == b"\x1f\x8b"
            with C_NiftiPathPolicy().ascii_temporary_directory() as directory:
                temporary = C_FilePath(directory) / "external-mask.nii"
                if compressed:
                    with (
                        gzip.open(source, "rb") as input_file,
                        temporary.open("wb") as output_file,
                    ):
                        shutil.copyfileobj(input_file, output_file)
                else:
                    shutil.copyfile(source, temporary)
                original = sitk.ReadImage(str(temporary))
            if (
                original.GetDimension() != 3
                or original.GetNumberOfComponentsPerPixel() != 1
            ):
                raise ValueError("external NIfTI mask must be a scalar 3-D image")
            data = self._binary_array(sitk.GetArrayFromImage(original))
            image = sitk.GetImageFromArray(data)
            image.CopyInformation(original)
        else:
            raise ValueError("external mask must end with .nii, .nii.gz, or .ubd.npz")
        corners = np.asarray(
            [
                image.TransformContinuousIndexToPhysicalPoint(list(corner))
                for corner in product(*[(-0.5, size - 0.5) for size in image.GetSize()])
            ]
        )
        reference_lower = (
            np.asarray(reference.getOriginLpsMm())
            - np.asarray(reference.getSpacingMm()) / 2
        )
        reference_upper = (
            reference_lower
            + np.asarray(reference.getData().shape) * reference.getSpacingMm()
        )
        if np.any(corners.max(axis=0) <= reference_lower) or np.any(
            corners.min(axis=0) >= reference_upper
        ):
            raise ValueError(
                "external mask does not overlap the image in physical space"
            )
        resampler = sitk.ResampleImageFilter()
        resampler.SetSize([int(size) for size in reference.getData().shape])
        resampler.SetOutputSpacing(reference.getSpacingMm())
        resampler.SetOutputOrigin(reference.getOriginLpsMm())
        resampler.SetOutputDirection((1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0))
        resampler.SetTransform(sitk.Transform(3, sitk.sitkIdentity))
        resampler.SetInterpolator(sitk.sitkNearestNeighbor)
        resampler.SetDefaultPixelValue(0)
        resampler.SetOutputPixelType(sitk.sitkUInt8)
        aligned = resampler.Execute(image)
        return C_ArrayFactory().wrap(
            np.ascontiguousarray(
                np.transpose(sitk.GetArrayFromImage(aligned), (2, 1, 0))
            )
        )
