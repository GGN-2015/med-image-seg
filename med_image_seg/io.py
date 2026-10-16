"""Medical volume I/O delegated to ct_mri_dicom_nii_reader."""

from __future__ import annotations

import gzip
import os
import shutil
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from tempfile import TemporaryDirectory, gettempdir
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


def _ascii_temporary_directory() -> TemporaryDirectory[str]:
    directories = [Path(gettempdir()), Path.cwd()]
    if os.name == "nt":
        directories.append(Path(os.environ.get("SYSTEMROOT", r"C:\Windows")) / "Temp")
    for directory in directories:
        try:
            directory = directory.resolve()
            if not str(directory).isascii():
                continue
            return TemporaryDirectory(prefix="med-image-seg-", dir=directory)
        except OSError:
            continue
    raise OSError(
        "NIfTI I/O requires a writable ASCII-only temporary directory; "
        "set TMPDIR, TEMP, or TMP to an ASCII-only path."
    )


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
        suffix = ".nii.gz" if output.name.lower().endswith(".nii.gz") else ".nii"
        with _ascii_temporary_directory() as temporary_directory:
            temporary_output = Path(temporary_directory) / f"mask{suffix}"
            sitk.WriteImage(image, str(temporary_output), useCompression=True)
            with TemporaryDirectory(
                prefix=".med-image-seg-", dir=output.parent
            ) as destination_directory:
                destination = Path(destination_directory) / "mask.tmp"
                shutil.copyfile(temporary_output, destination)
                os.replace(destination, output)
        return output


class MedicalMaskReader:
    """Read an external mask directly onto the reference image's L/P/S grid."""

    @staticmethod
    def _binary_array(data: np.ndarray) -> np.ndarray:
        if data.ndim != 3 or any(size == 0 for size in data.shape):
            raise ValueError("external mask must be a nonempty 3-D array")
        if data.dtype.kind not in "buif" or not np.isfinite(data).all():
            raise ValueError("external mask must contain finite real numeric values")
        return np.asarray(data != 0, dtype=np.uint8)

    def read(self, path: str | Path, reference: MedicalVolume) -> np.ndarray:
        source = Path(path).expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(f"external mask not found: {source}")
        if source.name.lower().endswith(".ubd.npz"):
            with np.load(source, allow_pickle=False) as archive:
                data = self._binary_array(archive["body_data"])
                spacing = float(archive["mmpd"].item())
            if not np.isfinite(spacing) or spacing <= 0:
                raise ValueError("UBD mask spacing must be finite and positive")
            mask_extent = np.asarray(data.shape) * spacing
            image_extent = np.asarray(reference.data.shape) * reference.spacing_mm
            tolerance = max(spacing, *reference.spacing_mm) + 1e-5
            if not np.allclose(mask_extent, image_extent, rtol=1e-5, atol=tolerance):
                raise ValueError("UBD mask field of view does not match the image")
            image = sitk.GetImageFromArray(np.transpose(data, (2, 1, 0)))
            image.SetSpacing((spacing,) * 3)
            image.SetOrigin(
                tuple(
                    origin - target_spacing / 2 + spacing / 2
                    for origin, target_spacing in zip(
                        reference.origin_lps_mm, reference.spacing_mm, strict=True
                    )
                )
            )
        elif source.name.lower().endswith((".nii", ".nii.gz")):
            with source.open("rb") as header:
                compressed = header.read(2) == b"\x1f\x8b"
            with _ascii_temporary_directory() as directory:
                temporary = Path(directory) / "external-mask.nii"
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
            np.asarray(reference.origin_lps_mm) - np.asarray(reference.spacing_mm) / 2
        )
        reference_upper = (
            reference_lower + np.asarray(reference.data.shape) * reference.spacing_mm
        )
        if np.any(corners.max(axis=0) <= reference_lower) or np.any(
            corners.min(axis=0) >= reference_upper
        ):
            raise ValueError(
                "external mask does not overlap the image in physical space"
            )
        resampler = sitk.ResampleImageFilter()
        resampler.SetSize([int(size) for size in reference.data.shape])
        resampler.SetOutputSpacing(reference.spacing_mm)
        resampler.SetOutputOrigin(reference.origin_lps_mm)
        resampler.SetOutputDirection((1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0))
        resampler.SetTransform(sitk.Transform(3, sitk.sitkIdentity))
        resampler.SetInterpolator(sitk.sitkNearestNeighbor)
        resampler.SetDefaultPixelValue(0)
        resampler.SetOutputPixelType(sitk.sitkUInt8)
        aligned = resampler.Execute(image)
        return np.ascontiguousarray(
            np.transpose(sitk.GetArrayFromImage(aligned), (2, 1, 0))
        )


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
    "MedicalMaskReader",
    "MedicalMaskWriter",
    "MedicalVolume",
    "MedicalVolumeReader",
    "load_volume",
    "save_mask",
]
