from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import final

import numpy as np
import pytest
from PySide6.QtCore import QPointF, QRectF, Qt, QThread, QTimer, SignalInstance
from PySide6.QtGui import QAction, QShortcut
from PySide6.QtTest import QTest
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
    QMessageBox,
    QProgressBar,
    QProgressDialog,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QSplitter,
    QToolBar,
    QWidget,
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
from med_image_seg.Abstract.Presentation.Window import (
    T_MutableAnnotationMainWindow,
)
from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

from ...Abstract.Navigation.T_TestLabeledNavigation import T_TestLabeledNavigation


# 验证前后有标注层跳转、边界提示及只读模式下的联动。
@final
class C_TestLabeledNavigation(
    T_TestLabeledNavigation[
        T_MutableAnnotationMainWindow[
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
        MonkeyPatch,
    ]
):
    # 为当前测试类配置离屏 Qt 环境。
    @pytest.fixture(autouse=True, name="configure_environment")
    def _configure_environment_fixture(self) -> None:
        from ..Environment.C_TestEnvironment import C_TestEnvironment

        C_TestEnvironment().configure()

    # 创建测试窗口，退出测试时关闭窗口并释放相关资源。
    @pytest.fixture(name="window")
    def _window_fixture(
        self, tmp_path: I_FilePath
    ) -> Iterator[
        T_MutableAnnotationMainWindow[
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
        ]
    ]:
        from med_image_seg.Concrete.Domain.Imaging.C_MedicalVolume import (
            C_MedicalVolume,
        )
        from med_image_seg.Concrete.Domain.Imaging.C_Metadata import C_Metadata
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )
        from med_image_seg.Concrete.Storage.Volumes.C_ImageSourceFactory import (
            C_ImageSourceFactory,
        )

        app = QApplication.instance() or QApplication([])
        image = tmp_path / "scan.nii"
        image.write_bytes(b"synthetic-image")
        source = C_ImageSourceFactory().from_path(image)
        instance = C_Qt_AnnotationMainWindow(sources=[], language="en")
        instance.setInternalLoadingSource(source)
        instance.volume_loaded(
            C_MedicalVolume(
                data=np.arange(20 * 16 * 12, dtype=np.float32).reshape(20, 16, 12),
                spacing_mm=(0.8, 0.8, 0.8),
                origin_lps_mm=(0.0, 0.0, 0.0),
                metadata=C_Metadata(json.dumps({})),
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

    # 生成可复现的标注样本，供多个测试场景使用。
    def _seed(
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
        indices: Iterable[int],
    ) -> None:
        from .C_LabeledNavigationFixtures import C_LabeledNavigationFixtures

        return C_LabeledNavigationFixtures().seed(window, indices)

    # 创建按钮并连接点击回调，统一布局服务的控件装配。
    def _button(
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
        direction: int,
    ) -> QPushButton:
        from .C_LabeledNavigationFixtures import C_LabeledNavigationFixtures

        return C_LabeledNavigationFixtures().button(window, direction)

    # 验证前后标注层按钮位于切层按钮下方，且不破坏区间条对齐。
    def test_labeled_buttons_sit_below_existing_buttons_without_misaligning_coverage(
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
    ) -> None:
        from med_image_seg.Concrete.Localization.C_Localizer import C_Localizer

        for top, bottom in (
            (window.getPreviousButton(), window.getPreviousLabeledButton()),
            (window.getNextButton(), window.getNextLabeledButton()),
        ):
            assert bottom.y() > top.y()
            assert bottom.x() == top.x()
            assert bottom.width() == top.width()
        assert window.getMaskCoverageBar().getHost().x() == window.getSliceSlider().x()
        assert (
            window.getMaskCoverageBar().getHost().width()
            == window.getSliceSlider().width()
        )
        assert window.getPreviousLabeledButton().text() == "Prev labeled slice"
        assert window.getNextLabeledButton().text() == "Next labeled slice"
        window.set_language("zh")
        QApplication.processEvents()
        assert window.getPreviousLabeledButton().text() == "上一标注层"
        assert window.getNextLabeledButton().text() == "下一标注层"
        assert window.getPreviousLabeledButton().toolTip() == C_Localizer().translate(
            "labeled_slice_tooltip", "zh"
        )
        assert window.getMaskCoverageBar().getHost().x() == window.getSliceSlider().x()
        assert (
            window.getMaskCoverageBar().getHost().width()
            == window.getSliceSlider().width()
        )

    # 验证导航找到最近的前后轮廓层，且不把当前层算作目标。
    @pytest.mark.parametrize(
        "current,direction,expected",
        [(6, -1, 4), (6, 1, 7), (4, -1, 1), (4, 1, 7), (0, 1, 1), (11, -1, 9)],
    )
    def test_buttons_jump_to_nearest_strictly_earlier_or_later_polygon_slice(
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
        current: int,
        direction: int,
        expected: int,
    ) -> None:
        from .C_LabeledNavigationFixtures import C_LabeledNavigationFixtures

        C_LabeledNavigationFixtures().seed(window, (9, 1, 7, 4))
        window.set_slice(current)
        original = window.requireProjectPath().read_bytes()
        QTest.mouseClick(
            C_LabeledNavigationFixtures().button(window, direction),
            Qt.MouseButton.LeftButton,
        )
        assert window.getCurrentSlice() == expected
        assert window.getSliceSpin().value() == expected
        assert window.getSliceSlider().value() == expected
        assert window.getCanvas().getHandleCount()
        assert window.requireProjectPath().read_bytes() == original

    # 验证有标注层导航跳过仅插值层、空关键层及空复核层。
    @pytest.mark.parametrize("direction, expected", [(-1, 1), (1, 10)])
    def test_interpolation_and_empty_keyframe_or_review_slices_are_skipped(
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
        direction: int,
        expected: int,
    ) -> None:
        from .C_LabeledNavigationFixtures import C_LabeledNavigationFixtures

        C_LabeledNavigationFixtures().seed(window, (1, 10))
        window.requireProject().set_completed(3, True)
        window.requireProject().set_keyframe(5, True)
        window.requireProject().set_force_empty(8, True)
        window.commit_change()
        window.set_slice(6)
        assert window.requireProject().interpolation_bounds(6) is not None
        window.go_to_labeled_slice(direction)
        assert window.getCurrentSlice() == expected

    # 验证强制空层上的已存轮廓仍计入有标注层导航。
    @pytest.mark.parametrize("source", ["manual", "prototype"])
    @pytest.mark.parametrize("operation", ["add", "erase"])
    def test_any_stored_polygon_counts_even_on_forced_empty_slice(
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
        source: str,
        operation: str,
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )

        window.requireProject().add_polygon(
            9,
            C_PolygonAnnotation(
                points=((2, 2), (9, 2), (5, 10)), source=source, operation=operation
            ),
        )
        window.requireProject().set_force_empty(9, True)
        window.commit_change()
        window.set_slice(6)
        assert not window.requireProject().to_mask().any()
        window.go_to_labeled_slice(1)
        assert window.getCurrentSlice() == 9

    # 验证找不到前后目标时提示方向正确，且不回绕或移动当前层。
    @pytest.mark.parametrize(
        "direction,labels",
        [(-1, ()), (1, ()), (-1, (6,)), (1, (6,)), (-1, (6, 11)), (1, (0, 6))],
    )
    def test_missing_target_shows_directional_message_without_wrapping_or_moving(
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
        monkeypatch: MonkeyPatch,
        direction: int,
        labels: Iterable[int],
    ) -> None:
        from med_image_seg.Concrete.Domain.Geometry.C_Point2D import C_Point2D
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList

        from .C_LabeledNavigationFixtures import C_LabeledNavigationFixtures

        C_LabeledNavigationFixtures().seed(window, labels)
        window.set_language("zh")
        window.set_slice(6)
        window.getCanvas().setDraftPoints(
            C_PointList([C_Point2D(3, 3), C_Point2D(7, 3)])
        )
        messages = []
        monkeypatch.setattr(
            QMessageBox, "information", lambda *args: messages.append(args)
        )
        QTest.mouseClick(
            C_LabeledNavigationFixtures().button(window, direction),
            Qt.MouseButton.LeftButton,
        )
        assert len(messages) == 1
        assert messages[0][0] is window
        assert messages[0][2] == (
            "未找到上一个有标注的面。" if direction < 0 else "未找到下一个有标注的面。"
        )
        assert (
            window.getCurrentSlice()
            == window.getSliceSlider().value()
            == window.getSliceSpin().value()
            == 6
        )
        assert window.getCanvas().getDraftPointCount() == 2

    # 验证找不到目标标注层时显示真正的模态提示框。
    @pytest.mark.parametrize("direction", [-1, 1])
    def test_missing_target_dialog_is_actually_modal(
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
        direction: int,
    ) -> None:
        from med_image_seg.Concrete.Localization.C_Localizer import C_Localizer

        from .C_LabeledNavigationFixtures import C_LabeledNavigationFixtures

        window.set_language("zh")
        captured = []

        # 捕获并关闭活动模态提示，避免导航边界测试阻塞。
        def dismiss():
            dialog = QApplication.activeModalWidget()
            if isinstance(dialog, QMessageBox):
                captured.append(
                    (dialog.isModal(), dialog.text(), dialog.parentWidget())
                )
                dialog.accept()

        QTimer.singleShot(0, dismiss)
        QTest.mouseClick(
            C_LabeledNavigationFixtures().button(window, direction),
            Qt.MouseButton.LeftButton,
        )
        key = (
            "previous_labeled_not_found" if direction < 0 else "next_labeled_not_found"
        )
        assert captured == [(True, C_Localizer().translate(key, "zh"), window)]

    # 验证有标注层导航只查询当前编号项目。
    def test_number_switch_limits_navigation_to_active_annotation(
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
    ) -> None:
        from .C_LabeledNavigationFixtures import C_LabeledNavigationFixtures

        C_LabeledNavigationFixtures().seed(window, (1, 9))
        window.set_annotation_index(2)
        C_LabeledNavigationFixtures().seed(window, (3, 10))
        window.set_slice(6)
        window.go_to_labeled_slice(-1)
        assert window.getCurrentSlice() == 3
        window.set_annotation_index(0)
        window.set_slice(6)
        window.go_to_labeled_slice(-1)
        assert window.getCurrentSlice() == 1
        window.go_to_labeled_slice(1)
        assert window.getCurrentSlice() == 9

    # 验证观察模式也可导航标注层，并同步三视图参考线。
    def test_labeled_navigation_works_in_observation_and_updates_cross_references(
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
        monkeypatch: MonkeyPatch,
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_AnnotationProject import (
            C_AnnotationProject,
        )

        from .C_LabeledNavigationFixtures import C_LabeledNavigationFixtures

        C_LabeledNavigationFixtures().seed(window, (1, 9))
        window.set_slice(5)
        window.getObserveRadio().setChecked(True)
        window._observation_clicked("LP", QPointF(5.5, 7.5))
        mask = window.requireInternalObservationMask()

        # 拦截观察导航重复生成掩码的调用。
        def no_recomputation(*args, **kwargs):
            pytest.fail("Labeled navigation must reuse the observation mask")

        monkeypatch.setattr(C_AnnotationProject, "to_mask", no_recomputation)
        assert window.getPreviousLabeledButton().isEnabled()
        assert window.getNextLabeledButton().isEnabled()
        QTest.mouseClick(window.getNextLabeledButton(), Qt.MouseButton.LeftButton)
        assert window.getObservationPosition() == (5, 7, 9)
        assert window.getObservationWindow(
            "PS"
        ).getCanvas().getInternalCrosshairPosition() == QPointF(7.5, 9.5)
        assert window.getObservationWindow(
            "SL"
        ).getCanvas().getInternalCrosshairPosition() == QPointF(9.5, 5.5)
        assert window.getInternalObservationMask() is mask
        assert window.getCanvas().getReadOnly()
        assert window.getCanvas().getHandleCount()
        assert all(not control.isEnabled() for control in window.iterEditingControls())

    # 验证未载入影像或软件忙碌时不可跳转有标注层。
    def test_labeled_navigation_is_unavailable_without_image_or_while_busy(
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
        monkeypatch: MonkeyPatch,
    ) -> None:
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_LabeledNavigationFixtures import C_LabeledNavigationFixtures

        app = QApplication.instance()
        assert app is not None
        empty = C_Qt_AnnotationMainWindow(sources=[])
        assert not empty.getPreviousLabeledButton().isEnabled()
        assert not empty.getNextLabeledButton().isEnabled()

        # 验证导航不可用时不会意外打开提示框。
        def no_dialog(*args):
            pytest.fail("Navigation is unavailable and must not open a dialog")

        monkeypatch.setattr(QMessageBox, "information", no_dialog)
        empty.go_to_labeled_slice(-1)
        empty.go_to_labeled_slice(1)
        empty.close()
        app.processEvents()
        C_LabeledNavigationFixtures().seed(window, (1, 9))
        current = window.getCurrentSlice()
        with window._polygon_busy_ui():
            assert not window.getPreviousLabeledButton().isEnabled()
            assert not window.getNextLabeledButton().isEnabled()
            window.go_to_labeled_slice(1)
        assert window.getCurrentSlice() == current

    # 把 pytest 临时目录转换为路径接口，供业务测试复用。
    @pytest.fixture(name="tmp_path")
    def _adapt_path(self, tmp_path: Path) -> I_FilePath:
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        return C_FilePath(tmp_path)
