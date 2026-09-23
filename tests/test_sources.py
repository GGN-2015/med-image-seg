from __future__ import annotations

from pathlib import Path

from med_image_seg import ImageCollection, ImageSource, SourceKind


def test_nifti_uses_colocated_named_json(tmp_path: Path) -> None:
    image = tmp_path / "pelvis.nii.gz"
    image.write_bytes(b"nifti-test")

    source = ImageSource.from_path(image)

    assert source.kind == SourceKind.NIFTI
    assert source.annotation_path == tmp_path / "pelvis.med-image-seg.json"
    assert source.mask_path == tmp_path / "pelvis.med-image-seg-mask.nii.gz"


def test_dicom_file_and_directory_share_annotation(tmp_path: Path) -> None:
    dicom = tmp_path / "IM0001.dcm"
    dicom.write_bytes(b"dicom-test")

    from_file = ImageSource.from_path(dicom)
    from_directory = ImageSource.from_path(tmp_path)

    assert from_file.kind == SourceKind.DICOM
    assert from_file.path == tmp_path
    assert from_file.annotation_path == tmp_path / ".med-image-seg.json"
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
    (series / "other-output.nii.gz").write_bytes(b"other-generated-mask")
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
