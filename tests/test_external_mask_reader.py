from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pytest
import SimpleITK as sitk

from med_image_seg.io import MedicalMaskReader, MedicalMaskWriter, MedicalVolume


def _reference(tmp_path, shape=(6, 5, 4), spacing=(1.0, 1.0, 1.0)):
    return MedicalVolume(
        data=np.zeros(shape, dtype=np.float32),
        spacing_mm=spacing,
        origin_lps_mm=(10.0, -20.0, 30.0),
        metadata={},
        source=tmp_path / "scan.nii",
    )


def _write(path, data, reference, *, spacing=None, origin=None, direction=None):
    image = sitk.GetImageFromArray(np.transpose(data, (2, 1, 0)))
    image.SetSpacing(spacing or reference.spacing_mm)
    image.SetOrigin(origin or reference.origin_lps_mm)
    if direction is not None:
        image.SetDirection(direction)
    sitk.WriteImage(image, str(path))


@pytest.mark.parametrize("suffix", [".nii", ".nii.gz", ".ubd.npz"])
@pytest.mark.parametrize("empty", [False, True])
def test_external_mask_round_trip_matches_reference_grid(tmp_path, suffix, empty):
    reference = _reference(tmp_path, spacing=(0.8, 0.8, 0.8))
    mask = np.zeros(reference.data.shape, dtype=np.uint8)
    if not empty:
        mask[1:4, 2:4, 1] = 1
        mask[4, 1, 3] = 1
    path = MedicalMaskWriter().write(tmp_path / f"mask{suffix}", mask, reference)
    result = MedicalMaskReader().read(path, reference)
    np.testing.assert_array_equal(result, mask)
    assert result.dtype == np.uint8
    assert result.flags.c_contiguous


def test_external_mask_keeps_all_nonzero_labels(tmp_path):
    reference = _reference(tmp_path)
    data = np.zeros(reference.data.shape, dtype=np.float32)
    data[1, 2, 1] = 7
    data[3, 2, 1] = -3
    data[4, 1, 3] = 0.01
    path = tmp_path / "labels.nii.gz"
    _write(path, data, reference)
    np.testing.assert_array_equal(MedicalMaskReader().read(path, reference), data != 0)


def test_nifti_resamples_nearest_neighbor_using_physical_origin_and_spacing(tmp_path):
    reference = _reference(tmp_path)
    data = np.zeros((3, 5, 4), dtype=np.float32)
    data[1, 2, 1] = 7
    path = tmp_path / "coarse.nii.gz"
    _write(path, data, reference, spacing=(2.0, 1.0, 1.0), origin=(10.25, -20.0, 30.0))
    result = MedicalMaskReader().read(path, reference)
    expected = np.zeros(reference.data.shape, dtype=np.uint8)
    expected[2:4, 2, 1] = 1
    np.testing.assert_array_equal(result, expected)


def test_nifti_direction_flip_is_correctly_reoriented_to_lps(tmp_path):
    reference = _reference(tmp_path)
    data = np.zeros(reference.data.shape, dtype=np.uint8)
    data[1, 2, 1] = 1
    path = tmp_path / "flipped.nii"
    _write(
        path,
        data,
        reference,
        origin=(15.0, -20.0, 30.0),
        direction=(-1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0),
    )
    np.testing.assert_array_equal(MedicalMaskReader().read(path, reference), data[::-1])


def test_nifti_axis_permutation_matches_reference_coordinates(tmp_path):
    reference = _reference(tmp_path)
    data = np.zeros((5, 6, 4), dtype=np.uint8)
    data[2, 4, 1] = 1
    path = tmp_path / "permuted.nii.gz"
    _write(
        path, data, reference, direction=(0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)
    )
    expected = np.zeros(reference.data.shape, dtype=np.uint8)
    expected[4, 2, 1] = 1
    np.testing.assert_array_equal(MedicalMaskReader().read(path, reference), expected)


def test_partial_nifti_field_of_view_is_zero_padded_on_reference_grid(tmp_path):
    reference = _reference(tmp_path)
    path = tmp_path / "partial.nii"
    _write(
        path, np.ones((2, 2, 2), dtype=np.uint8), reference, origin=(12.0, -19.0, 31.0)
    )
    expected = np.zeros(reference.data.shape, dtype=np.uint8)
    expected[2:4, 1:3, 1:3] = 1
    np.testing.assert_array_equal(MedicalMaskReader().read(path, reference), expected)


def test_nonoverlapping_nifti_is_rejected_instead_of_silently_misaligning(tmp_path):
    reference = _reference(tmp_path)
    path = tmp_path / "unrelated.nii"
    _write(
        path,
        np.ones(reference.data.shape, dtype=np.uint8),
        reference,
        origin=(1000.0, 1000.0, 1000.0),
    )
    with pytest.raises(ValueError, match="does not overlap"):
        MedicalMaskReader().read(path, reference)


def test_ubd_resampling_aligns_lower_voxel_support_edges(tmp_path):
    reference = _reference(tmp_path, shape=(6, 4, 4))
    data = np.zeros((3, 2, 2), dtype=np.uint8)
    data[0, 0, 0] = 3
    path = tmp_path / "coarse.ubd.npz"
    np.savez_compressed(path, body_data=data, mmpd=2.0)
    expected = np.zeros(reference.data.shape, dtype=np.uint8)
    expected[:2, :2, :2] = 1
    np.testing.assert_array_equal(MedicalMaskReader().read(path, reference), expected)


def test_ubd_mismatched_field_of_view_is_rejected(tmp_path):
    reference = _reference(tmp_path)
    path = tmp_path / "unrelated.ubd.npz"
    np.savez_compressed(path, body_data=np.ones((30, 30, 30)), mmpd=2.0)
    with pytest.raises(ValueError, match="field of view"):
        MedicalMaskReader().read(path, reference)


@pytest.mark.parametrize("spacing", [0.0, -1.0, np.nan, np.inf])
def test_ubd_invalid_spacing_is_rejected(tmp_path, spacing):
    reference = _reference(tmp_path)
    path = tmp_path / "invalid.ubd.npz"
    np.savez_compressed(path, body_data=reference.data, mmpd=spacing)
    with pytest.raises(ValueError, match="spacing"):
        MedicalMaskReader().read(path, reference)


@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf])
def test_nonfinite_decoded_nifti_labels_are_rejected(tmp_path, monkeypatch, value):
    reference = _reference(tmp_path)
    path = tmp_path / "invalid.nii"
    data = reference.data.copy()
    data[1, 2, 1] = value
    path.write_bytes(b"mocked NIfTI reader")
    image = sitk.GetImageFromArray(np.transpose(data, (2, 1, 0)))
    image.SetOrigin(reference.origin_lps_mm)
    monkeypatch.setattr(sitk, "ReadImage", lambda _path: image)
    with pytest.raises(ValueError, match="finite"):
        MedicalMaskReader().read(path, reference)


@pytest.mark.parametrize(
    "data",
    [
        np.zeros((2, 3)),
        np.zeros((2, 0, 3)),
        np.ones((6, 5, 4), dtype=complex),
        np.full((6, 5, 4), "label"),
    ],
)
def test_invalid_ubd_mask_arrays_are_rejected(tmp_path, data):
    reference = _reference(tmp_path)
    path = tmp_path / "invalid.ubd.npz"
    np.savez_compressed(path, body_data=data, mmpd=1.0)
    with pytest.raises(ValueError):
        MedicalMaskReader().read(path, reference)


@pytest.mark.parametrize("suffix", [".nii", ".nii.gz"])
def test_unicode_nifti_is_read_through_ascii_staging_and_cleaned_up(
    tmp_path, monkeypatch, suffix
):
    reference = _reference(tmp_path)
    original = tmp_path / f"mask{suffix}"
    _write(original, np.ones(reference.data.shape, dtype=np.uint8), reference)
    directory = tmp_path / "中文掩码"
    directory.mkdir()
    path = directory / f"分割{suffix}"
    shutil.copyfile(original, path)
    read = sitk.ReadImage
    staged = []

    def tracked(filename):
        assert str(filename).isascii()
        staged.append(filename)
        return read(filename)

    monkeypatch.setattr(sitk, "ReadImage", tracked)
    result = MedicalMaskReader().read(path, reference)
    assert result.all()
    assert staged
    assert all(not Path(filename).exists() for filename in staged)


def test_failed_nifti_read_cleans_up_ascii_staging(tmp_path, monkeypatch):
    reference = _reference(tmp_path)
    path = tmp_path / "invalid.nii"
    path.write_bytes(b"not a NIfTI file")
    staged = []

    def fail(filename):
        staged.append(filename)
        raise RuntimeError("invalid image")

    monkeypatch.setattr(sitk, "ReadImage", fail)
    with pytest.raises(RuntimeError, match="invalid image"):
        MedicalMaskReader().read(path, reference)
    assert all(not Path(filename).exists() for filename in staged)
