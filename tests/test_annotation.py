from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from med_image_seg import AnnotationProject, MedicalVolume, PolygonAnnotation


def _volume() -> MedicalVolume:
    return MedicalVolume(
        data=np.zeros((20, 18, 5), dtype=np.float32),
        spacing_mm=(0.8, 0.8, 0.8),
        origin_lps_mm=(1.0, 2.0, 3.0),
        metadata={},
        source=Path("anonymous"),
    )


def _project() -> AnnotationProject:
    return AnnotationProject.create(
        image_id="IMAGE-TEST",
        source_fingerprint="fingerprint",
        volume=_volume(),
    )


def test_delete_targets_last_edited_polygon_not_last_list_item() -> None:
    project = _project()
    first = PolygonAnnotation(points=((1, 1), (6, 1), (3, 6)))
    second = PolygonAnnotation(points=((10, 1), (15, 1), (12, 6)))
    project.add_polygon(2, first)
    project.add_polygon(2, second)
    project.replace_polygon(2, 0, ((2, 2), (7, 2), (4, 7)))

    deleted = project.delete_last_edited_polygon(2)

    assert deleted is not None
    assert deleted.points[0] == (2.0, 2.0)
    assert project.annotation(2).polygons[0].points == second.points


def test_save_is_atomic_and_recovers_from_backup(tmp_path: Path) -> None:
    project = _project()
    project.add_polygon(2, PolygonAnnotation(points=((1, 1), (6, 1), (3, 6))))
    path = project.save(tmp_path / "scan.med-image-seg.json")
    project.replace_polygon(2, 0, ((2, 2), (7, 2), (4, 7)))
    project.save(path)

    assert Path(f"{path}.bak").is_file()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert "source_path" not in payload
    assert payload["edit_counter"] == 2

    path.write_text("broken", encoding="utf-8")
    recovered = AnnotationProject.load(path)
    assert recovered.annotation(2).polygons[0].points[0] == (1.0, 1.0)


def test_interpolation_between_keyframes() -> None:
    project = _project()
    project.add_polygon(
        0,
        PolygonAnnotation(points=((2, 4), (8, 4), (8, 12), (2, 12))),
    )
    project.add_polygon(
        4,
        PolygonAnnotation(points=((6, 4), (12, 4), (12, 12), (6, 12))),
    )

    preview = project.interpolated_plane(2)
    mask = project.to_mask()

    assert preview is not None and preview.any()
    assert np.array_equal(mask[:, :, 2], preview.T)


def test_force_empty_overrides_polygons_and_interpolation() -> None:
    project = _project()
    polygon = PolygonAnnotation(points=((2, 4), (12, 4), (12, 14), (2, 14)))
    project.add_polygon(0, polygon)
    project.add_polygon(4, polygon)

    assert project.interpolated_plane(2).any()
    project.set_force_empty(2, True)

    assert project.interpolated_plane(2) is None
    assert not project.to_mask()[:, :, 2].any()
    assert project.annotation(2).force_empty


def test_adding_polygon_clears_force_empty() -> None:
    project = _project()
    project.set_force_empty(2, True)

    project.add_polygon(
        2,
        PolygonAnnotation(points=((2, 4), (12, 4), (12, 14), (2, 14))),
    )

    assert not project.annotation(2).force_empty
    assert project.to_mask(interpolate=False)[:, :, 2].any()


def test_manual_and_prototype_sources_are_combined_as_a_union() -> None:
    project = _project()
    project.add_polygon(
        2,
        PolygonAnnotation(
            points=((1, 2), (9, 2), (9, 12), (1, 12)),
            source="prototype",
        ),
    )
    project.add_polygon(
        2,
        PolygonAnnotation(points=((7, 2), (16, 2), (16, 12), (7, 12))),
    )
    project.add_polygon(
        2,
        PolygonAnnotation(
            points=((7, 4), (11, 4), (11, 10), (7, 10)),
            operation="erase",
        ),
    )

    plane = project.to_mask(interpolate=False)[:, :, 2]

    assert plane[8, 6] == 1  # Prototype survives a manual-source erase polygon.
    assert plane[14, 6] == 1  # Manual-only region is also retained.


def test_force_empty_round_trips_through_json(tmp_path: Path) -> None:
    project = _project()
    project.set_force_empty(2, True)

    loaded = AnnotationProject.load(project.save(tmp_path / "annotations.json"))

    assert loaded.schema_version == 4
    assert loaded.annotation(2).force_empty


def test_reviewing_machine_polygon_preserves_its_source() -> None:
    project = _project()
    project.add_polygon(
        2,
        PolygonAnnotation(
            points=((2, 4), (12, 4), (12, 14), (2, 14)),
            source="prototype",
        ),
    )

    project.set_completed(2, True)

    assert project.annotation(2).polygons[0].source == "prototype"


@pytest.mark.parametrize("interpolate", [False, True])
@pytest.mark.parametrize("seed", range(8))
def test_mask_presence_matches_exported_mask(seed: int, interpolate: bool) -> None:
    project = replace(_project(), shape_lps=(20, 18, 17))
    random = np.random.default_rng(seed)
    for slice_index in range(project.shape_lps[2]):
        for _polygon_index in range(int(random.integers(0, 4))):
            left, top = random.integers(-5, 20, size=2)
            width, height = random.integers(1, 12, size=2)
            project.add_polygon(
                slice_index,
                PolygonAnnotation(
                    points=(
                        (float(left), float(top)),
                        (float(left + width), float(top)),
                        (float(left + width), float(top + height)),
                        (float(left), float(top + height)),
                    ),
                    operation="erase" if random.random() < 0.4 else "add",
                    source="prototype" if random.random() < 0.5 else "manual",
                ),
            )
        project.set_completed(slice_index, random.random() < 0.2)
        project.set_keyframe(slice_index, random.random() < 0.15)
        project.set_force_empty(slice_index, random.random() < 0.2)

    presence = project.mask_presence(interpolate=interpolate)

    assert presence.dtype == np.bool_
    assert presence.shape == (project.shape_lps[2],)
    np.testing.assert_array_equal(
        presence, project.to_mask(interpolate=interpolate).any(axis=(0, 1))
    )


def test_mask_presence_handles_disjoint_keyframes_with_empty_interpolation() -> None:
    project = _project()
    project.add_polygon(0, PolygonAnnotation(points=((1, 1), (1, 1), (1, 1))))
    project.add_polygon(4, PolygonAnnotation(points=((18, 16), (18, 16), (18, 16))))

    assert project.mask_presence().tolist() == [True, False, False, False, True]
    np.testing.assert_array_equal(
        project.mask_presence(), project.to_mask().any((0, 1))
    )


def test_mask_presence_can_be_empty_despite_stored_contours() -> None:
    project = _project()
    points = ((2, 2), (8, 2), (5, 8))
    project.add_polygon(0, PolygonAnnotation(points=points))
    project.add_polygon(0, PolygonAnnotation(points=points, operation="erase"))
    project.add_polygon(1, PolygonAnnotation(points=points, operation="erase"))
    project.add_polygon(2, PolygonAnnotation(points=((-10, -10), (-8, -10), (-9, -8))))
    project.add_polygon(3, PolygonAnnotation(points=points))
    project.set_force_empty(3, True)
    project.set_completed(4, True)

    assert not project.mask_presence().any()
    assert not project.to_mask().any()


def test_mask_presence_keeps_separate_intervals_and_isolated_slices() -> None:
    project = replace(_project(), shape_lps=(20, 18, 13))
    polygon = PolygonAnnotation(points=((2, 2), (10, 2), (10, 10), (2, 10)))
    for slice_index in (0, 4, 6, 8, 12):
        project.add_polygon(slice_index, polygon)
    for slice_index in (5, 7):
        project.set_force_empty(slice_index, True)

    expected = [True] * 5 + [False, True, False] + [True] * 5
    assert project.mask_presence().tolist() == expected


def test_mask_presence_overlapping_keyframes_avoids_distance_and_volume_allocation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _project()
    polygon = PolygonAnnotation(points=((2, 2), (10, 2), (10, 10), (2, 10)))
    project.add_polygon(0, polygon)
    project.add_polygon(4, polygon)

    def unexpected_computation(*_args, **_kwargs) -> None:
        pytest.fail("overlapping keyframes need neither a distance field nor a volume")

    monkeypatch.setattr(AnnotationProject, "_signed_distance", unexpected_computation)
    monkeypatch.setattr(AnnotationProject, "to_mask", unexpected_computation)

    assert project.mask_presence().tolist() == [True] * 5


@pytest.mark.parametrize("state", ["empty", "completed", "keyframe", "force_empty"])
def test_empty_project_removal_ignores_non_polygon_state(tmp_path, state):
    project = _project()
    if state == "completed":
        project.set_completed(2, True)
    elif state == "keyframe":
        project.set_keyframe(2, True)
    elif state == "force_empty":
        project.set_force_empty(2, True)
    path = project.save(tmp_path / "scan.med-image-seg-1.json")
    project.save(path)
    assert Path(f"{path}.bak").is_file()
    for suffix in (".tmp", ".bak.tmp"):
        Path(f"{path}{suffix}").write_text("interrupted write", encoding="utf-8")

    assert not project.has_polygons
    assert project.save(path, delete_if_empty=True) == path
    assert all(
        not Path(f"{path}{suffix}").exists()
        for suffix in ("", ".bak", ".tmp", ".bak.tmp")
    )
    with pytest.raises(FileNotFoundError):
        AnnotationProject.load(path)


def test_default_save_keeps_empty_project_and_backup(tmp_path):
    project = _project()
    project.set_completed(2, True)
    path = project.save(tmp_path / "scan.med-image-seg.json")
    project.save(path)
    assert path.is_file()
    assert Path(f"{path}.bak").is_file()
    assert AnnotationProject.load(path).annotation(2).completed


@pytest.mark.parametrize(
    "operation, forced", [("add", False), ("erase", False), ("add", True)]
)
def test_delete_if_empty_counts_stored_polygons_not_nonzero_mask(
    tmp_path, operation, forced
):
    project = _project()
    project.add_polygon(
        4, PolygonAnnotation(points=((2, 2), (8, 2), (5, 8)), operation=operation)
    )
    project.set_force_empty(4, forced)
    assert project.has_polygons
    path = project.save(tmp_path / "scan.med-image-seg-2.json", delete_if_empty=True)
    assert path.is_file()
    assert AnnotationProject.load(path).has_polygons


def test_deleting_absent_empty_project_does_not_create_directories(tmp_path):
    path = tmp_path / "not-created" / "scan.med-image-seg-9.json"
    _project().save(path, delete_if_empty=True)
    assert not path.parent.exists()


def test_backup_removal_failure_does_not_delete_primary_annotation(
    tmp_path, monkeypatch
):
    project = _project()
    path = project.save(tmp_path / "scan.med-image-seg-2.json")
    project.save(path)
    original = Path.unlink

    def fail_backup(candidate, *args, **kwargs):
        if candidate == Path(f"{path}.bak"):
            raise PermissionError("backup is locked")
        return original(candidate, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "unlink", fail_backup)
        with pytest.raises(PermissionError, match="backup is locked"):
            project.save(path, delete_if_empty=True)
    assert path.is_file()
    assert Path(f"{path}.bak").is_file()
