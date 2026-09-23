from __future__ import annotations

import json
from pathlib import Path

import numpy as np

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
