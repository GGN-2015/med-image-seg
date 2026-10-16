from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QValidator
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QAbstractSpinBox, QApplication, QMessageBox

from med_image_seg.annotation import AnnotationProject, PolygonAnnotation
from med_image_seg.gui import AnnotationIndexSpinBox, AnnotationMainWindow
from med_image_seg.io import MedicalVolume, MedicalVolumeReader
from med_image_seg.localization import translate
from med_image_seg.observation import OBSERVATION_PLANES
from med_image_seg.sources import ImageSource


def _load_source(window, path, shape=(20, 16, 9)):
    path.write_bytes(b"synthetic-image")
    source = ImageSource.from_path(path)
    volume = MedicalVolume(
        data=np.arange(np.prod(shape), dtype=np.float32).reshape(shape),
        spacing_mm=(0.8, 0.8, 0.8),
        origin_lps_mm=(1.0, 2.0, 3.0),
        metadata={},
        source=source.path,
    )
    window._loading_source = source
    window.volume_loaded(volume)
    window._finish_loading_ui()
    return source


@pytest.fixture
def window(tmp_path):
    app = QApplication.instance() or QApplication([])
    instance = AnnotationMainWindow(sources=[], language="zh")
    _load_source(instance, tmp_path / "扫描.nii.gz")
    instance.show()
    app.processEvents()
    yield instance
    instance.close()
    app.processEvents()
    instance.deleteLater()
    app.processEvents()


def _polygon(offset=0):
    return [(2 + offset, 2), (9 + offset, 2), (5 + offset, 10)]


def _new_project(window):
    return AnnotationProject.create(
        image_id=window.current_source.source_id,
        source_fingerprint=window.current_source.fingerprint,
        volume=window.volume,
    )


def _assert_no_sidecars(path):
    assert all(
        not Path(f"{path}{suffix}").exists()
        for suffix in ("", ".bak", ".tmp", ".bak.tmp")
    )


def test_number_selector_defaults_to_zero_and_translates(window):
    assert window.annotation_index == 0
    assert window.annotation_index_spin.value() == 0
    assert window.annotation_index_label.text() == "标注编号"
    assert window.project_path == window.current_source.annotation_path
    assert window.project_path.is_file()
    window.set_language("en")
    assert window.annotation_index_label.text() == "Annotation number"
    assert "Numbered files with no polygons" in window.annotation_index_spin.toolTip()


def test_switching_numbers_keeps_projects_independent_without_reloading_image(
    window, monkeypatch
):
    window.set_slice(3)
    window.add_polygon(_polygon(), "add")
    zero_project = window.project
    zero_path = window.project_path
    volume = window.volume
    level, width = window.level_spin.value(), window.width_spin.value()

    def no_image_read(*args, **kwargs):
        pytest.fail("Changing annotation number must not reload the image")

    monkeypatch.setattr(MedicalVolumeReader, "read", no_image_read)
    window.annotation_index_spin.setValue(1)
    first_path = window.current_source.annotation_path_for_index(1)
    assert window.annotation_index == 1
    assert window.project is not zero_project
    assert window.project_path == first_path
    assert window.volume is volume
    assert window.current_slice == 3
    assert (window.level_spin.value(), window.width_spin.value()) == (level, width)
    assert not window.project.has_polygons
    assert not any(window.mask_coverage_bar.presence)
    _assert_no_sidecars(first_path)
    zero_bytes = zero_path.read_bytes()

    window.add_polygon(_polygon(5), "add")
    window.set_slice_completed(True)
    first_saved = AnnotationProject.load(first_path)
    assert first_saved.annotation(3).completed
    assert first_saved.annotation(3).polygons[0].points == tuple(_polygon(5))
    assert zero_path.read_bytes() == zero_bytes

    window.annotation_index_spin.setValue(0)
    assert window.project_path == zero_path
    assert window.project.annotation(3).polygons[0].points == tuple(_polygon())
    assert not window.project.annotation(3).completed
    assert window.canvas._handles
    window.annotation_index_spin.setValue(1)
    assert window.project.annotation(3).completed
    assert window.project.annotation(3).polygons[0].points == tuple(_polygon(5))


def test_number_input_commits_once_on_enter_and_supports_arrow_steps(
    window, monkeypatch
):
    opened = []
    original = window._open_annotation_project

    def tracked(source, volume, index):
        opened.append(index)
        return original(source, volume, index)

    monkeypatch.setattr(window, "_open_annotation_project", tracked)
    editor = window.annotation_index_spin.lineEdit()
    editor.setFocus()
    editor.selectAll()
    QTest.keyClicks(editor, "12")
    assert window.annotation_index == 0
    assert opened == []
    QTest.keyClick(editor, Qt.Key.Key_Return)
    assert opened == [12]
    assert window.annotation_index == 12
    QTest.keyClick(window.annotation_index_spin, Qt.Key.Key_Up)
    assert window.annotation_index == 13
    QTest.keyClick(window.annotation_index_spin, Qt.Key.Key_Down)
    assert window.annotation_index == 12
    window.annotation_index_spin.stepBy(-100)
    assert window.annotation_index == 0
    assert not (
        window.annotation_index_spin.stepEnabled()
        & QAbstractSpinBox.StepEnabledFlag.StepDownEnabled
    )


def test_number_input_supports_arbitrary_precision_and_rejects_negative_values(window):
    index = 10**35 + 7
    window.annotation_index_spin.setValue(index)
    assert window.annotation_index == index
    assert window.annotation_index_spin.value() == index
    assert window.project_path.name == f"扫描.med-image-seg-{index}.json"
    window.annotation_index_spin.stepBy(1)
    assert window.annotation_index == index + 1
    with pytest.raises(ValueError, match="nonnegative"):
        window.annotation_index_spin.setValue(-1)
    with pytest.raises(ValueError, match="nonnegative"):
        window.set_annotation_index(-1)
    assert window.annotation_index == index + 1
    state, _, _ = window.annotation_index_spin.validate("-1", 2)
    assert state == QValidator.State.Invalid
    state, _, _ = window.annotation_index_spin.validate("1.5", 3)
    assert state == QValidator.State.Invalid


def test_reselecting_active_number_does_not_reload_or_save(window, monkeypatch):
    active = window.project

    def unexpected(*args, **kwargs):
        pytest.fail("The active annotation should not be reloaded or saved")

    monkeypatch.setattr(window, "_open_annotation_project", unexpected)
    with monkeypatch.context() as patch:
        patch.setattr(AnnotationProject, "save", unexpected)
        assert window.set_annotation_index(0)
    assert window.project is active


@pytest.mark.parametrize(
    "action",
    [
        "add",
        "drag",
        "copy",
        "review",
        "force_empty",
        "unreview",
        "restore_interpolation",
    ],
)
def test_numbered_annotation_edits_save_immediately(window, monkeypatch, action):
    window.set_annotation_index(5)
    window.set_slice(1)
    window.add_polygon(_polygon(), "add")
    window.set_slice(7)
    window.add_polygon(_polygon(4), "add")
    window.set_slice(4)
    path = window.project_path
    previous = path.read_bytes()
    if action == "add":
        window.add_polygon(_polygon(2), "add")
    elif action == "drag":
        window.set_slice(1)
        window.update_polygon(0, _polygon(1))
    elif action == "copy":
        window.set_slice(2)
        window.copy_previous_slice()
    elif action == "review":
        window.set_slice_completed(True)
    elif action == "force_empty":
        window.set_force_empty(True)
    elif action == "unreview":
        window.set_slice_completed(True)
        window.set_slice_completed(False)
    elif action == "restore_interpolation":
        window.set_slice_completed(True)
        monkeypatch.setattr(
            QMessageBox, "question", lambda *args: QMessageBox.StandardButton.Yes
        )
        window.clear_current_slice()
    assert path.is_file()
    assert path.read_bytes() != previous
    restored = AnnotationProject.load(path)
    np.testing.assert_array_equal(restored.to_mask(), window.project.to_mask())
    assert restored.completed_count == window.project.completed_count
    assert restored.keyframe_indices == window.project.keyframe_indices
    assert not window._dirty
    assert Path(f"{path}.bak").is_file()


@pytest.mark.parametrize("action", ["undo", "clear", "copy_empty"])
def test_removing_last_polygon_removes_all_files_and_prevents_backup_resurrection(
    window, monkeypatch, action
):
    window.set_annotation_index(2)
    window.add_polygon(_polygon(), "add")
    window.set_slice_completed(True)
    path = window.project_path
    previous = path.read_bytes()
    assert Path(f"{path}.bak").is_file()
    for suffix in (".tmp", ".bak.tmp"):
        Path(f"{path}{suffix}").write_bytes(previous)
    monkeypatch.setattr(
        QMessageBox, "question", lambda *args: QMessageBox.StandardButton.Yes
    )
    if action == "undo":
        window.delete_last_edited_polygon()
    elif action == "clear":
        window.clear_current_slice()
    else:
        window.copy_previous_slice()
    assert not window.project.has_polygons
    _assert_no_sidecars(path)
    assert not window._dirty
    assert "不保留 JSON" in window.autosave_status.text()
    window.set_annotation_index(0)
    window.set_annotation_index(2)
    assert not window.project.has_polygons
    assert window.project.completed_count == 0
    assert window.project.keyframe_indices == ()
    _assert_no_sidecars(path)


def test_removing_one_slice_keeps_file_if_another_slice_has_polygons(window):
    window.set_annotation_index(1)
    window.set_slice(1)
    window.add_polygon(_polygon(), "add")
    window.set_slice(7)
    window.add_polygon(_polygon(3), "add")
    window.delete_last_edited_polygon()
    assert window.project_path.is_file()
    assert window.project.has_polygons
    assert AnnotationProject.load(window.project_path).annotation(1).polygons


@pytest.mark.parametrize("number", [0, 1])
def test_review_or_force_empty_without_polygons_only_persists_for_number_zero(
    window, number
):
    window.set_annotation_index(number)
    window.set_slice_completed(True)
    window.set_force_empty(True)
    path = window.project_path
    if number == 0:
        saved = AnnotationProject.load(path)
        assert saved.annotation(window.current_slice).completed
        assert saved.annotation(window.current_slice).force_empty
    else:
        _assert_no_sidecars(path)
    window.set_annotation_index(3)
    window.set_annotation_index(number)
    assert window.project.annotation(window.current_slice).completed == (number == 0)
    assert window.project.annotation(window.current_slice).force_empty == (number == 0)


def test_forced_empty_with_saved_polygons_keeps_numbered_file(window):
    window.set_annotation_index(1)
    window.add_polygon(_polygon(), "add")
    window.set_force_empty(True)
    assert not window.project.to_mask().any()
    assert window.project.has_polygons
    restored = AnnotationProject.load(window.project_path)
    assert restored.annotation(window.current_slice).polygons
    assert restored.annotation(window.current_slice).force_empty


def test_switching_closes_and_saves_draft_to_the_outgoing_number(window):
    old_path = window.project_path
    old_slice = window.current_slice
    window.canvas._draft_points = [QPointF(*point) for point in _polygon()]
    assert window.set_annotation_index(6)
    saved = AnnotationProject.load(old_path)
    assert saved.annotation(old_slice).polygons[0].points == tuple(_polygon())
    assert not window.project.has_polygons
    assert not window.canvas._draft_points


def test_old_save_failure_blocks_switch_and_restores_number_input(window, monkeypatch):
    old_project, old_path = window.project, window.project_path
    old_bytes = old_path.read_bytes()
    window._dirty = True
    errors = []

    def fail(*args, **kwargs):
        raise PermissionError("annotation is locked")

    with monkeypatch.context() as patch:
        patch.setattr(AnnotationProject, "save", fail)
        patch.setattr(QMessageBox, "critical", lambda *args: errors.append(args[2]))
        window.annotation_index_spin.setValue(1)
        assert window.annotation_index == 0
        assert window.annotation_index_spin.value() == 0
        assert window.project is old_project
        assert window.project_path == old_path
        assert window._dirty
        assert old_path.read_bytes() == old_bytes
        assert not window.current_source.annotation_path_for_index(1).exists()
    assert errors == ["annotation is locked"]


@pytest.mark.parametrize("failure", ["corrupt", "fingerprint", "geometry"])
def test_unreadable_or_mismatched_target_does_not_replace_active_project(
    window, monkeypatch, failure
):
    window.add_polygon(_polygon(), "add")
    old_project, old_path = window.project, window.project_path
    target = window.current_source.annotation_path_for_index(1)
    if failure == "corrupt":
        target.write_text("broken JSON", encoding="utf-8")
    else:
        project = _new_project(window)
        project.add_polygon(2, PolygonAnnotation(points=tuple(_polygon(3))))
        if failure == "fingerprint":
            project.source_fingerprint = "wrong-image"
        else:
            project.shape_lps = (30, 30, 30)
        project.save(target)
    target_bytes = target.read_bytes()
    errors = []
    monkeypatch.setattr(QMessageBox, "critical", lambda *args: errors.append(args[2]))
    window.annotation_index_spin.setValue(1)
    assert errors
    assert window.annotation_index == 0
    assert window.annotation_index_spin.value() == 0
    assert window.project is old_project
    assert window.project_path == old_path
    assert target.read_bytes() == target_bytes
    assert window.isEnabled()
    assert window.autosave_timer.isActive()
    assert not window._switching_annotation


def test_numbered_project_can_recover_its_own_backup(window):
    target = window.current_source.annotation_path_for_index(4)
    project = _new_project(window)
    project.add_polygon(2, PolygonAnnotation(points=tuple(_polygon(2))))
    project.save(target)
    project.save(target)
    target.write_text("broken", encoding="utf-8")
    assert window.set_annotation_index(4)
    assert window.project.annotation(2).polygons
    assert window.project_path == target
    window.set_slice(2)
    window.set_slice_completed(True)
    assert json.loads(target.read_text(encoding="utf-8"))["slices"]["2"]["completed"]


def test_deletion_failure_keeps_dirty_project_and_blocks_switch(window, monkeypatch):
    window.set_annotation_index(1)
    window.add_polygon(_polygon(), "add")
    window.set_slice_completed(True)
    path = window.project_path
    original = Path.unlink
    errors = []

    def fail_primary(candidate, *args, **kwargs):
        if candidate == path:
            raise PermissionError("cannot remove empty annotation")
        return original(candidate, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "unlink", fail_primary)
        patch.setattr(QMessageBox, "critical", lambda *args: errors.append(args[2]))
        window.delete_last_edited_polygon()
        assert not window.project.has_polygons
        assert window._dirty
        assert not window.set_annotation_index(2)
        assert window.annotation_index == 1
        assert window.annotation_index_spin.value() == 1
        assert path.is_file()
    assert errors == ["cannot remove empty annotation"]
    window.autosave_if_needed()
    _assert_no_sidecars(path)
    assert not window._dirty


def test_switch_in_observation_rebuilds_all_masks_and_preserves_intersection(window):
    for index in (1, 7):
        window.set_slice(index)
        window.add_polygon(_polygon(), "add")
    project = _new_project(window)
    for index in (2, 8):
        project.add_polygon(index, PolygonAnnotation(points=tuple(_polygon(6))))
    project.set_force_empty(5, True)
    project.save(window.current_source.annotation_path_for_index(1))
    expected = project.to_mask()
    window.set_slice(3)
    window.observe_radio.setChecked(True)
    window._observation_clicked("LP", QPointF(11.5, 6.5))
    position = window.observation_position
    views = tuple(window.observation_windows.values())
    old_mask = window._observation_mask.copy()
    assert window.annotation_index_spin.isEnabled()
    window.annotation_index_spin.setValue(1)
    assert window.read_only
    assert window.observation_position == position
    assert tuple(window.observation_windows.values()) == views
    assert all(view.isVisible() for view in views)
    assert all(not control.isEnabled() for control in window.editing_controls)
    np.testing.assert_array_equal(window._observation_mask, expected)
    assert not np.array_equal(old_mask, window._observation_mask)
    np.testing.assert_array_equal(
        window.mask_coverage_bar.presence, expected.any(axis=(0, 1))
    )
    for view in views:
        plane = OBSERVATION_PLANES[view.plane.name]
        assert view.canvas._crosshair_position == QPointF(
            position[plane.horizontal_axis] + 0.5, position[plane.vertical_axis] + 0.5
        )
        assert view.canvas._interpolation_item is not None


def test_selected_number_is_retained_when_loading_another_image(window, tmp_path):
    window.set_annotation_index(3)
    window.add_polygon(_polygon(), "add")
    old_path = window.project_path
    old_bytes = old_path.read_bytes()
    source = _load_source(window, tmp_path / "second.nii", (15, 12, 7))
    assert window.annotation_index == 3
    assert window.annotation_index_spin.value() == 3
    assert window.project_path == source.annotation_path_for_index(3)
    assert not source.annotation_path.exists()
    assert not window.project.has_polygons
    _assert_no_sidecars(window.project_path)
    window.add_polygon(_polygon(), "add")
    assert window.project_path.is_file()
    assert old_path.read_bytes() == old_bytes


@pytest.mark.parametrize("empty", [True, False])
def test_json_export_uses_active_number_and_respects_empty_file_policy(
    window, monkeypatch, empty
):
    window.set_annotation_index(7)
    if not empty:
        window.add_polygon(_polygon(), "add")
    messages = []
    monkeypatch.setattr(
        QMessageBox, "information", lambda *args: messages.append(args[2])
    )
    window.export_annotations()
    assert messages
    assert str(window.project_path) in messages[0]
    assert window.project_path.name == "扫描.med-image-seg-7.json"
    if empty:
        _assert_no_sidecars(window.project_path)
        assert "不导出空文件" in messages[0]
    else:
        assert window.project_path.is_file()
        assert messages[0] == translate(
            "export_annotations_complete_message", "zh", path=window.project_path
        )


def test_index_can_be_set_before_loading_first_image(tmp_path):
    app = QApplication.instance() or QApplication([])
    window = AnnotationMainWindow(sources=[])
    assert not window.annotation_index_spin.isEnabled()
    assert window.set_annotation_index(10)
    _load_source(window, tmp_path / "scan.nii")
    assert window.project_path.name == "scan.med-image-seg-10.json"
    assert window.annotation_index_spin.value() == 10
    _assert_no_sidecars(window.project_path)
    window.close()
    app.processEvents()


def test_blank_number_input_restores_active_value(window):
    window.set_annotation_index(3)
    editor = window.annotation_index_spin.lineEdit()
    editor.selectAll()
    QTest.keyClick(editor, Qt.Key.Key_Backspace)
    QTest.keyClick(editor, Qt.Key.Key_Return)
    assert window.annotation_index == 3
    assert window.annotation_index_spin.value() == 3
    assert editor.text() == "3"


def test_spin_box_read_only_state_disables_arrows():
    app = QApplication.instance() or QApplication([])
    spin = AnnotationIndexSpinBox()
    spin.setReadOnly(True)
    assert spin.stepEnabled() == QAbstractSpinBox.StepEnabledFlag.StepNone
    spin.close()
    app.processEvents()


def test_loading_image_opens_selected_existing_number_and_defaults_to_zero(window):
    source, volume = window.current_source, window.volume
    for number, offset in ((0, 0), (2, 5)):
        project = _new_project(window)
        project.add_polygon(3, PolygonAnnotation(points=tuple(_polygon(offset))))
        project.save(source.annotation_path_for_index(number))
    window._loading_source = source
    window.volume_loaded(volume)
    assert window.annotation_index == 0
    assert window.project.annotation(3).polygons[0].points == tuple(_polygon())
    window.set_annotation_index(2)
    window._loading_source = source
    window.volume_loaded(volume)
    assert window.annotation_index_spin.value() == 2
    assert window.project_path == source.annotation_path_for_index(2)
    assert window.project.annotation(3).polygons[0].points == tuple(_polygon(5))


def test_empty_numbered_backup_is_removed_when_opened_without_primary(window):
    path = window.current_source.annotation_path_for_index(2)
    project = _new_project(window)
    project.set_completed(3, True)
    project.save(path)
    project.save(path)
    path.unlink()
    assert Path(f"{path}.bak").is_file()
    assert window.set_annotation_index(2)
    assert window.project.annotation(3).completed
    _assert_no_sidecars(path)


def test_mask_failure_during_number_switch_preserves_observation_views(
    window, monkeypatch
):
    window.add_polygon(_polygon(), "add")
    target = window.current_source.annotation_path_for_index(2)
    project = _new_project(window)
    project.add_polygon(3, PolygonAnnotation(points=tuple(_polygon(5))))
    project.save(target)
    window.observe_radio.setChecked(True)
    original_project, original_mask = window.project, window._observation_mask
    original_position = window.observation_position
    original_path = window.project_path
    errors = []

    def fail(*args, **kwargs):
        assert not window.isEnabled()
        assert all(not view.isEnabled() for view in window.observation_windows.values())
        raise MemoryError("mask allocation failed")

    monkeypatch.setattr(AnnotationProject, "to_mask", fail)
    monkeypatch.setattr(QMessageBox, "critical", lambda *args: errors.append(args[2]))
    assert not window.set_annotation_index(2)
    assert errors == ["mask allocation failed"]
    assert window.project is original_project
    assert window._observation_mask is original_mask
    assert window.project_path == original_path
    assert window.observation_position == original_position
    assert window.annotation_index == window.annotation_index_spin.value() == 0
    assert window.read_only
    assert all(view.isEnabled() for view in window.observation_windows.values())
    assert all(not control.isEnabled() for control in window.editing_controls)
