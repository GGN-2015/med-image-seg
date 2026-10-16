from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pytest
import SimpleITK as sitk

import med_image_seg.io as medical_io
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


@pytest.mark.parametrize("suffix", [".nii", ".nii.gz"])
@pytest.mark.parametrize(
    ("directory", "filename"),
    [("ascii", "mask"), ("中文目录", "mask"), ("ascii", "掩码"), ("中文目录", "掩码")],
)
def test_nifti_export_uses_ascii_staging_and_preserves_geometry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    suffix: str,
    directory: str,
    filename: str,
) -> None:
    output = tmp_path / directory / f"{filename}{suffix}"
    output.parent.mkdir()
    output.write_bytes(b"previous mask")
    mask = np.zeros((4, 5, 6), dtype=np.uint8)
    mask[1:3, 2:4, 1:5] = 1
    spacing = (0.8, 0.8, 0.8)
    origin = (-10.0, 20.0, 30.0)
    temporary_paths: list[Path] = []
    written_bytes: list[bytes] = []
    write_image = sitk.WriteImage

    def record_write(image: sitk.Image, path: str, *, useCompression: bool) -> None:
        temporary = Path(path)
        assert str(temporary).isascii()
        assert temporary.name == f"mask{suffix}"
        assert temporary != output
        assert useCompression
        temporary_paths.append(temporary)
        write_image(image, path, useCompression=useCompression)
        written = sitk.ReadImage(path)
        assert written.GetSize() == mask.shape
        assert written.GetSpacing() == pytest.approx(spacing)
        assert written.GetOrigin() == origin
        assert written.GetDirection() == (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
        np.testing.assert_array_equal(
            np.transpose(sitk.GetArrayFromImage(written), (2, 1, 0)), mask
        )
        written_bytes.append(temporary.read_bytes())

    monkeypatch.setattr(medical_io.sitk, "WriteImage", record_write)

    result = MedicalMaskWriter().write_geometry(
        output, mask, spacing_mm=spacing, origin_lps_mm=origin
    )

    assert result == output.resolve()
    assert len(temporary_paths) == 1
    assert output.read_bytes() == written_bytes[0]
    assert not temporary_paths[0].parent.exists()
    assert list(output.parent.iterdir()) == [output]


@pytest.mark.parametrize("failed_step", ["write", "copy", "replace"])
@pytest.mark.parametrize("existing_output", [False, True])
def test_failed_nifti_export_preserves_output_and_cleans_temporary_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failed_step: str,
    existing_output: bool,
) -> None:
    output = tmp_path / "中文目录" / "掩码.nii.gz"
    output.parent.mkdir()
    if existing_output:
        output.write_bytes(b"previous mask")
    temporary_paths: list[Path] = []

    def fail_write(image: sitk.Image, path: str, *, useCompression: bool) -> None:
        temporary = Path(path)
        temporary_paths.append(temporary)
        temporary.write_bytes(b"temporary mask")
        if failed_step == "write":
            raise RuntimeError("simulated export failure")

    def fail_copy(source: Path, destination: Path) -> None:
        temporary_paths.append(destination)
        destination.write_bytes(b"partial copy")
        if failed_step == "copy":
            raise OSError("simulated export failure")

    def fail_replace(source: Path, destination: Path) -> None:
        raise OSError("simulated export failure")

    monkeypatch.setattr(medical_io.sitk, "WriteImage", fail_write)
    monkeypatch.setattr(medical_io.shutil, "copyfile", fail_copy)
    monkeypatch.setattr(medical_io.os, "replace", fail_replace)

    with pytest.raises((RuntimeError, OSError), match="simulated export failure"):
        MedicalMaskWriter().write_geometry(
            output, np.ones((2, 3, 4), dtype=np.uint8), spacing_mm=(1.0, 1.0, 1.0)
        )

    if existing_output:
        assert output.read_bytes() == b"previous mask"
    else:
        assert not output.exists()
    assert temporary_paths
    assert all(not temporary.parent.exists() for temporary in temporary_paths)
    assert list(output.parent.iterdir()) == ([output] if existing_output else [])


@pytest.mark.parametrize("default_kind", ["unicode", "unwritable"])
def test_ascii_temporary_directory_falls_back_from_unsuitable_default(
    monkeypatch: pytest.MonkeyPatch, default_kind: str
) -> None:
    temporary_directory = medical_io.TemporaryDirectory
    with medical_io._ascii_temporary_directory() as ascii_directory:
        root = Path(ascii_directory)
        default = root / ("中文临时目录" if default_kind == "unicode" else "unwritable")
        default.mkdir()

        def create_directory(*, prefix: str, dir: Path) -> TemporaryDirectory[str]:
            assert dir != default or default_kind != "unicode"
            if dir == default:
                raise PermissionError("simulated unwritable directory")
            return temporary_directory(prefix=prefix, dir=dir)

        with monkeypatch.context() as patch:
            patch.chdir(root)
            patch.setattr(medical_io, "gettempdir", lambda: str(default))
            patch.setattr(medical_io, "TemporaryDirectory", create_directory)
            with medical_io._ascii_temporary_directory() as directory:
                temporary = Path(directory)
                assert str(temporary).isascii()
                assert temporary.parent == root
            assert not temporary.exists()


def test_ascii_temporary_directory_reports_no_usable_directory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def deny_directory(*, prefix: str, dir: Path) -> None:
        raise PermissionError("simulated unwritable directory")

    monkeypatch.setattr(medical_io, "TemporaryDirectory", deny_directory)

    with pytest.raises(OSError, match="writable ASCII-only temporary directory"):
        medical_io._ascii_temporary_directory()


def test_ubd_round_trip_supports_unicode_paths_and_preserves_mask(
    tmp_path: Path,
) -> None:
    output = tmp_path / "中文目录" / "掩码.ubd.npz"
    mask = np.zeros((4, 5, 6), dtype=np.uint8)
    mask[1:3, 2:4, 1:5] = 1

    result = MedicalMaskWriter().write_geometry(
        output, mask, spacing_mm=(0.8, 0.8, 0.8)
    )
    loaded = MedicalVolumeReader(0.8).read(output)

    assert result == output.resolve()
    assert loaded.spacing_mm == (0.8, 0.8, 0.8)
    assert loaded.metadata["modality"] == "MASK"
    np.testing.assert_array_equal(loaded.data, mask)
    with np.load(output, allow_pickle=False) as archive:
        assert archive["body_data"].dtype == np.uint8
        assert archive["image_type"].item() == "mask"
        assert archive["mmpd"].item() == 0.8


def test_ubd_export_rejects_anisotropic_spacing(tmp_path: Path) -> None:
    output = tmp_path / "mask.ubd.npz"

    with pytest.raises(ValueError, match="UBD output requires isotropic spacing"):
        MedicalMaskWriter().write_geometry(
            output, np.ones((2, 3, 4), dtype=np.uint8), spacing_mm=(0.8, 0.8, 1.0)
        )

    assert not output.exists()


def test_dicom_series_loads_through_required_reader(tmp_path: Path) -> None:
    directory = tmp_path / "dicom"
    _write_test_dicom_series(directory)

    volume = MedicalVolumeReader(1.0).read(directory)

    assert volume.data.ndim == 3
    assert volume.data.shape[2] >= 4
    assert volume.metadata["modality"] == "CT"
