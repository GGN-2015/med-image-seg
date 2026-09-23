from __future__ import annotations

from pathlib import Path

import numpy as np
import SimpleITK as sitk

from med_image_seg import MedicalMaskWriter, MedicalVolumeReader


def _write_test_nifti(path: Path) -> None:
    array = np.arange(4 * 5 * 6, dtype=np.float32).reshape(4, 5, 6)
    image = sitk.GetImageFromArray(array)
    image.SetSpacing((1.0, 1.0, 1.0))
    image.SetOrigin((1.0, 2.0, 3.0))
    sitk.WriteImage(image, str(path))


def _write_test_dicom_series(directory: Path) -> None:
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


def test_nifti_round_trip_uses_reader_and_preserves_mask_geometry(
    tmp_path: Path,
) -> None:
    source = tmp_path / "scan.nii.gz"
    _write_test_nifti(source)

    volume = MedicalVolumeReader(1.0).read(source)
    mask = np.zeros(volume.data.shape, dtype=np.uint8)
    mask[1:-1, 1:-1, 1:-1] = 1
    output = MedicalMaskWriter().write(tmp_path / "mask.nii.gz", mask, volume)
    written = sitk.ReadImage(str(output))

    assert volume.data.ndim == 3
    assert volume.spacing_mm == (1.0, 1.0, 1.0)
    assert written.GetSpacing() == volume.spacing_mm
    assert written.GetOrigin() == volume.origin_lps_mm
    assert written.GetSize() == mask.shape


def test_dicom_series_loads_through_required_reader(tmp_path: Path) -> None:
    directory = tmp_path / "dicom"
    _write_test_dicom_series(directory)

    volume = MedicalVolumeReader(1.0).read(directory)

    assert volume.data.ndim == 3
    assert volume.data.shape[2] >= 4
    assert volume.metadata["modality"] == "CT"
