from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from ....Abstract.Storage.Volumes.I_MutableMedicalVolumeReader import (
    I_MutableMedicalVolumeReader,
)

if TYPE_CHECKING:
    from ....Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
import json
from typing import final

import numpy as np
from ct_mri_dicom_nii_reader import BodyDataLoaderManager
from ct_mri_dicom_nii_reader.body_data.body_data_imp.dicom_to_hu_lps import (
    load_dicom_hu_lps,
)
from ct_mri_dicom_nii_reader.body_data.body_data_imp.nifti_to_lps import load_nifti_lps


# 适配医学影像读取库，把输入重采样到指定间距的 LPS 网格。
@final
class C_MedicalVolumeReader(I_MutableMedicalVolumeReader):
    # 返回读取器使用的标注网格间距。
    def getInternalSpacingMm(self) -> float:
        return self._state_spacing_mm

    # 记录读取器使用的标注网格间距。
    def setInternalSpacingMm(self, value: float) -> None:
        self._state_spacing_mm = value

    # 校验并保存目标标注网格间距。
    def __init__(self, spacing_mm: float = 0.8) -> None:
        self.setInternalSpacingMm(self._validate_spacing(spacing_mm))

    # 委托间距校验器拒绝非有限值和非正数。
    def _validate_spacing(self, spacing_mm: float) -> float:
        from ...Algorithms.Validation.C_SpacingValidator import C_SpacingValidator

        return C_SpacingValidator().validate(spacing_mm)

    # 返回 LPS 网格间距，单位为毫米。
    def getSpacingMm(self) -> float:
        return self.getInternalSpacingMm()

    # 通过影像读取库加载输入，并重采样为指定间距的 LPS 体素和几何信息。
    def read(
        self,
        path: str | I_FilePath,
        *,
        spacing_mm: float | None = None,
        interpolation: Literal["linear", "nearest"] = "linear",
    ) -> I_MedicalVolume:
        from ...Domain.Imaging.C_MedicalVolume import C_MedicalVolume
        from ...Domain.Imaging.C_Metadata import C_Metadata
        from ..Paths.C_FilePath import C_FilePath

        source = C_FilePath(path).expanduser().resolve()
        target_spacing = self._validate_spacing(
            self.getInternalSpacingMm() if spacing_mm is None else spacing_mm
        )
        lower_name = source.getName().lower()
        if source.is_dir() or lower_name.endswith(".dcm") or (not source.getSuffix()):
            directory = source if source.is_dir() else source.getParent()
            data, metadata = load_dicom_hu_lps(
                str(directory), target_spacing, require_ct=True, return_metadata=True
            )
        elif lower_name.endswith((".nii", ".nii.gz")):
            data, metadata = load_nifti_lps(
                str(source), target_spacing, interpolation=interpolation
            )
        elif lower_name.endswith(".ubd.npz"):
            body_data = BodyDataLoaderManager().load_file(
                str(source), mmpd=target_spacing
            )
            data = body_data.to_numpy(copy=False)
            stored_spacing = float(body_data.get_mmpd())
            metadata = {
                "axis_order": ("L", "P", "S"),
                "shape_lps": body_data.get_size(),
                "spacing_lps_mm": (stored_spacing,) * 3,
                "origin_lps_mm": (0.0, 0.0, 0.0),
                "modality": (body_data.get_type() or "UNKNOWN").upper(),
            }
        else:
            raise ValueError(
                "unsupported image; expected DICOM, .nii, .nii.gz, or .ubd.npz"
            )
        document = C_Metadata(json.dumps(dict(metadata), default=np.ndarray.tolist))
        return C_MedicalVolume(
            data=np.asarray(data, dtype=np.float32),
            spacing_mm=(
                document.getNumber("spacing_lps_mm", 0),
                document.getNumber("spacing_lps_mm", 1),
                document.getNumber("spacing_lps_mm", 2),
            ),
            origin_lps_mm=(
                document.getNumber("origin_lps_mm", 0),
                document.getNumber("origin_lps_mm", 1),
                document.getNumber("origin_lps_mm", 2),
            ),
            metadata=document,
            source=source,
        )
