from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QPointF, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox

from med_image_seg.annotation import AnnotationProject, PolygonAnnotation
from med_image_seg.gui import AnnotationMainWindow
from med_image_seg.io import MedicalVolume
from med_image_seg.observation import AXIS_COLORS, OBSERVATION_PLANES
from med_image_seg.sources import ImageSource


def _load_volume(
    window: AnnotationMainWindow,
    path: Path,
    shape: tuple[int, int, int] = (20, 16, 9),
) -> None:
    path.write_bytes(b"synthetic-image")
    source = ImageSource.from_path(path)
    volume = MedicalVolume(
        data=np.arange(np.prod(shape), dtype=np.float32).reshape(shape),
        spacing_mm=(0.8, 0.8, 0.8),
        origin_lps_mm=(10.0, 20.0, 30.0),
        metadata={},
        source=source.path,
    )
    window._loading_source = source
    window.volume_loaded(volume)
    window._finish_loading_ui()


@pytest.fixture
def window(tmp_path):
    app = QApplication.instance() or QApplication([])
    instance = AnnotationMainWindow(sources=[], language="zh")
    _load_volume(instance, tmp_path / "scan.nii.gz")
    instance.show()
    app.processEvents()
    yield instance
    instance.close()
    app.processEvents()
    instance.deleteLater()
    app.processEvents()


def _seed_masks(window: AnnotationMainWindow) -> np.ndarray:
    polygon = PolygonAnnotation(points=((3, 3), (15, 3), (15, 12), (3, 12)))
    erase = PolygonAnnotation(
        points=((8, 6), (10, 6), (10, 8), (8, 8)), operation="erase"
    )
    for index in (1, 7):
        window.project.add_polygon(index, polygon)
        window.project.add_polygon(index, erase)
    window.project.set_force_empty(4, True)
    window.commit_change()
    window.refresh_slice()
    return window.project.to_mask(interpolate=True)


def _canvas(window: AnnotationMainWindow, name: str):
    return window.canvas if name == "LP" else window.observation_windows[name].canvas


def _overlay_mask(canvas) -> np.ndarray:
    image = canvas._interpolation_item.pixmap().toImage()
    return np.array(
        [
            [
                image.pixelColor(horizontal, vertical).alpha() > 0
                for horizontal in range(image.width())
            ]
            for vertical in range(image.height())
        ],
        dtype=bool,
    )


@pytest.mark.parametrize("name", ["LP", "PS", "SL"])
def test_plane_sections_have_correct_axes_and_voxel_values(name):
    data = np.arange(7 * 11 * 13).reshape(7, 11, 13)
    position = (2, 5, 9)
    plane = OBSERVATION_PLANES[name]
    section = plane.section(data, position)
    assert section.shape == (
        data.shape[plane.vertical_axis],
        data.shape[plane.horizontal_axis],
    )
    for vertical in range(section.shape[0]):
        for horizontal in range(section.shape[1]):
            voxel = list(position)
            voxel[plane.horizontal_axis] = horizontal
            voxel[plane.vertical_axis] = vertical
            assert section[vertical, horizontal] == data[tuple(voxel)]


@pytest.mark.parametrize("name", ["LP", "PS", "SL"])
def test_plane_clicks_use_pixel_centers_and_clamp_to_volume(name):
    plane = OBSERVATION_PLANES[name]
    position = (2, 5, 9)
    shape = (7, 11, 13)
    result = plane.position_at(position, 1.5, 3.5, shape)
    assert result[plane.horizontal_axis] == 1
    assert result[plane.vertical_axis] == 3
    assert result[plane.fixed_axis] == position[plane.fixed_axis]
    result = plane.position_at(position, -20, 100, shape)
    assert result[plane.horizontal_axis] == 0
    assert result[plane.vertical_axis] == shape[plane.vertical_axis] - 1


@pytest.mark.parametrize("operation", ["add", "erase"])
def test_entering_observation_closes_and_saves_draft_before_read_only(
    window, operation
):
    if operation == "erase":
        window.erase_radio.setChecked(True)
    window.canvas._draft_points = [QPointF(2, 2), QPointF(8, 2), QPointF(5, 8)]
    window.observe_radio.setChecked(True)
    annotation = window.project.annotation(window.current_slice)
    assert len(annotation.polygons) == 1
    assert annotation.polygons[0].operation == operation
    restored = AnnotationProject.load(window.project_path)
    assert restored.annotation(window.current_slice).polygons == annotation.polygons
    assert not window.canvas._draft_points
    assert window.read_only
    assert window.canvas.read_only
    assert window.canvas._handles
    assert all(not control.isEnabled() for control in window.editing_controls)
    assert all(not shortcut.isEnabled() for shortcut in window.editing_shortcuts)
    assert window.slice_slider.isEnabled()
    assert window.level_spin.isEnabled()
    assert window.export_action.isEnabled()
    assert window.export_ubd_action.isEnabled()
    assert window.export_json_action.isEnabled()


@pytest.mark.parametrize("count", [0, 1, 2])
def test_too_short_draft_is_discarded_without_creating_invalid_polygon(window, count):
    window.canvas._draft_points = [QPointF(index, index) for index in range(count)]
    window.observe_radio.setChecked(True)
    assert window.read_only
    assert not window.project.annotation(window.current_slice).polygons
    assert not window.canvas._draft_points


@pytest.mark.parametrize(
    ("name", "clicked", "expected"),
    [
        ("LP", (4.5, 6.5), (4, 6, 4)),
        ("PS", (6.5, 2.5), (10, 6, 2)),
        ("SL", (2.5, 4.5), (4, 8, 2)),
    ],
)
def test_click_in_any_view_updates_shared_intersection_and_slice_controls(
    window, name, clicked, expected
):
    window.observe_radio.setChecked(True)
    QApplication.processEvents()
    canvas = _canvas(window, name)
    viewport_point = canvas.mapFromScene(QPointF(*clicked))
    QTest.mouseClick(canvas.viewport(), Qt.MouseButton.LeftButton, pos=viewport_point)
    assert window.observation_position == expected
    assert window.current_slice == expected[2]
    assert window.slice_slider.value() == expected[2]
    assert window.slice_spin.value() == expected[2]
    assert window.observation_windows["PS"].slice_spin.value() == expected[0]
    assert window.observation_windows["SL"].slice_spin.value() == expected[1]
    for plane_name, plane in OBSERVATION_PLANES.items():
        displayed = _canvas(window, plane_name)
        assert displayed._crosshair_position == QPointF(
            expected[plane.horizontal_axis] + 0.5,
            expected[plane.vertical_axis] + 0.5,
        )
        assert not displayed._draft_points


def test_sequential_navigation_keeps_all_three_views_synchronized(window):
    window.observe_radio.setChecked(True)
    window._observation_clicked("LP", QPointF(4.5, 6.5))
    window._observation_clicked("PS", QPointF(9.5, 2.5))
    assert window.observation_position == (4, 9, 2)
    window._observation_clicked("SL", QPointF(7.5, 11.5))
    assert window.observation_position == (11, 9, 7)
    window.slice_slider.setValue(5)
    assert window.observation_position == (11, 9, 5)
    window.observation_windows["PS"].slice_spin.setValue(3)
    window.observation_windows["SL"].slice_spin.setValue(2)
    assert window.observation_position == (3, 2, 5)


@pytest.mark.parametrize("name", ["LP", "PS", "SL"])
def test_crosshair_and_reference_line_colors_identify_the_same_planes(window, name):
    window.observe_radio.setChecked(True)
    plane = OBSERVATION_PLANES[name]
    canvas = _canvas(window, name)
    assert canvas._crosshair_colors == (
        AXIS_COLORS[plane.horizontal_axis],
        AXIS_COLORS[plane.vertical_axis],
        plane.color,
    )
    assert len(set(canvas._crosshair_colors)) == 3
    assert not canvas.grab().isNull()


@pytest.mark.parametrize("index", [1, 2, 4, 6, 7])
def test_companion_masks_match_full_export_volume_including_erasures_and_empty_slices(
    window, index
):
    expected = _seed_masks(window)
    window.observe_radio.setChecked(True)
    window._observation_clicked("LP", QPointF(5.5, 5.5))
    window.set_slice(index)
    np.testing.assert_array_equal(window._observation_mask, expected)
    for name in ("PS", "SL"):
        plane = OBSERVATION_PLANES[name]
        canvas = _canvas(window, name)
        np.testing.assert_array_equal(
            _overlay_mask(canvas), plane.section(expected, window.observation_position)
        )
        assert not canvas._handles
        assert not canvas._polygon_items
    if index in (1, 7):
        assert window.canvas._handles
        assert window.canvas._interpolation_item is None
    elif index == 4:
        assert not window.canvas._handles
        assert window.canvas._interpolation_item is None
    else:
        np.testing.assert_array_equal(
            _overlay_mask(window.canvas), expected[:, :, index].T
        )


def test_observation_precomputes_mask_once_and_reuses_it_for_navigation_and_contrast(
    window, monkeypatch
):
    _seed_masks(window)
    calls = []
    original = AnnotationProject.to_mask

    def tracked(project, *, interpolate=True):
        calls.append(interpolate)
        assert not window.isEnabled()
        assert not window.autosave_timer.isActive()
        return original(project, interpolate=interpolate)

    monkeypatch.setattr(AnnotationProject, "to_mask", tracked)
    window.observe_radio.setChecked(True)
    assert calls == [True]

    def unexpected(*args, **kwargs):
        pytest.fail("Navigation must not recompute interpolation")

    monkeypatch.setattr(AnnotationProject, "interpolated_plane", unexpected)
    window._observation_clicked("PS", QPointF(5.5, 6.5))
    window.set_slice(3)
    window.level_spin.setValue(window.level_spin.value() + 1)
    window.width_spin.setValue(window.width_spin.value() + 10)
    window.set_language("en")
    assert calls == [True]
    assert "Read-only" in window.observation_windows["PS"].windowTitle()


def test_read_only_blocks_edit_buttons_shortcuts_direct_methods_and_handle_drags(
    window,
):
    _seed_masks(window)
    window.set_slice(1)
    window.observe_radio.setChecked(True)
    original = window.project_path.read_bytes()
    original_counter = window.project.edit_counter
    original_polygons = list(window.project.annotation(1).polygons)
    handle_position = window.canvas.mapFromScene(window.canvas._handles[0].pos())
    QTest.mousePress(
        window.canvas.viewport(), Qt.MouseButton.LeftButton, pos=handle_position
    )
    QTest.mouseMove(
        window.canvas.viewport(),
        handle_position
        + window.canvas.mapFromScene(QPointF(1, 1))
        - window.canvas.mapFromScene(QPointF(0, 0)),
    )
    QTest.mouseRelease(window.canvas.viewport(), Qt.MouseButton.LeftButton)
    for key, modifier in (
        (Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier),
        (Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier),
        (Qt.Key.Key_C, Qt.KeyboardModifier.NoModifier),
        (Qt.Key.Key_M, Qt.KeyboardModifier.NoModifier),
    ):
        QTest.keyClick(window, key, modifier)
    window.add_polygon([(1, 1), (5, 1), (3, 5)], "add")
    window.update_polygon(0, [(1, 1), (5, 1), (3, 5)])
    window.delete_last_edited_polygon()
    window.clear_current_slice()
    window.copy_previous_slice()
    window.set_slice_completed(True)
    window.set_force_empty(True)
    window.toggle_completed()
    window.canvas.finish_polygon()
    assert window.project.edit_counter == original_counter
    assert window.project.annotation(1).polygons == original_polygons
    assert not window.project.annotation(1).completed
    assert not window.project.annotation(1).force_empty
    assert window.project_path.read_bytes() == original
    assert not window.canvas._draft_points
    assert window.canvas._dragging_handle is None


def test_companion_windows_are_nonmodal_unclosable_and_follow_mode_and_parent(window):
    window.observe_radio.setChecked(True)
    QApplication.processEvents()
    views = tuple(window.observation_windows.values())
    for view in views:
        assert view.isVisible()
        assert view.parentWidget() is window
        assert view.windowModality() == Qt.WindowModality.NonModal
        assert not (view.windowFlags() & Qt.WindowType.WindowCloseButtonHint)
        assert not view.close()
        assert view.isVisible()
    window.hide()
    assert all(not view.isVisible() for view in views)
    window.show()
    assert all(view.isVisible() for view in views)
    window.erase_radio.setChecked(True)
    assert not window.read_only
    assert not window.canvas.read_only
    assert window.canvas._operation == "erase"
    assert window.canvas._crosshair_position is None
    assert all(not view.isVisible() for view in views)
    assert all(control.isEnabled() for control in window.editing_controls)
    assert all(shortcut.isEnabled() for shortcut in window.editing_shortcuts)
    window.observe_radio.setChecked(True)
    assert tuple(window.observation_windows.values()) == views
    window.close()
    assert all(not view.isVisible() for view in views)


def test_observation_temporarily_enables_interpolation_and_restores_prior_preference(
    window,
):
    window.show_interpolation.setChecked(False)
    window.observe_radio.setChecked(True)
    assert window.show_interpolation.isChecked()
    assert not window.show_interpolation.isEnabled()
    window.add_radio.setChecked(True)
    assert not window.show_interpolation.isChecked()
    assert window.show_interpolation.isEnabled()


def test_reentering_observation_rebuilds_mask_after_editing(window):
    window.observe_radio.setChecked(True)
    assert not window._observation_mask.any()
    window.add_radio.setChecked(True)
    window.add_polygon([(2, 2), (9, 2), (5, 9)], "add")
    window.observe_radio.setChecked(True)
    assert window._observation_mask.any()


def test_observation_handles_loading_new_volume_with_different_dimensions(
    window, tmp_path
):
    _seed_masks(window)
    window.observe_radio.setChecked(True)
    old_views = tuple(window.observation_windows.values())
    _load_volume(window, tmp_path / "second.nii.gz", (5, 7, 3))
    assert window.observation_position == (2, 3, 1)
    assert window._observation_mask.shape == (5, 7, 3)
    assert not window._observation_mask.any()
    assert window.current_slice == 1
    assert window.observation_windows["PS"].slice_spin.maximum() == 4
    assert window.observation_windows["SL"].slice_spin.maximum() == 6
    assert tuple(window.observation_windows.values()) == old_views
    assert all(not control.isEnabled() for control in window.editing_controls)


def test_loading_disables_companion_views_and_restores_read_only_state(window):
    window.observe_radio.setChecked(True)
    window._show_loading(window.current_source)
    assert all(not view.isEnabled() for view in window.observation_windows.values())
    window._finish_loading_ui()
    assert all(view.isEnabled() for view in window.observation_windows.values())
    assert all(not control.isEnabled() for control in window.editing_controls)


def test_failed_mask_preparation_during_reload_preserves_previous_volume(
    window, tmp_path, monkeypatch
):
    _seed_masks(window)
    window.observe_radio.setChecked(True)
    old_volume = window.volume
    old_project = window.project
    old_mask = window._observation_mask
    old_position = window.observation_position

    def fail(*args, **kwargs):
        raise MemoryError("cannot allocate replacement mask")

    monkeypatch.setattr(AnnotationProject, "to_mask", fail)
    _load_volume(window, tmp_path / "failed-replacement.nii.gz", (5, 7, 3))
    assert "cannot allocate replacement mask" in window._load_error
    assert window.volume is old_volume
    assert window.project is old_project
    assert window._observation_mask is old_mask
    assert window.observation_position == old_position
    assert window.read_only
    window._observation_clicked("PS", QPointF(3.5, 6.5))
    assert window.observation_position == (old_position[0], 3, 6)


def test_failed_mask_preparation_restores_editing_and_does_not_leave_disabled_ui(
    window, monkeypatch
):
    errors = []

    def fail(*args, **kwargs):
        raise MemoryError("synthetic mask allocation failure")

    monkeypatch.setattr(AnnotationProject, "to_mask", fail)
    monkeypatch.setattr(QMessageBox, "critical", lambda *args: errors.append(args[2]))
    window.erase_radio.setChecked(True)
    window.observe_radio.setChecked(True)
    assert errors == ["synthetic mask allocation failure"]
    assert not window.read_only
    assert window.erase_radio.isChecked()
    assert window.canvas._operation == "erase"
    assert window.isEnabled()
    assert window.autosave_timer.isActive()
    assert not window._closing_polygon
    assert not window.observation_windows


def test_single_voxel_volume_has_valid_intersection_and_sections(window, tmp_path):
    _load_volume(window, tmp_path / "single.nii.gz", (1, 1, 1))
    window.observe_radio.setChecked(True)
    assert window.observation_position == (0, 0, 0)
    for name in OBSERVATION_PLANES:
        canvas = _canvas(window, name)
        assert canvas._image_rect.width() == 1
        assert canvas._image_rect.height() == 1
        assert canvas._crosshair_position == QPointF(0.5, 0.5)
