from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QMessageBox,
    QSlider,
    QStyle,
    QStyleFactory,
    QStyleOptionSlider,
    QWidget,
)

from med_image_seg.annotation import AnnotationProject, PolygonAnnotation
from med_image_seg.gui import AnnotationMainWindow, MaskCoverageBar
from med_image_seg.io import MedicalVolume
from med_image_seg.localization import translate
from med_image_seg.sources import ImageSource


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def _load_source(window: AnnotationMainWindow, path: Path) -> ImageSource:
    path.write_bytes(b"synthetic-image")
    source = ImageSource.from_path(path)
    volume = MedicalVolume(
        data=np.arange(20 * 18 * 5, dtype=np.float32).reshape(20, 18, 5),
        spacing_mm=(0.8, 0.8, 0.8),
        origin_lps_mm=(0.0, 0.0, 0.0),
        metadata={},
        source=source.path,
    )
    window._loading_source = source
    window.volume_loaded(volume)
    window._finish_loading_ui()
    return source


@pytest.mark.parametrize("style_name", ["Fusion", "Windows"])
@pytest.mark.parametrize("depth", [1, 7, 510])
@pytest.mark.parametrize("rtl", [False, True])
@pytest.mark.parametrize("inverted", [False, True])
def test_coverage_centers_match_native_slider_for_every_slice_after_resize(
    style_name: str, depth: int, rtl: bool, inverted: bool
) -> None:
    app = _app()
    holder = QWidget()
    grid = QGridLayout(holder)
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(0, depth - 1)
    slider.setInvertedAppearance(inverted)
    style = QStyleFactory.create(style_name)
    assert style is not None
    style.setParent(slider)
    slider.setStyle(style)
    indicator = MaskCoverageBar(slider)
    indicator.set_presence([False] * depth)
    grid.addWidget(slider, 0, 0)
    grid.addWidget(indicator, 1, 0)
    holder.setLayoutDirection(
        Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight
    )
    try:
        holder.show()
        for width in (151, 801):
            holder.resize(width, 70)
            app.processEvents()
            assert indicator.width() == slider.width()
            assert (
                indicator.mapToGlobal(QPoint(0, 0)).x()
                == slider.mapToGlobal(QPoint(0, 0)).x()
            )
            centers = indicator.slice_centers()
            assert len(centers) == depth
            for slice_index in range(depth):
                slider.setValue(slice_index)
                option = QStyleOptionSlider()
                slider.initStyleOption(option)
                handle = slider.style().subControlRect(
                    QStyle.ComplexControl.CC_Slider,
                    option,
                    QStyle.SubControl.SC_SliderHandle,
                    slider,
                )
                actual_center = indicator.mapFromGlobal(
                    slider.mapToGlobal(handle.center())
                ).x()
                assert centers[slice_index] == actual_center
    finally:
        holder.close()


@pytest.mark.parametrize("inverted", [False, True])
def test_coverage_paints_separate_intervals_and_cannot_change_slider(
    inverted: bool,
) -> None:
    app = _app()
    holder = QWidget()
    grid = QGridLayout(holder)
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(0, 6)
    slider.setValue(3)
    slider.setInvertedAppearance(inverted)
    indicator = MaskCoverageBar(slider)
    presence = (True, True, False, True, False, True, True)
    indicator.set_presence(presence)
    grid.addWidget(slider, 0, 0)
    grid.addWidget(indicator, 1, 0)
    holder.resize(501, 70)
    holder.show()
    app.processEvents()
    try:
        image = indicator.grab().toImage()
        ratio = image.devicePixelRatio()
        for present, center in zip(presence, indicator.slice_centers(), strict=True):
            pixel_color = image.pixelColor(
                int(center * ratio), int(indicator.height() / 2 * ratio)
            )
            assert pixel_color.name() == ("#00b878" if present else "#c7ccd2")
        QTest.mousePress(indicator, Qt.MouseButton.LeftButton, pos=QPoint(10, 5))
        QTest.mouseMove(indicator, QPoint(indicator.width() - 10, 5))
        QTest.mouseRelease(
            indicator,
            Qt.MouseButton.LeftButton,
            pos=QPoint(indicator.width() - 10, 5),
        )
        app.processEvents()
        assert slider.value() == 3
        assert indicator.presence == presence
        assert indicator.focusPolicy() == Qt.FocusPolicy.NoFocus
    finally:
        holder.close()


def test_window_coverage_tracks_edits_interpolation_and_forced_empty_slices(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = _app()
    window = AnnotationMainWindow(sources=[])
    source = _load_source(window, tmp_path / "scan.nii.gz")
    window.show()
    try:
        assert window.mask_coverage_bar.presence == (False,) * 5
        for slice_index in (0, 4):
            window.set_slice(slice_index)
            window.add_polygon([(2, 2), (10, 2), (10, 10), (2, 10)], "add")
        assert window.mask_coverage_bar.presence == (True,) * 5
        window.set_slice(2)
        window.set_force_empty(True)
        assert not window.mask_coverage_bar.presence[2]
        assert window.project is not None
        np.testing.assert_array_equal(
            window.mask_coverage_bar.presence, window.project.to_mask().any((0, 1))
        )
        window.set_force_empty(False)
        assert window.mask_coverage_bar.presence == (True,) * 5
        window.set_slice_completed(True)
        assert not window.mask_coverage_bar.presence[2]
        window.set_slice_completed(False)
        assert not window.mask_coverage_bar.presence[2]
        monkeypatch.setattr(
            QMessageBox, "question", lambda *_args: QMessageBox.StandardButton.Yes
        )
        window.clear_current_slice()
        assert window.mask_coverage_bar.presence == (True,) * 5
        window.set_slice(0)
        window.add_polygon([(2, 2), (10, 2), (10, 10), (2, 10)], "erase")
        assert not window.mask_coverage_bar.presence[0]
        window.delete_last_edited_polygon()
        assert window.mask_coverage_bar.presence == (True,) * 5
        window.set_language("zh")
        app.processEvents()
        assert window.mask_coverage_bar.accessibleName() == translate(
            "mask_coverage_name", "zh"
        )
        assert window.mask_coverage_bar.toolTip() == translate(
            "mask_coverage_tooltip", "zh"
        )
        assert window.mask_coverage_bar.width() == window.slice_slider.width()
        assert window.mask_coverage_bar.x() == window.slice_slider.x()
        assert window.mask_coverage_bar.y() > window.slice_slider.y()
        assert source.annotation_path.is_file()

        _load_source(window, tmp_path / "second.nii.gz")
        assert window.mask_coverage_bar.presence == (False,) * 5
    finally:
        window.close()


def test_coverage_is_cached_during_navigation_and_preview_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = _app()
    window = AnnotationMainWindow(sources=[])
    _load_source(window, tmp_path / "scan.nii.gz")
    for slice_index in (0, 4):
        window.set_slice(slice_index)
        window.add_polygon([(2, 2), (10, 2), (10, 10), (2, 10)], "add")

    def unexpected_recomputation(*_args, **_kwargs) -> None:
        pytest.fail("navigation and display settings must not recalculate coverage")

    monkeypatch.setattr(AnnotationProject, "mask_presence", unexpected_recomputation)
    try:
        window.set_slice(2)
        window.show_interpolation.setChecked(False)
        window.level_spin.setValue(window.level_spin.value() + 1)
        window.width_spin.setValue(window.width_spin.value() + 1)
        window.refresh_slice()
        app.processEvents()
        assert window.mask_coverage_bar.presence == (True,) * 5
    finally:
        window.close()


def test_loaded_annotation_populates_coverage_without_allocating_full_mask(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = _app()
    window = AnnotationMainWindow(sources=[])
    source = _load_source(window, tmp_path / "scan.nii.gz")
    assert window.project is not None
    polygon = PolygonAnnotation(points=((2, 2), (10, 2), (10, 10), (2, 10)))
    for slice_index in (0, 1, 3, 4):
        window.project.add_polygon(slice_index, polygon)
    window.project.set_force_empty(2, True)
    window.project.save(source.annotation_path)

    def unexpected_volume(*_args, **_kwargs) -> None:
        pytest.fail("coverage must not allocate a full 3-D mask")

    monkeypatch.setattr(AnnotationProject, "to_mask", unexpected_volume)
    try:
        assert window.volume is not None
        window._loading_source = source
        window.volume_loaded(window.volume)
        app.processEvents()
        assert window.mask_coverage_bar.presence == (True, True, False, True, True)
    finally:
        window.close()
