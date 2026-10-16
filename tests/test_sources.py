from __future__ import annotations

from pathlib import Path

import pytest

from med_image_seg import ImageCollection, ImageSource, SourceKind


@pytest.mark.parametrize("suffix", [".nii", ".nii.gz", ".ubd.npz"])
def test_volume_file_uses_colocated_outputs(tmp_path: Path, suffix: str) -> None:
    image = tmp_path / f"pelvis{suffix}"
    image.write_bytes(b"nifti-test")

    source = ImageSource.from_path(image)

    assert source.kind == (SourceKind.UBD if suffix == ".ubd.npz" else SourceKind.NIFTI)
    assert source.annotation_path == tmp_path / "pelvis.med-image-seg.json"
    assert source.mask_path == tmp_path / "pelvis.med-image-seg-mask.nii.gz"
    assert source.ubd_mask_path == tmp_path / "pelvis.med-image-seg-mask.ubd.npz"


def test_dicom_file_and_directory_share_annotation(tmp_path: Path) -> None:
    dicom = tmp_path / "IM0001.dcm"
    dicom.write_bytes(b"dicom-test")

    from_file = ImageSource.from_path(dicom)
    from_directory = ImageSource.from_path(tmp_path)

    assert from_file.kind == SourceKind.DICOM
    assert from_file.path == tmp_path
    assert from_file.annotation_path == tmp_path / ".med-image-seg.json"
    assert from_file.mask_path == tmp_path / "med-image-seg-mask.nii.gz"
    assert from_file.ubd_mask_path == tmp_path / "med-image-seg-mask.ubd.npz"
    assert from_file.ubd_mask_path == from_directory.ubd_mask_path
    assert from_file.fingerprint == from_directory.fingerprint


def test_dicom_outputs_do_not_change_source_fingerprint(tmp_path: Path) -> None:
    series = tmp_path / "dicom"
    series.mkdir()
    (series / "0001.dcm").write_bytes(b"dicom-1")
    (series / "0002.dcm").write_bytes(b"dicom-2")
    before = ImageSource.from_path(series)

    before.annotation_path.write_text("{}", encoding="utf-8")
    Path(f"{before.annotation_path}.bak").write_text("{}", encoding="utf-8")
    before.mask_path.write_bytes(b"generated-mask")
    before.ubd_mask_path.write_bytes(b"generated-ubd-mask")
    (series / "other-output.nii.gz").write_bytes(b"other-generated-mask")
    (series / "other-output.ubd.npz").write_bytes(b"other-generated-ubd-mask")
    (series / "metadata.json").write_text("{}", encoding="utf-8")
    after = ImageSource.from_path(series)

    assert after.fingerprint == before.fingerprint
    assert after.source_id == before.source_id
    assert "2 files" in after.display_name


def test_collection_deduplicates_sources(tmp_path: Path) -> None:
    image = tmp_path / "scan.nii"
    image.write_bytes(b"image")

    collection = ImageCollection([image, image])

    assert len(collection) == 1


@pytest.mark.parametrize("suffix", [".nii", ".nii.gz", ".ubd.npz"])
@pytest.mark.parametrize("index", [0, 1, 23, 2**80])
def test_numbered_annotation_paths_preserve_base_and_directory(tmp_path, suffix, index):
    image = tmp_path / f"扫描.复查{suffix}"
    image.write_bytes(b"image")
    source = ImageSource.from_path(image)
    number = "" if index == 0 else f"-{index}"
    assert source.annotation_path_for_index(index) == (
        tmp_path / f"扫描.复查.med-image-seg{number}.json"
    )
    assert source.annotation_path_for_index(0) == source.annotation_path


def test_numbered_dicom_annotations_do_not_affect_fingerprint(tmp_path):
    (tmp_path / "0001.dcm").write_bytes(b"dicom")
    source = ImageSource.from_path(tmp_path)
    for index in (1, 12):
        path = source.annotation_path_for_index(index)
        assert path.name == f".med-image-seg-{index}.json"
        for suffix in ("", ".bak", ".tmp", ".bak.tmp"):
            Path(f"{path}{suffix}").write_text("{}", encoding="utf-8")
    after = ImageSource.from_path(tmp_path)
    assert after.fingerprint == source.fingerprint
    assert "1 files" in after.display_name


@pytest.mark.parametrize("index, error", [(-1, ValueError), (1.5, TypeError)])
def test_annotation_path_rejects_invalid_indices(tmp_path, index, error):
    image = tmp_path / "scan.nii"
    image.write_bytes(b"image")
    source = ImageSource.from_path(image)
    with pytest.raises(error):
        source.annotation_path_for_index(index)
