from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, QThread, QTimer, SignalInstance
from PySide6.QtGui import QAction, QShortcut
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGraphicsEllipseItem,
    QGraphicsPathItem,
    QGraphicsPixmapItem,
    QGraphicsPolygonItem,
    QGraphicsView,
    QGroupBox,
    QLabel,
    QListWidget,
    QMainWindow,
    QProgressBar,
    QProgressDialog,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QSplitter,
    QToolBar,
)
from pytest import MonkeyPatch

from med_image_seg.Abstract.Presentation.Canvas import (
    T_MutableSliceCanvas,
    T_MutableVertexHandle,
)
from med_image_seg.Abstract.Presentation.Loading import (
    T_MutableExternalMaskLoadThread,
    T_MutableVolumeLoadThread,
)
from med_image_seg.Abstract.Presentation.Navigation import (
    T_MutableAnnotationIndexSpinBox,
    T_MutableMaskCoverageBar,
)
from med_image_seg.Abstract.Presentation.Observation import (
    T_MutableOrthogonalSliceWindow,
)

from ...Abstract.Navigation.T_TestMaskCoverage import T_TestMaskCoverage

if TYPE_CHECKING:
    from med_image_seg.Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
    from med_image_seg.Abstract.Presentation.Window import (
        T_MutableAnnotationMainWindow,
    )
    from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath
from typing import final

import numpy as np
import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QGridLayout,
    QMessageBox,
    QSlider,
    QStyle,
    QStyleFactory,
    QStyleOptionSlider,
    QWidget,
)


# 验证掩码区间条的显示、层号对齐和计算缓存。
@final
class C_TestMaskCoverage(T_TestMaskCoverage[MonkeyPatch]):
    # 为当前测试类配置离屏 Qt 环境。
    @pytest.fixture(autouse=True, name="configure_environment")
    def _configure_environment_fixture(self) -> None:
        from ..Environment.C_TestEnvironment import C_TestEnvironment

        C_TestEnvironment().configure()

    # 复用或创建 QApplication，供测试驱动界面事件。
    def _app(self) -> QApplication:
        from .C_MaskCoverageFixtures import C_MaskCoverageFixtures

        return C_MaskCoverageFixtures().app()

    # 启动影像读取前保存当前项目，避免切换来源时丢失标注。
    def _load_source(
        self,
        window: T_MutableAnnotationMainWindow[
            QMainWindow,
            QTimer,
            QToolBar,
            QAction,
            QLabel,
            QPushButton,
            QComboBox,
            QSplitter,
            QListWidget,
            QDoubleSpinBox,
            QSlider,
            QSpinBox,
            QGroupBox,
            QRadioButton,
            QCheckBox,
            QProgressBar,
            QProgressDialog,
            QShortcut,
            QWidget,
            QButtonGroup,
            T_MutableSliceCanvas[
                QGraphicsView,
                QPointF,
                QRectF,
                QGraphicsPixmapItem,
                QGraphicsPathItem,
                QGraphicsPolygonItem,
                T_MutableVertexHandle[QGraphicsEllipseItem],
                SignalInstance,
            ],
            T_MutableOrthogonalSliceWindow[
                QWidget,
                QLabel,
                T_MutableSliceCanvas[
                    QGraphicsView,
                    QPointF,
                    QRectF,
                    QGraphicsPixmapItem,
                    QGraphicsPathItem,
                    QGraphicsPolygonItem,
                    T_MutableVertexHandle[QGraphicsEllipseItem],
                    SignalInstance,
                ],
                QSpinBox,
                SignalInstance,
            ],
            T_MutableAnnotationIndexSpinBox[QAbstractSpinBox, SignalInstance],
            T_MutableMaskCoverageBar[QWidget, QSlider],
            T_MutableVolumeLoadThread[QThread, SignalInstance],
            T_MutableExternalMaskLoadThread[QThread, SignalInstance],
            QPointF,
        ],
        path: I_FilePath,
    ) -> I_ImageSource:
        from .C_MaskCoverageFixtures import C_MaskCoverageFixtures

        return C_MaskCoverageFixtures().load_source(window, path)

    # 改变窗口尺寸，逐层核对区间条中心与原生滑块位置一致。
    @pytest.mark.parametrize("style_name", ["Fusion", "Windows"])
    @pytest.mark.parametrize("depth", [1, 7, 510])
    @pytest.mark.parametrize("rtl", [False, True])
    @pytest.mark.parametrize("inverted", [False, True])
    def test_coverage_centers_match_native_slider_for_every_slice_after_resize(
        self, style_name: str, depth: int, rtl: bool, inverted: bool
    ) -> None:
        from med_image_seg.Concrete.Presentation.Navigation import (
            C_Qt_MaskCoverageBar,
        )

        from .C_MaskCoverageFixtures import C_MaskCoverageFixtures

        app = C_MaskCoverageFixtures().app()
        holder = QWidget()
        grid = QGridLayout(holder)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, depth - 1)
        slider.setInvertedAppearance(inverted)
        style = QStyleFactory.create(style_name)
        assert style is not None
        style.setParent(slider)
        slider.setStyle(style)
        indicator = C_Qt_MaskCoverageBar(slider)
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

    # 验证分段区间正确着色，点击区间条不会改变切片滑块。
    @pytest.mark.parametrize("inverted", [False, True])
    def test_coverage_paints_separate_intervals_and_cannot_change_slider(
        self, inverted: bool
    ) -> None:
        from med_image_seg.Concrete.Presentation.Navigation import (
            C_Qt_MaskCoverageBar,
        )

        from .C_MaskCoverageFixtures import C_MaskCoverageFixtures

        app = C_MaskCoverageFixtures().app()
        holder = QWidget()
        grid = QGridLayout(holder)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 6)
        slider.setValue(3)
        slider.setInvertedAppearance(inverted)
        indicator = C_Qt_MaskCoverageBar(slider)
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
            for present, center in zip(
                presence, indicator.slice_centers(), strict=True
            ):
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
            assert indicator.getPresence() == presence
            assert indicator.focusPolicy() == Qt.FocusPolicy.NoFocus
        finally:
            holder.close()

    # 逐次编辑、插值和强制空层，核验区间条及时反映实际掩码。
    def test_window_coverage_tracks_edits_interpolation_and_forced_empty_slices(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch
    ) -> None:
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Localization.C_Localizer import C_Localizer
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_MaskCoverageFixtures import C_MaskCoverageFixtures

        app = C_MaskCoverageFixtures().app()
        window = C_Qt_AnnotationMainWindow(sources=[])
        source = C_MaskCoverageFixtures().load_source(window, tmp_path / "scan.nii.gz")
        window.show()
        try:
            assert window.getMaskCoverageBar().getPresence() == (False,) * 5
            for slice_index in (0, 4):
                window.set_slice(slice_index)
                window.add_polygon(
                    C_PointList([(2, 2), (10, 2), (10, 10), (2, 10)]), "add"
                )
            assert window.getMaskCoverageBar().getPresence() == (True,) * 5
            window.set_slice(2)
            window.set_force_empty(True)
            assert not window.getMaskCoverageBar().getPresence()[2]
            assert window.getProject() is not None
            np.testing.assert_array_equal(
                window.getMaskCoverageBar().getPresence(),
                window.requireProject().to_mask().any((0, 1)),
            )
            window.set_force_empty(False)
            assert window.getMaskCoverageBar().getPresence() == (True,) * 5
            window.set_slice_completed(True)
            assert not window.getMaskCoverageBar().getPresence()[2]
            window.set_slice_completed(False)
            assert not window.getMaskCoverageBar().getPresence()[2]
            monkeypatch.setattr(
                QMessageBox, "question", lambda *_args: QMessageBox.StandardButton.Yes
            )
            window.clear_current_slice()
            assert window.getMaskCoverageBar().getPresence() == (True,) * 5
            window.set_slice(0)
            window.add_polygon(
                C_PointList([(2, 2), (10, 2), (10, 10), (2, 10)]), "erase"
            )
            assert not window.getMaskCoverageBar().getPresence()[0]
            window.delete_last_edited_polygon()
            assert window.getMaskCoverageBar().getPresence() == (True,) * 5
            window.set_language("zh")
            app.processEvents()
            assert (
                window.getMaskCoverageBar().getHost().accessibleName()
                == C_Localizer().translate("mask_coverage_name", "zh")
            )
            assert (
                window.getMaskCoverageBar().getHost().toolTip()
                == C_Localizer().translate("mask_coverage_tooltip", "zh")
            )
            assert (
                window.getMaskCoverageBar().getHost().width()
                == window.getSliceSlider().width()
            )
            assert (
                window.getMaskCoverageBar().getHost().x() == window.getSliceSlider().x()
            )
            assert (
                window.getMaskCoverageBar().getHost().y() > window.getSliceSlider().y()
            )
            assert source.getAnnotationPath().is_file()
            C_MaskCoverageFixtures().load_source(window, tmp_path / "second.nii.gz")
            assert window.getMaskCoverageBar().getPresence() == (False,) * 5
        finally:
            window.close()

    # 验证切层和显示设置变化复用掩码存在性缓存。
    def test_coverage_is_cached_during_navigation_and_preview_changes(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_AnnotationProject import (
            C_AnnotationProject,
        )
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_MaskCoverageFixtures import C_MaskCoverageFixtures

        app = C_MaskCoverageFixtures().app()
        window = C_Qt_AnnotationMainWindow(sources=[])
        C_MaskCoverageFixtures().load_source(window, tmp_path / "scan.nii.gz")
        for slice_index in (0, 4):
            window.set_slice(slice_index)
            window.add_polygon(C_PointList([(2, 2), (10, 2), (10, 10), (2, 10)]), "add")

        # 拦截切层和显示设置变化导致的区间缓存重算。
        def unexpected_recomputation(*_args, **_kwargs) -> None:
            pytest.fail("navigation and display settings must not recalculate coverage")

        monkeypatch.setattr(
            C_AnnotationProject, "mask_presence", unexpected_recomputation
        )
        try:
            window.set_slice(2)
            window.getShowInterpolation().setChecked(False)
            window.getLevelSpin().setValue(window.getLevelSpin().value() + 1)
            window.getWidthSpin().setValue(window.getWidthSpin().value() + 1)
            window.refresh_slice()
            app.processEvents()
            assert window.getMaskCoverageBar().getPresence() == (True,) * 5
        finally:
            window.close()

    # 验证载入 JSON 后直接生成区间条，不分配完整三维掩码。
    def test_loaded_annotation_populates_coverage_without_allocating_full_mask(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_AnnotationProject import (
            C_AnnotationProject,
        )
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_MaskCoverageFixtures import C_MaskCoverageFixtures

        app = C_MaskCoverageFixtures().app()
        window = C_Qt_AnnotationMainWindow(sources=[])
        source = C_MaskCoverageFixtures().load_source(window, tmp_path / "scan.nii.gz")
        assert window.getProject() is not None
        polygon = C_PolygonAnnotation(points=((2, 2), (10, 2), (10, 10), (2, 10)))
        for slice_index in (0, 1, 3, 4):
            window.requireProject().add_polygon(slice_index, polygon)
        window.requireProject().set_force_empty(2, True)
        window.requireProject().save(source.getAnnotationPath())

        # 拦截为显示区间条而分配完整三维掩码的调用。
        def unexpected_volume(*_args, **_kwargs) -> None:
            pytest.fail("coverage must not allocate a full 3-D mask")

        monkeypatch.setattr(C_AnnotationProject, "to_mask", unexpected_volume)
        try:
            assert window.getVolume() is not None
            window.setInternalLoadingSource(source)
            window.volume_loaded(window.requireVolume())
            app.processEvents()
            assert window.getMaskCoverageBar().getPresence() == (
                True,
                True,
                False,
                True,
                True,
            )
        finally:
            window.close()

    # 把 pytest 临时目录转换为路径接口，供业务测试复用。
    @pytest.fixture(name="tmp_path")
    def _adapt_path(self, tmp_path: Path) -> I_FilePath:
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        return C_FilePath(tmp_path)
