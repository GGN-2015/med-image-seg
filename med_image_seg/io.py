"""Medical volume I/O delegated to ct_mri_dicom_nii_reader."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np
import SimpleITK as sitk
from ct_mri_dicom_nii_reader import BodyDataLoaderManager
from ct_mri_dicom_nii_reader.body_data.body_data_imp.dicom_to_hu_lps import (
    load_dicom_hu_lps,
)
from ct_mri_dicom_nii_reader.body_data.body_data_imp.nifti_to_lps import (
    load_nifti_lps,
)


@dataclass(frozen=True, slots=True)
class MedicalVolume:
    """A medical image on an isotropic L/P/S grid."""

    data: np.ndarray
    spacing_mm: tuple[float, float, float]
    origin_lps_mm: tuple[float, float, float]
    metadata: dict[str, Any]
    source: Path


def _nifti_safe_spacing(spacing_mm: tuple[float, float, float]) -> tuple[float, ...]:
    safe: list[float] = []
    for value in spacing_mm:
        serialized = np.float32(value)
        if float(serialized) > float(value):
            serialized = np.nextafter(serialized, np.float32(-np.inf), dtype=np.float32)
        safe.append(float(serialized))
    return tuple(safe)


class MedicalVolumeReader:
    """Read DICOM, NIfTI, or UBD through the dedicated reader package."""

    def __init__(self, spacing_mm: float = 0.8) -> None:
        self._spacing_mm = self._validate_spacing(spacing_mm)

    @staticmethod
    def _validate_spacing(spacing_mm: float) -> float:
        if not np.isfinite(spacing_mm) or spacing_mm <= 0:
            raise ValueError("spacing_mm must be a finite number greater than zero")
        return float(spacing_mm)

    @property
    def spacing_mm(self) -> float:
        return self._spacing_mm

    def read(
        self,
        path: str | Path,
        *,
        spacing_mm: float | None = None,
        interpolation: Literal["linear", "nearest"] = "linear",
    ) -> MedicalVolume:
        source = Path(path).expanduser().resolve()
        target_spacing = self._validate_spacing(
            self._spacing_mm if spacing_mm is None else spacing_mm
        )
        lower_name = source.name.lower()
        if source.is_dir() or lower_name.endswith(".dcm") or not source.suffix:
            directory = source if source.is_dir() else source.parent
            data, metadata = load_dicom_hu_lps(
                directory,
                target_spacing,
                require_ct=True,
                return_metadata=True,
            )
        elif lower_name.endswith((".nii", ".nii.gz")):
            data, metadata = load_nifti_lps(
                source,
                target_spacing,
                interpolation=interpolation,
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
        return MedicalVolume(
            data=np.asarray(data, dtype=np.float32),
            spacing_mm=tuple(float(value) for value in metadata["spacing_lps_mm"]),
            origin_lps_mm=tuple(float(value) for value in metadata["origin_lps_mm"]),
            metadata=dict(metadata),
            source=source,
        )


def load_volume(
    path: str | Path,
    spacing_mm: float = 0.8,
    *,
    interpolation: Literal["linear", "nearest"] = "linear",
) -> MedicalVolume:
    return MedicalVolumeReader(spacing_mm).read(path, interpolation=interpolation)


class MedicalMaskWriter:
    """Write binary masks with the loaded volume geometry."""

    def write(
        self,
        path: str | Path,
        mask: np.ndarray,
        reference: MedicalVolume,
    ) -> Path:
        return self.write_geometry(
            path,
            mask,
            spacing_mm=reference.spacing_mm,
            origin_lps_mm=reference.origin_lps_mm,
        )

    def write_geometry(
        self,
        path: str | Path,
        mask: np.ndarray,
        *,
        spacing_mm: tuple[float, float, float],
        origin_lps_mm: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> Path:
        output = Path(path).expanduser().resolve()
        array = np.asarray(mask, dtype=np.uint8)
        if array.ndim != 3:
            raise ValueError("mask must be a 3-D array")
        if not np.all((array == 0) | (array == 1)):
            raise ValueError("mask must contain only 0 and 1")
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.name.lower().endswith(".ubd.npz"):
            from ct_mri_dicom_nii_reader import BodyData

            if not np.allclose(spacing_mm, spacing_mm[0]):
                raise ValueError("UBD output requires isotropic spacing")
            body_data = BodyData()
            body_data.from_array(array, "mask", float(spacing_mm[0]))
            body_data.save(str(output))
            return output
        if not output.name.lower().endswith((".nii", ".nii.gz")):
            raise ValueError("output must end with .nii, .nii.gz, or .ubd.npz")
        image = sitk.GetImageFromArray(np.transpose(array, (2, 1, 0)))
        image.SetSpacing(_nifti_safe_spacing(spacing_mm))
        image.SetOrigin(tuple(float(value) for value in origin_lps_mm))
        image.SetDirection((1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0))
        sitk.WriteImage(image, str(output), useCompression=True)
        return output


def save_mask(
    path: str | Path,
    mask: np.ndarray,
    *,
    spacing_mm: tuple[float, float, float],
    origin_lps_mm: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> Path:
    return MedicalMaskWriter().write_geometry(
        path,
        mask,
        spacing_mm=spacing_mm,
        origin_lps_mm=origin_lps_mm,
    )


__all__ = [
    "MedicalMaskWriter",
    "MedicalVolume",
    "MedicalVolumeReader",
    "load_volume",
    "save_mask",
]
