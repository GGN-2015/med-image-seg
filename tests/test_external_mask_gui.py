from __future__ import annotations

import os
import threading
import time
from copy import deepcopy
from dataclasses import asdict

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QPointF, QTimer
from PySide6.QtGui import QShortcut
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox, QProgressBar

from med_image_seg.annotation import AnnotationProject
from med_image_seg.gui import EXTERNAL_MASK_COLOR, AnnotationMainWindow
from med_image_seg.io import MedicalMaskReader, MedicalMaskWriter, MedicalVolume
from med_image_seg.localization import translate
from med_image_seg.observation import OBSERVATION_PLANES
from med_image_seg.sources import ImageSource


def _wait_loaded(window):
    deadline = time.monotonic() + 10
    while window.external_mask_thread is not None and time.monotonic() < deadline:
        QApplication.processEvents()
        time.sleep(0.005)
    assert window.external_mask_thread is None
    QApplication.processEvents()


@pytest.fixture
def window(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    path = tmp_path / "scan.nii"
    path.write_bytes(b"synthetic-image")
    source = ImageSource.from_path(path)
    instance = AnnotationMainWindow(sources=[], language="zh")
    instance._loading_source = source
    instance.volume_loaded(
        MedicalVolume(
            data=np.arange(20 * 16 * 9, dtype=np.float32).reshape(20, 16, 9),
            spacing_mm=(0.8, 0.8, 0.8),
            origin_lps_mm=(10.0, 20.0, 30.0),
            metadata={},
            source=path,
        )
    )
    instance._finish_loading_ui()
    instance.show()
    app.processEvents()
    instance._test_mask_errors = []
    monkeypatch.setattr(
        QMessageBox,
        "critical",
        lambda *args: instance._test_mask_errors.append(args[2]),
    )
    yield instance
    _wait_loaded(instance)
    instance.close()
    app.processEvents()
    instance.deleteLater()
    app.processEvents()


def _seed(window):
    window.set_slice(2)
    window.add_polygon([(2, 2), (9, 2), (5, 10)], "add")
    window.set_slice(6)
    window.add_polygon([(3, 2), (10, 2), (6, 10)], "add")
    window.set_slice(4)


def _write_mask(window, tmp_path, suffix=".nii.gz", empty=False):
    mask = np.zeros(window.volume.data.shape, dtype=np.uint8)
    if not empty:
        mask[3:12, 5:10, 1] = 1
        mask[5:15, 7:13, 7:9] = 1
    path = MedicalMaskWriter().write(
        tmp_path / f"external{suffix}", mask, window.volume
    )
    return path, mask


def _overlay(canvas):
    image = canvas._interpolation_item.pixmap().toImage()
    return np.array(
        [
            [
                image.pixelColor(horizontal, vertical).getRgb()
                for horizontal in range(image.width())
            ]
            for vertical in range(image.height())
        ],
        dtype=np.uint8,
    )


def test_buttons_start_with_only_load_enabled_even_without_image(monkeypatch):
    app = QApplication.instance() or QApplication([])
    window = AnnotationMainWindow(sources=[], language="zh")
    assert window.load_external_mask_button.isEnabled()
    assert not window.unload_external_mask_button.isEnabled()
    assert window.load_external_mask_button.text() == "载入外置掩码"
    assert window.unload_external_mask_button.text() == "卸载外置掩码"
    messages = []
    monkeypatch.setattr(
        QMessageBox, "information", lambda *args: messages.append(args[2])
    )
    window.choose_external_mask()
    assert messages == [translate("external_mask_no_image", "zh")]
    assert not window.external_preview_active
    window.close()
    app.processEvents()


@pytest.mark.parametrize("suffix", [".nii", ".nii.gz", ".ubd.npz"])
def test_external_mask_replaces_all_polygon_views_and_coverage(
    window, tmp_path, suffix
):
    _seed(window)
    project = window.project
    original = deepcopy(asdict(project))
    original_json = window.project_path.read_bytes()
    path, expected = _write_mask(window, tmp_path, suffix)
    assert window.load_external_mask(path)
    _wait_loaded(window)
    assert not window._test_mask_errors
    assert window.external_preview_active
    assert window.read_only
    assert window.observe_radio.isChecked()
    assert not window.annotation_index_spin.isEnabled()
    assert not window.load_external_mask_button.isEnabled()
    assert window.unload_external_mask_button.isEnabled()
    assert not window.mode_group.isEnabled()
    assert all(not action.isEnabled() for action in window.annotation_toolbar.actions())
    assert not window.autosave_timer.isActive()
    np.testing.assert_array_equal(window.external_mask, expected)
    np.testing.assert_array_equal(
        window.mask_coverage_bar.presence, expected.any(axis=(0, 1))
    )
    window._observation_clicked("LP", QPointF(8.5, 8.5))
    window.set_slice(7)
    for name, plane in OBSERVATION_PLANES.items():
        canvas = (
            window.canvas if name == "LP" else window.observation_windows[name].canvas
        )
        assert not canvas._handles
        assert not canvas._polygon_items
        overlay = _overlay(canvas)
        mask_section = plane.section(expected, window.observation_position).astype(bool)
        np.testing.assert_array_equal(overlay[:, :, 3] > 0, mask_section)
        assert np.all(overlay[mask_section] == EXTERNAL_MASK_COLOR)
    assert window.project is project
    assert asdict(window.project) == original
    assert window.project_path.read_bytes() == original_json


def test_external_preview_never_calls_json_save_or_full_polygon_rasterization(
    window, tmp_path, monkeypatch
):
    _seed(window)
    path, _ = _write_mask(window, tmp_path)
    original = deepcopy(asdict(window.project))

    def forbidden(*args, **kwargs):
        pytest.fail("External preview must not rasterize or save the JSON project")

    with monkeypatch.context() as patch:
        patch.setattr(AnnotationProject, "save", forbidden)
        patch.setattr(AnnotationProject, "to_mask", forbidden)
        assert window.load_external_mask(path)
        _wait_loaded(window)
        window.set_slice(1)
        window._observation_clicked("PS", QPointF(5.5, 7.5))
        window.level_spin.setValue(window.level_spin.value() + 5)
        window.set_language("en")
        window.add_polygon([(1, 1), (5, 1), (2, 5)], "add")
        window.update_polygon(0, [(1, 1), (5, 1), (2, 5)])
        window.delete_last_edited_polygon()
        window.clear_current_slice()
        window.copy_previous_slice()
        window.set_slice_completed(True)
        window.set_force_empty(True)
        window.toggle_completed()
        window.commit_change()
        window.autosave_if_needed()
        assert window.save_project(notify=True, force=True)
        window.export_annotations()
        window.export_mask()
        window.export_ubd_mask()
        assert not window.set_annotation_index(1)
        window.add_radio.setChecked(True)
        assert window.observe_radio.isChecked()
        assert window.read_only
        assert asdict(window.project) == original
        assert "JSON saving paused" in window.autosave_status.text()
        assert window.close()


@pytest.mark.parametrize("mode", ["add", "erase", "observe"])
@pytest.mark.parametrize("autosave_active", [True, False])
def test_unload_restores_original_number_slice_mode_coverage_and_shortcuts(
    window, tmp_path, monkeypatch, mode, autosave_active
):
    window.set_annotation_index(3)
    _seed(window)
    window.show_interpolation.setChecked(False)
    radio = {
        "add": window.add_radio,
        "erase": window.erase_radio,
        "observe": window.observe_radio,
    }[mode]
    radio.setChecked(True)
    if not autosave_active:
        window.autosave_timer.stop()
    position = window.observation_position
    coverage = window.mask_coverage_bar.presence
    project, project_path = window.project, window.project_path
    saved = project_path.read_bytes()
    cached_mask = window._observation_mask
    path, _ = _write_mask(window, tmp_path)
    assert window.load_external_mask(path)
    _wait_loaded(window)
    window._observation_clicked("PS", QPointF(8.5, 7.5))
    window._observation_clicked("SL", QPointF(8.5, 13.5))

    def no_reload(*args, **kwargs):
        pytest.fail(
            "Unloading must restore the in-memory project without reloading JSON"
        )

    monkeypatch.setattr(AnnotationProject, "load", no_reload)
    assert window.unload_external_mask()
    assert not window.external_preview_active
    assert window.external_mask is None
    assert window.project is project
    assert window.project_path == project_path
    assert window.annotation_index == window.annotation_index_spin.value() == 3
    assert (
        window.current_slice
        == window.slice_slider.value()
        == window.slice_spin.value()
        == position[2]
    )
    assert window.observation_position == position
    assert window.mask_coverage_bar.presence == coverage
    assert window._observation_mask is cached_mask
    assert radio.isChecked()
    assert window.read_only == (mode == "observe")
    assert window.annotation_index_spin.isEnabled() == (mode != "observe")
    assert all(
        shortcut.isEnabled() == (mode != "observe")
        for shortcut in window.editing_shortcuts
    )
    assert all(action.isEnabled() for action in window.annotation_toolbar.actions())
    assert window.load_external_mask_button.isEnabled()
    assert not window.unload_external_mask_button.isEnabled()
    assert window.autosave_timer.isActive() == autosave_active
    assert project_path.read_bytes() == saved
    assert window.show_interpolation.isChecked() == (mode == "observe")


@pytest.mark.parametrize("cancel", [True, False])
def test_file_chooser_opens_after_switching_to_read_only(
    window, tmp_path, monkeypatch, cancel
):
    _seed(window)
    path, _ = _write_mask(window, tmp_path)

    def choose(*args):
        assert window.external_preview_active
        assert window.read_only
        assert not window.annotation_index_spin.isEnabled()
        assert window.observe_radio.isChecked()
        assert all(view.isVisible() for view in window.observation_windows.values())
        assert "*.nii *.nii.gz *.ubd.npz" in args[3]
        return ("" if cancel else str(path), "")

    monkeypatch.setattr(QFileDialog, "getOpenFileName", choose)
    window.choose_external_mask()
    _wait_loaded(window)
    if cancel:
        assert not window.external_preview_active
        assert not window.read_only
        assert window.annotation_index_spin.isEnabled()
        assert window.load_external_mask_button.isEnabled()
        assert not window.unload_external_mask_button.isEnabled()
    else:
        assert window.external_mask is not None


@pytest.mark.parametrize("failure", ["missing", "corrupt", "unsupported"])
def test_failed_external_load_restores_original_editing_state(
    window, tmp_path, failure
):
    window.set_annotation_index(2)
    _seed(window)
    position = window.observation_position
    project = window.project
    saved = window.project_path.read_bytes()
    path = tmp_path / ("invalid.npz" if failure == "unsupported" else "invalid.nii")
    if failure != "missing":
        path.write_bytes(b"not a medical image")
    assert window.load_external_mask(path)
    _wait_loaded(window)
    assert window._test_mask_errors
    assert not window.external_preview_active
    assert not window.read_only
    assert window.project is project
    assert window.annotation_index == 2
    assert window.observation_position == position
    assert window.external_loading_dialog is None
    assert window.centralWidget().isEnabled()
    assert window.annotation_toolbar.isEnabled()
    assert window.load_external_mask_button.isEnabled()
    assert not window.unload_external_mask_button.isEnabled()
    assert window.autosave_timer.isActive()
    assert QApplication.overrideCursor() is None
    assert window.project_path.read_bytes() == saved


def test_external_loading_is_nonblocking_and_locks_all_views_until_completion(
    window, tmp_path, monkeypatch
):
    path, mask = _write_mask(window, tmp_path)
    started, release = threading.Event(), threading.Event()
    worker_threads = []

    def delayed(*args):
        worker_threads.append(threading.get_ident())
        started.set()
        assert release.wait(5)
        return mask

    monkeypatch.setattr(MedicalMaskReader, "read", delayed)
    ticks = []
    timer = QTimer(window)
    timer.setInterval(5)
    timer.timeout.connect(lambda: ticks.append(True))
    timer.start()
    try:
        assert window.load_external_mask(path)
        deadline = time.monotonic() + 2
        while (not started.is_set() or len(ticks) < 3) and time.monotonic() < deadline:
            QApplication.processEvents()
            time.sleep(0.005)
        assert started.is_set()
        assert len(ticks) >= 3
        assert len(worker_threads) == 1
        assert worker_threads[0] != threading.get_ident()
        assert not window.centralWidget().isEnabled()
        assert not window.annotation_toolbar.isEnabled()
        assert all(not view.isEnabled() for view in window.observation_windows.values())
        assert all(
            not shortcut.isEnabled() for shortcut in window.findChildren(QShortcut)
        )
        assert window.external_loading_dialog.isVisible()
        progress = window.external_loading_dialog.findChild(QProgressBar)
        assert (progress.minimum(), progress.maximum()) == (0, 0)
        assert not window.unload_external_mask()
        assert not window.load_external_mask(path)
        assert not window.close()
    finally:
        release.set()
        timer.stop()
        _wait_loaded(window)
    assert window.centralWidget().isEnabled()
    assert window.unload_external_mask_button.isEnabled()
    assert window.external_loading_dialog is None


def test_empty_external_mask_displays_all_gray_coverage_without_json_fallback(
    window, tmp_path
):
    _seed(window)
    path, _ = _write_mask(window, tmp_path, empty=True)
    assert window.load_external_mask(path)
    _wait_loaded(window)
    assert window.external_mask is not None
    assert not window.external_mask.any()
    assert window.mask_coverage_bar.presence == (False,) * 9
    assert not window.canvas._polygon_items
    assert not (_overlay(window.canvas)[:, :, 3] > 0).any()


def test_unsaved_draft_is_closed_before_external_preview_then_restored(
    window, tmp_path
):
    points = [(2, 2), (9, 2), (5, 10)]
    window.canvas._draft_points = [QPointF(*point) for point in points]
    old_slice = window.current_slice
    path, _ = _write_mask(window, tmp_path)
    window.load_external_mask(path)
    _wait_loaded(window)
    assert not window.canvas._handles
    assert window.project.annotation(old_slice).polygons[0].points == tuple(points)
    window.unload_external_mask()
    assert window.canvas._handles
    assert window.current_slice == old_slice
