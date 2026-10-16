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

from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QKeyEvent, QShortcut
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox, QProgressBar

from med_image_seg.annotation import (
    AnnotationExporter,
    AnnotationProject,
    PolygonAnnotation,
)
from med_image_seg.gui import AnnotationMainWindow, SliceCanvas
from med_image_seg.io import MedicalVolume, MedicalVolumeReader
from med_image_seg.localization import translate
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


def _assert_polygon_busy(window: AnnotationMainWindow) -> None:
    assert window._closing_polygon
    assert not window.isEnabled()
    assert not window.centralWidget().isEnabled()
    assert not window.annotation_toolbar.isEnabled()
    assert not window.canvas.isEnabled()
    assert all(not action.isEnabled() for action in window.annotation_toolbar.actions())
    assert all(not shortcut.isEnabled() for shortcut in window.findChildren(QShortcut))
    assert not window.autosave_timer.isActive()
    assert window.statusBar().currentMessage() == translate("closing_polygon_status")
    cursor = QApplication.overrideCursor()
    assert cursor is not None
    assert cursor.shape() == Qt.CursorShape.WaitCursor


def test_no_argument_window_starts_without_images() -> None:
    app = _app()
    window = AnnotationMainWindow(sources=[])
    app.processEvents()

    assert window.source_list.count() == 0
    assert window.volume is None
    assert window.language == "en"
    assert window.file_button.text() == "Import image files"
    assert all(not widget.isEnabled() for widget in window.editor_widgets)
    assert not window.export_action.isEnabled()
    assert not window.export_ubd_action.isEnabled()
    assert not window.export_json_action.isEnabled()
    assert window.annotation_toolbar.actions() == [
        window.export_action,
        window.export_ubd_action,
        window.export_json_action,
    ]
    window.close()


def test_interface_language_can_switch_without_restart() -> None:
    app = _app()
    window = AnnotationMainWindow(sources=[])
    assert window.export_action.text() == "Export interpolated 3D mask (.nii.gz)"
    assert window.export_ubd_action.text() == "Export interpolated 3D mask (.ubd.npz)"
    assert (
        window.export_json_action.text() == "Export annotations (.med-image-seg.json)"
    )

    window.set_language("zh")
    app.processEvents()

    assert window.language == "zh"
    assert window.file_button.text() == "导入影像文件"
    assert window.windowTitle() == "med-image-seg - 医疗影像多边形标注"
    assert window.language_combo.currentData() == "zh"
    assert window.export_action.text() == translate("export_mask", "zh")
    assert window.export_ubd_action.text() == translate("export_ubd_mask", "zh")
    assert window.export_json_action.text() == translate("export_annotations", "zh")
    window.close()


def test_loading_dialog_is_visible_and_main_ui_is_disabled(tmp_path: Path) -> None:
    app = _app()
    source = _source(tmp_path)
    window = AnnotationMainWindow(sources=[])
    window._loading_source = source
    window.volume_loaded(_volume(source))
    window._finish_loading_ui()
    assert window.export_action.isEnabled()
    assert window.export_ubd_action.isEnabled()
    assert window.export_json_action.isEnabled()
    window._show_loading(source)
    app.processEvents()

    assert window.loading_dialog is not None
    assert window.loading_dialog.isVisible()
    progress = window.loading_dialog.findChild(QProgressBar)
    assert progress is not None and progress.isVisible()
    assert (progress.minimum(), progress.maximum()) == (0, 0)
    assert not window.centralWidget().isEnabled()
    assert not window.export_action.isEnabled()
    assert not window.export_ubd_action.isEnabled()
    assert not window.export_json_action.isEnabled()

    window._finish_loading_ui()
    app.processEvents()
    assert window.centralWidget().isEnabled()
    assert window.export_action.isEnabled()
    assert window.export_ubd_action.isEnabled()
    assert window.export_json_action.isEnabled()
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


@pytest.mark.parametrize("trigger", ["space", "button", "right", "double"])
def test_polygon_closure_disables_ui_until_save_and_refresh_finish(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, trigger: str
) -> None:
    app = _app()
    source = _source(tmp_path)
    window = AnnotationMainWindow(sources=[])
    window._loading_source = source
    window.volume_loaded(_volume(source))
    window._finish_loading_ui()
    window.show()
    window.activateWindow()
    window.canvas.setFocus()
    app.processEvents()
    points = [(2.0, 2.0), (8.0, 2.0), (5.0, 8.0)]
    window.canvas._draft_points = [QPointF(*point) for point in points]
    window.canvas._update_draft()
    slice_index = window.current_slice
    previous_message = window.statusBar().currentMessage()
    stages: list[str] = []
    add_polygon = AnnotationProject.add_polygon
    save = AnnotationProject.save
    refresh_slice = window.refresh_slice

    def record_add(
        self: AnnotationProject, index: int, polygon: PolygonAnnotation
    ) -> None:
        _assert_polygon_busy(window)
        stages.append("annotation")
        add_polygon(self, index, polygon)

    def record_save(self: AnnotationProject, path: str | Path) -> Path:
        _assert_polygon_busy(window)
        stages.append("save")
        window.add_polygon(points, "add")
        window.canvas.finish_polygon()
        window.autosave_if_needed()
        assert not window.close()
        for event_type in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease):
            QApplication.postEvent(
                window,
                QKeyEvent(event_type, Qt.Key.Key_Right, Qt.KeyboardModifier.NoModifier),
            )
        return save(self, path)

    def record_refresh() -> None:
        _assert_polygon_busy(window)
        stages.append("refresh")
        refresh_slice()

    try:
        with monkeypatch.context() as patch:
            patch.setattr(AnnotationProject, "add_polygon", record_add)
            patch.setattr(AnnotationProject, "save", record_save)
            patch.setattr(window, "refresh_slice", record_refresh)
            if trigger == "space":
                QTest.keyClick(window.canvas.viewport(), Qt.Key.Key_Space)
            elif trigger == "button":
                window.finish_button.click()
            elif trigger == "right":
                QTest.mouseClick(window.canvas.viewport(), Qt.MouseButton.RightButton)
            else:
                QTest.mouseDClick(window.canvas.viewport(), Qt.MouseButton.LeftButton)
            app.processEvents()

        assert stages == ["annotation", "save", "refresh"]
        assert window.isEnabled()
        assert window.centralWidget().isEnabled()
        assert window.canvas.isEnabled()
        assert window.annotation_toolbar.isEnabled()
        assert all(action.isEnabled() for action in window.annotation_toolbar.actions())
        assert all(shortcut.isEnabled() for shortcut in window.findChildren(QShortcut))
        assert window.autosave_timer.isActive()
        assert not window._closing_polygon
        assert not window._dirty
        assert window.statusBar().currentMessage() == previous_message
        assert QApplication.overrideCursor() is None
        assert window.current_slice == slice_index
        assert not window.canvas._draft_points
        assert len(window.canvas._polygon_items) == 1
        loaded = AnnotationProject.load(source.annotation_path)
        assert len(loaded.annotation(slice_index).polygons) == 1
    finally:
        window.close()


@pytest.mark.parametrize("failed_step", ["annotation", "save", "refresh"])
@pytest.mark.parametrize("initially_enabled", [False, True])
def test_polygon_closure_restores_previous_ui_state_after_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failed_step: str,
    initially_enabled: bool,
) -> None:
    app = _app()
    source = _source(tmp_path)
    window = AnnotationMainWindow(sources=[])
    window._loading_source = source
    window.volume_loaded(_volume(source))
    window._finish_loading_ui()
    window.file_button.setEnabled(False)
    window.export_json_action.setEnabled(False)
    shortcuts = window.findChildren(QShortcut)
    shortcuts[0].setEnabled(False)
    window.autosave_timer.stop()
    window.setEnabled(initially_enabled)
    window.statusBar().showMessage("previous status")
    QApplication.setOverrideCursor(Qt.CursorShape.CrossCursor)

    def fail_annotation(
        self: AnnotationProject, index: int, polygon: PolygonAnnotation
    ) -> None:
        _assert_polygon_busy(window)
        raise RuntimeError("simulated polygon failure")

    def fail_save(self: AnnotationProject, path: str | Path) -> Path:
        _assert_polygon_busy(window)
        raise OSError("simulated JSON save failure")

    def fail_refresh() -> None:
        _assert_polygon_busy(window)
        raise RuntimeError("simulated polygon failure")

    try:
        with monkeypatch.context() as patch:
            if failed_step == "annotation":
                patch.setattr(AnnotationProject, "add_polygon", fail_annotation)
            elif failed_step == "save":
                patch.setattr(AnnotationProject, "save", fail_save)
            else:
                patch.setattr(window, "refresh_slice", fail_refresh)
            if failed_step == "save":
                window.add_polygon([(2, 2), (8, 2), (5, 8)], "add")
                assert window._dirty
                assert "simulated JSON save failure" in window.autosave_status.text()
            else:
                with pytest.raises(RuntimeError, match="simulated polygon failure"):
                    window.add_polygon([(2, 2), (8, 2), (5, 8)], "add")
            app.processEvents()

        assert window.isEnabled() is initially_enabled
        assert not window.file_button.isEnabled()
        assert not window.export_json_action.isEnabled()
        assert not shortcuts[0].isEnabled()
        assert all(shortcut.isEnabled() for shortcut in shortcuts[1:])
        assert not window.autosave_timer.isActive()
        assert not window._closing_polygon
        assert window.statusBar().currentMessage() == "previous status"
        cursor = QApplication.overrideCursor()
        assert cursor is not None
        assert cursor.shape() == Qt.CursorShape.CrossCursor
    finally:
        QApplication.restoreOverrideCursor()
        window.close()


@pytest.mark.parametrize("point_count", [0, 1, 2])
def test_incomplete_polygon_does_not_enter_busy_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, point_count: int
) -> None:
    app = _app()
    source = _source(tmp_path)
    window = AnnotationMainWindow(sources=[])
    window._loading_source = source
    window.volume_loaded(_volume(source))
    window._finish_loading_ui()
    window.canvas._draft_points = [
        QPointF(index, index) for index in range(point_count)
    ]
    previous_json = source.annotation_path.read_bytes()

    def unexpected_busy_state() -> None:
        pytest.fail("an incomplete polygon must not enter the busy state")

    monkeypatch.setattr(window, "_polygon_busy_ui", unexpected_busy_state)
    try:
        window.canvas.finish_polygon()
        app.processEvents()

        assert window.isEnabled()
        assert not window._closing_polygon
        assert len(window.canvas._draft_points) == point_count
        assert source.annotation_path.read_bytes() == previous_json
        assert QApplication.overrideCursor() is None
    finally:
        window.close()


@pytest.mark.parametrize("suffix", [".nii.gz", ".ubd.npz"])
def test_export_toolbar_actions_write_interpolated_masks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, suffix: str
) -> None:
    app = _app()
    source = _source(tmp_path)
    volume = _volume(source)
    window = AnnotationMainWindow(sources=[])
    window._loading_source = source
    window.volume_loaded(volume)
    window._finish_loading_ui()
    messages: list[str] = []
    monkeypatch.setattr(
        QMessageBox,
        "information",
        lambda _parent, _title, message: messages.append(message),
    )
    monkeypatch.setattr(
        QMessageBox, "critical", lambda _parent, _title, message: pytest.fail(message)
    )
    try:
        for slice_index in (1, 3):
            window.set_slice(slice_index)
            window.add_polygon([(2, 2), (8, 2), (5, 8)], "add")
        assert window.project is not None
        expected = window.project.to_mask(interpolate=True)
        assert expected[:, :, 2].any()
        if suffix == ".ubd.npz":
            window.export_ubd_action.trigger()
            output = source.ubd_mask_path
            assert not source.mask_path.exists()
            with np.load(output, allow_pickle=False) as archive:
                assert archive["image_type"].item() == "mask"
                assert archive["mmpd"].item() == volume.spacing_mm[0]
                written = archive["body_data"]
        else:
            window.export_action.trigger()
            output = source.mask_path
            assert not source.ubd_mask_path.exists()
            image = sitk.ReadImage(str(output))
            written = np.transpose(sitk.GetArrayFromImage(image), (2, 1, 0))
        app.processEvents()

        np.testing.assert_array_equal(written, expected)
        assert source.annotation_path.is_file()
        assert len(messages) == 1
        assert str(output) in messages[0]
        assert QApplication.overrideCursor() is None
    finally:
        window.close()


@pytest.mark.parametrize("failed_step", ["save", "export"])
def test_ubd_export_handles_failures_without_success_message(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failed_step: str
) -> None:
    app = _app()
    source = _source(tmp_path)
    window = AnnotationMainWindow(sources=[])
    window._loading_source = source
    window.volume_loaded(_volume(source))
    window._finish_loading_ui()
    errors: list[str] = []

    def fail_export(
        self: AnnotationExporter,
        project: AnnotationProject,
        volume: MedicalVolume,
        output_path: Path,
        *,
        interpolate: bool,
    ) -> Path:
        if failed_step == "save":
            pytest.fail("export must not run when saving fails")
        raise OSError("simulated UBD export failure")

    try:
        with monkeypatch.context() as patch:
            patch.setattr(AnnotationExporter, "export", fail_export)
            if failed_step == "save":
                patch.setattr(window, "save_project", lambda *, notify: False)
            patch.setattr(
                QMessageBox,
                "critical",
                lambda _parent, _title, message: errors.append(message),
            )
            patch.setattr(
                QMessageBox,
                "information",
                lambda *_args: pytest.fail("failed export must not report success"),
            )

            window.export_ubd_action.trigger()
            app.processEvents()

            assert not source.ubd_mask_path.exists()
            assert errors == (
                ["simulated UBD export failure"] if failed_step == "export" else []
            )
            assert QApplication.overrideCursor() is None
    finally:
        window.close()


@pytest.mark.parametrize("suffix", [".dcm", ".nii", ".nii.gz", ".ubd.npz"])
@pytest.mark.parametrize("file_state", ["saved", "missing", "pending"])
def test_json_export_saves_annotation_project_beside_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    suffix: str,
    file_state: str,
) -> None:
    app = _app()
    directory = tmp_path / "中文目录"
    directory.mkdir()
    image = directory / f"病例{suffix}"
    image.write_bytes(b"synthetic-image")
    source = ImageSource.from_path(image)
    volume = _volume(source)
    window = AnnotationMainWindow(sources=[])
    window._loading_source = source
    window.volume_loaded(volume)
    window._finish_loading_ui()
    messages: list[str] = []
    saved_paths: list[Path] = []
    save = AnnotationProject.save

    def record_save(self: AnnotationProject, path: str | Path) -> Path:
        saved_paths.append(Path(path))
        return save(self, path)

    try:
        for slice_index in (1, 3):
            window.set_slice(slice_index)
            window.add_polygon([(2, 2), (8, 2), (5, 8)], "add")
        window.set_slice_completed(True)
        window.set_slice(4)
        window.set_force_empty(True)
        assert window.project is not None
        assert not window._dirty
        previous_json = source.annotation_path.read_bytes()
        if file_state == "missing":
            source.annotation_path.unlink()
        elif file_state == "pending":
            window.project.add_polygon(
                0,
                PolygonAnnotation(points=((3, 3), (9, 3), (6, 9)), source="prototype"),
            )
            window._dirty = True
        monkeypatch.setattr(AnnotationProject, "save", record_save)
        monkeypatch.setattr(
            QMessageBox,
            "information",
            lambda _parent, _title, message: messages.append(message),
        )
        monkeypatch.setattr(
            QMessageBox,
            "critical",
            lambda _parent, _title, message: pytest.fail(message),
        )

        window.export_json_action.trigger()
        app.processEvents()

        loaded = AnnotationProject.load(source.annotation_path)
        loaded.validate_volume(volume)
        assert loaded.image_id == window.project.image_id
        assert loaded.source_fingerprint == window.project.source_fingerprint
        assert loaded.edit_counter == window.project.edit_counter
        assert loaded.metadata == window.project.metadata
        for slice_index in range(volume.data.shape[2]):
            assert loaded.annotation(slice_index) == window.project.annotation(
                slice_index
            )
        np.testing.assert_array_equal(loaded.to_mask(), window.project.to_mask())
        assert saved_paths == [source.annotation_path]
        assert not window._dirty
        assert not source.mask_path.exists()
        assert not source.ubd_mask_path.exists()
        if file_state != "missing":
            assert Path(f"{source.annotation_path}.bak").read_bytes() == previous_json
        assert len(messages) == 1
        assert messages[0] == translate(
            "export_annotations_complete_message", path=source.annotation_path
        )
        assert QApplication.overrideCursor() is None
    finally:
        window.close()


@pytest.mark.parametrize("dirty", [False, True])
def test_json_export_reports_save_failure_without_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, dirty: bool
) -> None:
    app = _app()
    source = _source(tmp_path)
    window = AnnotationMainWindow(sources=[])
    window._loading_source = source
    window.volume_loaded(_volume(source))
    window._finish_loading_ui()
    errors: list[str] = []
    previous_json = source.annotation_path.read_bytes()
    window._dirty = dirty

    def fail_save(self: AnnotationProject, path: str | Path) -> Path:
        raise OSError("simulated JSON export failure")

    try:
        with monkeypatch.context() as patch:
            patch.setattr(AnnotationProject, "save", fail_save)
            patch.setattr(
                QMessageBox,
                "critical",
                lambda _parent, _title, message: errors.append(message),
            )
            patch.setattr(
                QMessageBox,
                "information",
                lambda *_args: pytest.fail("failed export must not report success"),
            )

            window.export_json_action.trigger()
            app.processEvents()

            assert errors == ["simulated JSON export failure"]
            assert window._dirty is dirty
            assert source.annotation_path.read_bytes() == previous_json
            assert QApplication.overrideCursor() is None
    finally:
        window.close()


def test_json_export_without_project_does_not_report_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _app()
    window = AnnotationMainWindow(sources=[])
    monkeypatch.setattr(
        QMessageBox,
        "information",
        lambda *_args: pytest.fail("no project must not report export success"),
    )
    try:
        window.export_annotations()
        app.processEvents()
        assert not window.export_json_action.isEnabled()
    finally:
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
