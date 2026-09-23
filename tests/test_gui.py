from __future__ import annotations

import json
import os
import time
from pathlib import Path

import numpy as np
import pytest
import SimpleITK as sitk

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QPointF, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QProgressBar

from med_image_seg.annotation import AnnotationProject, PolygonAnnotation
from med_image_seg.gui import AnnotationMainWindow, SliceCanvas
from med_image_seg.io import MedicalVolume, MedicalVolumeReader
from med_image_seg.sources import ImageSource


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def _source(tmp_path: Path) -> ImageSource:
    image = tmp_path / "scan.nii.gz"
    image.write_bytes(b"synthetic-nifti-placeholder")
    return ImageSource.from_path(image)


def _volume(source: ImageSource) -> MedicalVolume:
    return MedicalVolume(
        data=np.arange(20 * 16 * 5, dtype=np.float32).reshape(20, 16, 5),
        spacing_mm=(0.8, 0.8, 0.8),
        origin_lps_mm=(0.0, 0.0, 0.0),
        metadata={"modality": "CT"},
        source=source.path,
    )


def _write_nifti(path: Path) -> None:
    image = sitk.GetImageFromArray(
        np.arange(8 * 12 * 16, dtype=np.float32).reshape(8, 12, 16)
    )
    image.SetSpacing((1.0, 1.0, 1.0))
    sitk.WriteImage(image, str(path))


def test_no_argument_window_starts_without_images() -> None:
    app = _app()
    window = AnnotationMainWindow(sources=[])
    app.processEvents()

    assert window.source_list.count() == 0
    assert window.volume is None
    assert all(not widget.isEnabled() for widget in window.editor_widgets)
    window.close()


def test_loading_dialog_is_visible_and_main_ui_is_disabled(tmp_path: Path) -> None:
    app = _app()
    source = _source(tmp_path)
    window = AnnotationMainWindow(sources=[])
    window._show_loading(source)
    app.processEvents()

    assert window.loading_dialog is not None
    assert window.loading_dialog.isVisible()
    progress = window.loading_dialog.findChild(QProgressBar)
    assert progress is not None and progress.isVisible()
    assert (progress.minimum(), progress.maximum()) == (0, 0)
    assert not window.centralWidget().isEnabled()

    window._finish_loading_ui()
    app.processEvents()
    assert window.centralWidget().isEnabled()
    window.close()


def test_polygon_edits_save_immediately_next_to_image(tmp_path: Path) -> None:
    app = _app()
    source = _source(tmp_path)
    window = AnnotationMainWindow(sources=[])
    window._loading_source = source
    window.volume_loaded(_volume(source))
    window._finish_loading_ui()
    window.add_polygon([(2, 2), (8, 2), (5, 8)], "add")
    window.update_polygon(0, [(3, 3), (8, 2), (5, 8)])
    app.processEvents()

    assert source.annotation_path.is_file()
    assert Path(f"{source.annotation_path}.bak").is_file()
    payload = json.loads(source.annotation_path.read_text(encoding="utf-8"))
    current = str(window.current_slice)
    assert payload["slices"][current]["polygons"][0]["points"][0] == [3.0, 3.0]

    window.delete_last_edited_polygon()
    payload = json.loads(source.annotation_path.read_text(encoding="utf-8"))
    assert current not in payload["slices"]
    window.close()


def test_canvas_vertex_handle_can_be_dragged() -> None:
    app = _app()
    canvas = SliceCanvas()
    canvas.resize(420, 420)
    canvas.show()
    canvas.set_slice(
        np.zeros((100, 100), dtype=np.uint8),
        [PolygonAnnotation(points=((20, 20), (80, 20), (50, 80)))],
    )
    app.processEvents()
    changes: list[tuple[int, list[tuple[float, float]]]] = []
    canvas.polygon_changed.connect(
        lambda index, points: changes.append((index, points))
    )

    start = canvas.mapFromScene(QPointF(20, 20))
    destination = canvas.mapFromScene(QPointF(30, 35))
    QTest.mousePress(canvas.viewport(), Qt.MouseButton.LeftButton, pos=start)
    QTest.mouseMove(canvas.viewport(), destination, delay=10)
    QTest.mouseRelease(
        canvas.viewport(), Qt.MouseButton.LeftButton, pos=destination, delay=10
    )
    app.processEvents()

    assert changes
    assert changes[0][0] == 0
    assert np.allclose(changes[0][1][0], (30.0, 35.0), atol=1.0)
    canvas.close()


def test_initial_nifti_loads_in_background_and_creates_json(tmp_path: Path) -> None:
    app = _app()
    image_path = tmp_path / "real.nii.gz"
    _write_nifti(image_path)
    source = ImageSource.from_path(image_path)
    window = AnnotationMainWindow(sources=[source], spacing_mm=1.0)
    window.show()

    deadline = time.monotonic() + 20.0
    while time.monotonic() < deadline:
        app.processEvents()
        if window.current_source == source and window.load_thread is None:
            break
        time.sleep(0.01)

    assert window.current_source == source
    assert window.volume is not None
    assert source.annotation_path.is_file()
    assert window.loading_dialog is None
    assert window.centralWidget().isEnabled()
    window.close()


def test_initial_image_automatically_loads_existing_json(tmp_path: Path) -> None:
    app = _app()
    image_path = tmp_path / "annotated.nii.gz"
    _write_nifti(image_path)
    source = ImageSource.from_path(image_path)
    volume = MedicalVolumeReader(1.0).read(source.path)
    project = AnnotationProject.create(
        image_id=source.source_id,
        source_fingerprint=source.fingerprint,
        volume=volume,
    )
    project.add_polygon(
        3,
        PolygonAnnotation(
            points=((2, 2), (10, 2), (10, 8), (2, 8)),
            source="prototype",
        ),
    )
    project.save(source.annotation_path)
    window = AnnotationMainWindow(sources=[source], spacing_mm=1.0)
    window.show()

    deadline = time.monotonic() + 20.0
    while time.monotonic() < deadline:
        app.processEvents()
        if window.current_source == source and window.load_thread is None:
            break
        time.sleep(0.01)

    assert window.project is not None
    assert window.project.annotation(3).polygons[0].source == "prototype"
    window.set_slice(3)
    assert len(window.canvas._polygon_items) == 1
    window.close()


def test_force_empty_checkbox_saves_immediately(tmp_path: Path) -> None:
    app = _app()
    source = _source(tmp_path)
    window = AnnotationMainWindow(sources=[])
    window._loading_source = source
    window.volume_loaded(_volume(source))
    window._finish_loading_ui()
    window.add_polygon([(2, 2), (8, 2), (5, 8)], "add")

    window.force_empty_check.setChecked(True)
    app.processEvents()

    payload = json.loads(source.annotation_path.read_text(encoding="utf-8"))
    current = str(window.current_slice)
    assert payload["slices"][current]["force_empty"] is True
    assert len(payload["slices"][current]["polygons"]) == 1
    assert not window.canvas._polygon_items
    assert window.project is not None
    assert not window.project.to_mask()[:, :, window.current_slice].any()
    window.close()
