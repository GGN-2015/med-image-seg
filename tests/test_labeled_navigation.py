from __future__ import annotations

import os

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QPointF, Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox

from med_image_seg.annotation import AnnotationProject, PolygonAnnotation
from med_image_seg.gui import AnnotationMainWindow
from med_image_seg.io import MedicalVolume
from med_image_seg.localization import translate
from med_image_seg.sources import ImageSource


@pytest.fixture
def window(tmp_path):
    app = QApplication.instance() or QApplication([])
    image = tmp_path / "scan.nii"
    image.write_bytes(b"synthetic-image")
    source = ImageSource.from_path(image)
    instance = AnnotationMainWindow(sources=[], language="en")
    instance._loading_source = source
    instance.volume_loaded(
        MedicalVolume(
            data=np.arange(20 * 16 * 12, dtype=np.float32).reshape(20, 16, 12),
            spacing_mm=(0.8, 0.8, 0.8),
            origin_lps_mm=(0.0, 0.0, 0.0),
            metadata={},
            source=image,
        )
    )
    instance._finish_loading_ui()
    instance.show()
    app.processEvents()
    yield instance
    instance.close()
    app.processEvents()
    instance.deleteLater()
    app.processEvents()


def _seed(window, indices):
    for index in indices:
        window.project.add_polygon(
            index, PolygonAnnotation(points=((2, 2), (9, 2), (5, 10)))
        )
    window.commit_change()
    window.refresh_slice()


def _button(window, direction):
    return (
        window.previous_labeled_button if direction < 0 else window.next_labeled_button
    )


def test_labeled_buttons_sit_below_existing_buttons_without_misaligning_coverage(
    window,
):
    for top, bottom in (
        (window.previous_button, window.previous_labeled_button),
        (window.next_button, window.next_labeled_button),
    ):
        assert bottom.y() > top.y()
        assert bottom.x() == top.x()
        assert bottom.width() == top.width()
    assert window.mask_coverage_bar.x() == window.slice_slider.x()
    assert window.mask_coverage_bar.width() == window.slice_slider.width()
    assert window.previous_labeled_button.text() == "Prev labeled slice"
    assert window.next_labeled_button.text() == "Next labeled slice"
    window.set_language("zh")
    QApplication.processEvents()
    assert window.previous_labeled_button.text() == "上一标注层"
    assert window.next_labeled_button.text() == "下一标注层"
    assert window.previous_labeled_button.toolTip() == translate(
        "labeled_slice_tooltip", "zh"
    )
    assert window.mask_coverage_bar.x() == window.slice_slider.x()
    assert window.mask_coverage_bar.width() == window.slice_slider.width()


@pytest.mark.parametrize(
    "current,direction,expected",
    [(6, -1, 4), (6, 1, 7), (4, -1, 1), (4, 1, 7), (0, 1, 1), (11, -1, 9)],
)
def test_buttons_jump_to_nearest_strictly_earlier_or_later_polygon_slice(
    window, current, direction, expected
):
    _seed(window, (9, 1, 7, 4))
    window.set_slice(current)
    original = window.project_path.read_bytes()
    QTest.mouseClick(_button(window, direction), Qt.MouseButton.LeftButton)
    assert window.current_slice == expected
    assert window.slice_spin.value() == expected
    assert window.slice_slider.value() == expected
    assert window.canvas._handles
    assert window.project_path.read_bytes() == original


@pytest.mark.parametrize("direction, expected", [(-1, 1), (1, 10)])
def test_interpolation_and_empty_keyframe_or_review_slices_are_skipped(
    window, direction, expected
):
    _seed(window, (1, 10))
    window.project.set_completed(3, True)
    window.project.set_keyframe(5, True)
    window.project.set_force_empty(8, True)
    window.commit_change()
    window.set_slice(6)
    assert window.project.interpolation_bounds(6) is not None
    window.go_to_labeled_slice(direction)
    assert window.current_slice == expected


@pytest.mark.parametrize("source", ["manual", "prototype"])
@pytest.mark.parametrize("operation", ["add", "erase"])
def test_any_stored_polygon_counts_even_on_forced_empty_slice(
    window, source, operation
):
    window.project.add_polygon(
        9,
        PolygonAnnotation(
            points=((2, 2), (9, 2), (5, 10)), source=source, operation=operation
        ),
    )
    window.project.set_force_empty(9, True)
    window.commit_change()
    window.set_slice(6)
    assert not window.project.to_mask().any()
    window.go_to_labeled_slice(1)
    assert window.current_slice == 9


@pytest.mark.parametrize(
    "direction,labels",
    [(-1, ()), (1, ()), (-1, (6,)), (1, (6,)), (-1, (6, 11)), (1, (0, 6))],
)
def test_missing_target_shows_directional_message_without_wrapping_or_moving(
    window, monkeypatch, direction, labels
):
    _seed(window, labels)
    window.set_language("zh")
    window.set_slice(6)
    window.canvas._draft_points = [QPointF(3, 3), QPointF(7, 3)]
    messages = []
    monkeypatch.setattr(QMessageBox, "information", lambda *args: messages.append(args))
    QTest.mouseClick(_button(window, direction), Qt.MouseButton.LeftButton)
    assert len(messages) == 1
    assert messages[0][0] is window
    assert messages[0][2] == (
        "未找到上一个有标注的面。" if direction < 0 else "未找到下一个有标注的面。"
    )
    assert (
        window.current_slice
        == window.slice_slider.value()
        == window.slice_spin.value()
        == 6
    )
    assert len(window.canvas._draft_points) == 2


@pytest.mark.parametrize("direction", [-1, 1])
def test_missing_target_dialog_is_actually_modal(window, direction):
    window.set_language("zh")
    captured = []

    def dismiss():
        dialog = QApplication.activeModalWidget()
        if isinstance(dialog, QMessageBox):
            captured.append((dialog.isModal(), dialog.text(), dialog.parentWidget()))
            dialog.accept()

    QTimer.singleShot(0, dismiss)
    QTest.mouseClick(_button(window, direction), Qt.MouseButton.LeftButton)
    key = "previous_labeled_not_found" if direction < 0 else "next_labeled_not_found"
    assert captured == [(True, translate(key, "zh"), window)]


def test_number_switch_limits_navigation_to_active_annotation(window):
    _seed(window, (1, 9))
    window.set_annotation_index(2)
    _seed(window, (3, 10))
    window.set_slice(6)
    window.go_to_labeled_slice(-1)
    assert window.current_slice == 3
    window.set_annotation_index(0)
    window.set_slice(6)
    window.go_to_labeled_slice(-1)
    assert window.current_slice == 1
    window.go_to_labeled_slice(1)
    assert window.current_slice == 9


def test_labeled_navigation_works_in_observation_and_updates_cross_references(
    window, monkeypatch
):
    _seed(window, (1, 9))
    window.set_slice(5)
    window.observe_radio.setChecked(True)
    window._observation_clicked("LP", QPointF(5.5, 7.5))
    mask = window._observation_mask

    def no_recomputation(*args, **kwargs):
        pytest.fail("Labeled navigation must reuse the observation mask")

    monkeypatch.setattr(AnnotationProject, "to_mask", no_recomputation)
    assert window.previous_labeled_button.isEnabled()
    assert window.next_labeled_button.isEnabled()
    QTest.mouseClick(window.next_labeled_button, Qt.MouseButton.LeftButton)
    assert window.observation_position == (5, 7, 9)
    assert window.observation_windows["PS"].canvas._crosshair_position == QPointF(
        7.5, 9.5
    )
    assert window.observation_windows["SL"].canvas._crosshair_position == QPointF(
        9.5, 5.5
    )
    assert window._observation_mask is mask
    assert window.canvas.read_only
    assert window.canvas._handles
    assert all(not control.isEnabled() for control in window.editing_controls)


def test_labeled_navigation_is_unavailable_without_image_or_while_busy(
    window, monkeypatch
):
    app = QApplication.instance()
    empty = AnnotationMainWindow(sources=[])
    assert not empty.previous_labeled_button.isEnabled()
    assert not empty.next_labeled_button.isEnabled()

    def no_dialog(*args):
        pytest.fail("Navigation is unavailable and must not open a dialog")

    monkeypatch.setattr(QMessageBox, "information", no_dialog)
    empty.go_to_labeled_slice(-1)
    empty.go_to_labeled_slice(1)
    empty.close()
    app.processEvents()
    _seed(window, (1, 9))
    current = window.current_slice
    with window._polygon_busy_ui():
        assert not window.previous_labeled_button.isEnabled()
        assert not window.next_labeled_button.isEnabled()
        window.go_to_labeled_slice(1)
    assert window.current_slice == current
