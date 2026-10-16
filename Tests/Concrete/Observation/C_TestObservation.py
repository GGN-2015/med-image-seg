from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QRectF, QThread, QTimer, SignalInstance
from PySide6.QtGui import QAction, QShortcut
from PySide6.QtWidgets import (
    QAbstractSpinBox,
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
    QSlider,
    QSpinBox,
    QSplitter,
    QToolBar,
    QWidget,
)
from pytest import MonkeyPatch

from med_image_seg.Abstract.Domain.Annotations import (
    I_MutableAnnotationProject,
)
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

from ...Abstract.Observation.T_TestObservation import T_TestObservation

if TYPE_CHECKING:
    from med_image_seg.Abstract.Presentation.Window import (
        T_MutableAnnotationMainWindow,
    )
    from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath
from typing import final

import numpy as np
import pytest
from numpy.typing import NDArray
from PySide6.QtCore import QPointF, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox


# 验证只读三视图、十字线联动、掩码截面和编辑状态恢复。
@final
class C_TestObservation(
    T_TestObservation[
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

    # 按指定间距读取并重采样医学影像，返回体积接口。
    def _load_volume(
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
        shape: tuple[int, int, int] = (20, 16, 9),
    ) -> None:
        from .C_ObservationFixtures import C_ObservationFixtures

        return C_ObservationFixtures().load_volume(window, path, shape)

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
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_ObservationFixtures import C_ObservationFixtures

        app = QApplication.instance() or QApplication([])
        instance = C_Qt_AnnotationMainWindow(sources=[], language="zh")
        C_ObservationFixtures().load_volume(instance, tmp_path / "scan.nii.gz")
        instance.show()
        app.processEvents()
        yield instance
        instance.close()
        app.processEvents()
        instance.deleteLater()
        app.processEvents()

    # 生成带已知前景位置的掩码，供截面和区间比较使用。
    def _seed_masks(
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
    ) -> NDArray[np.uint8]:
        from .C_ObservationFixtures import C_ObservationFixtures

        return C_ObservationFixtures().seed_masks(window)

    # 构造带测试切片的画布，供鼠标交互和显示断言使用。
    def _canvas(
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
        name: str,
    ) -> T_MutableSliceCanvas[
        QGraphicsView,
        QPointF,
        QRectF,
        QGraphicsPixmapItem,
        QGraphicsPathItem,
        QGraphicsPolygonItem,
        T_MutableVertexHandle[QGraphicsEllipseItem],
        SignalInstance,
    ]:
        from .C_ObservationFixtures import C_ObservationFixtures

        return C_ObservationFixtures().canvas(window, name)

    # 提取画布遮罩的前景像素，用于比较显示结果和预期掩码。
    def _overlay_mask(
        self,
        canvas: T_MutableSliceCanvas[
            QGraphicsView,
            QPointF,
            QRectF,
            QGraphicsPixmapItem,
            QGraphicsPathItem,
            QGraphicsPolygonItem,
            T_MutableVertexHandle[QGraphicsEllipseItem],
            SignalInstance,
        ],
    ) -> NDArray[np.bool_]:
        from .C_ObservationFixtures import C_ObservationFixtures

        return C_ObservationFixtures().overlay_mask(canvas)

    # 核验三个截面的轴顺序及提取出的体素数值。
    @pytest.mark.parametrize("name", ["LP", "PS", "SL"])
    def test_plane_sections_have_correct_axes_and_voxel_values(self, name: str) -> None:
        from med_image_seg.Concrete.Algorithms.Observation import (
            C_ObservationPlanes,
        )

        data = np.arange(7 * 11 * 13).reshape(7, 11, 13)
        position = (2, 5, 9)
        plane = C_ObservationPlanes().getPlanes().getByName(name)
        section = plane.section(data, position)
        assert section.shape == (
            data.shape[plane.getVerticalAxis()],
            data.shape[plane.getHorizontalAxis()],
        )
        for vertical in range(section.shape[0]):
            for horizontal in range(section.shape[1]):
                voxel: list[int] = list(position)
                voxel[plane.getHorizontalAxis()] = horizontal
                voxel[plane.getVerticalAxis()] = vertical
                assert section[vertical, horizontal] == data[tuple(voxel)]

    # 核验截面点击采用像素位置并限制在有效体素范围内。
    @pytest.mark.parametrize("name", ["LP", "PS", "SL"])
    def test_plane_clicks_use_pixel_centers_and_clamp_to_volume(
        self, name: str
    ) -> None:
        from med_image_seg.Concrete.Algorithms.Observation import (
            C_ObservationPlanes,
        )

        plane = C_ObservationPlanes().getPlanes().getByName(name)
        position = (2, 5, 9)
        shape = (7, 11, 13)
        result = plane.position_at(position, 1.5, 3.5, shape)
        assert result[plane.getHorizontalAxis()] == 1
        assert result[plane.getVerticalAxis()] == 3
        assert result[plane.getFixedAxis()] == position[plane.getFixedAxis()]
        result = plane.position_at(position, -20, 100, shape)
        assert result[plane.getHorizontalAxis()] == 0
        assert result[plane.getVerticalAxis()] == shape[plane.getVerticalAxis()] - 1

    # 验证进入观察模式前先闭合并保存已有草稿。
    @pytest.mark.parametrize("operation", ["add", "erase"])
    def test_entering_observation_closes_and_saves_draft_before_read_only(
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
        operation: str,
    ) -> None:
        from med_image_seg.Concrete.Domain.Geometry.C_Point2D import C_Point2D
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Storage.Projects.C_ProjectRepository import (
            C_ProjectRepository,
        )

        if operation == "erase":
            window.getEraseRadio().setChecked(True)
        window.getCanvas().setDraftPoints(
            C_PointList([C_Point2D(2, 2), C_Point2D(8, 2), C_Point2D(5, 8)])
        )
        window.getObserveRadio().setChecked(True)
        annotation = window.requireProject().annotation(window.getCurrentSlice())
        assert annotation.getPolygonCount() == 1
        assert annotation.getPolygon(0).getOperation() == operation
        restored = C_ProjectRepository().load(window.requireProjectPath())
        assert list(
            restored.annotation(window.getCurrentSlice()).iterPolygons()
        ) == list(annotation.iterPolygons())
        assert not window.getCanvas().getDraftPointCount()
        assert window.getReadOnly()
        assert window.getCanvas().getReadOnly()
        assert window.getCanvas().getHandleCount()
        assert all(not control.isEnabled() for control in window.iterEditingControls())
        assert all(
            not shortcut.isEnabled() for shortcut in window.iterEditingShortcuts()
        )
        assert window.getSliceSlider().isEnabled()
        assert window.getLevelSpin().isEnabled()
        assert window.getExportAction().isEnabled()
        assert window.getExportUbdAction().isEnabled()
        assert window.getExportJsonAction().isEnabled()

    # 进入只读模式时丢弃不足三个点的草稿，不生成无效轮廓。
    @pytest.mark.parametrize("count", [0, 1, 2])
    def test_too_short_draft_is_discarded_without_creating_invalid_polygon(
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
        count: int,
    ) -> None:
        from med_image_seg.Concrete.Domain.Geometry.C_Point2D import C_Point2D
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList

        window.getCanvas().setDraftPoints(
            C_PointList([C_Point2D(index, index) for index in range(count)])
        )
        window.getObserveRadio().setChecked(True)
        assert window.getReadOnly()
        assert (
            not window.requireProject()
            .annotation(window.getCurrentSlice())
            .getPolygonCount()
        )
        assert not window.getCanvas().getDraftPointCount()

    # 点击任一截面，验证共享交点和其余层号控件同步更新。
    @pytest.mark.parametrize(
        ("name", "clicked", "expected"),
        [
            ("LP", (4.5, 6.5), (4, 6, 4)),
            ("PS", (6.5, 2.5), (10, 6, 2)),
            ("SL", (2.5, 4.5), (4, 8, 2)),
        ],
    )
    def test_click_in_any_view_updates_shared_intersection_and_slice_controls(
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
        name: str,
        clicked: tuple[float, float],
        expected: tuple[int, int, int],
    ) -> None:
        from med_image_seg.Concrete.Algorithms.Observation import (
            C_ObservationPlanes,
        )

        from .C_ObservationFixtures import C_ObservationFixtures

        window.getObserveRadio().setChecked(True)
        QApplication.processEvents()
        canvas = C_ObservationFixtures().canvas(window, name)
        viewport_point = canvas.getHost().mapFromScene(QPointF(*clicked))
        QTest.mouseClick(
            canvas.getHost().viewport(), Qt.MouseButton.LeftButton, pos=viewport_point
        )
        assert window.getObservationPosition() == expected
        assert window.getCurrentSlice() == expected[2]
        assert window.getSliceSlider().value() == expected[2]
        assert window.getSliceSpin().value() == expected[2]
        assert window.getObservationWindow("PS").getSliceSpin().value() == expected[0]
        assert window.getObservationWindow("SL").getSliceSpin().value() == expected[1]
        for plane_name, plane in C_ObservationPlanes().getPlanes().getItems():
            displayed = C_ObservationFixtures().canvas(window, plane_name)
            assert displayed.getInternalCrosshairPosition() == QPointF(
                expected[plane.getHorizontalAxis()] + 0.5,
                expected[plane.getVerticalAxis()] + 0.5,
            )
            assert not displayed.getDraftPointCount()

    # 连续切层，核验三视图交点、层号及参考线始终同步。
    def test_sequential_navigation_keeps_all_three_views_synchronized(
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
        window.getObserveRadio().setChecked(True)
        window._observation_clicked("LP", QPointF(4.5, 6.5))
        window._observation_clicked("PS", QPointF(9.5, 2.5))
        assert window.getObservationPosition() == (4, 9, 2)
        window._observation_clicked("SL", QPointF(7.5, 11.5))
        assert window.getObservationPosition() == (11, 9, 7)
        window.getSliceSlider().setValue(5)
        assert window.getObservationPosition() == (11, 9, 5)
        window.getObservationWindow("PS").getSliceSpin().setValue(3)
        window.getObservationWindow("SL").getSliceSpin().setValue(2)
        assert window.getObservationPosition() == (3, 2, 5)

    # 验证十字星与其他视图中的同色参考线代表同一截面。
    @pytest.mark.parametrize("name", ["LP", "PS", "SL"])
    def test_crosshair_and_reference_line_colors_identify_the_same_planes(
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
        name: str,
    ) -> None:
        from med_image_seg.Concrete.Algorithms.Observation import (
            C_ObservationPlanes,
        )

        from .C_ObservationFixtures import C_ObservationFixtures

        window.getObserveRadio().setChecked(True)
        plane = C_ObservationPlanes().getPlanes().getByName(name)
        canvas = C_ObservationFixtures().canvas(window, name)
        assert canvas.getInternalCrosshairColors() == (
            C_ObservationPlanes().getAxisColors().getByAxis(plane.getHorizontalAxis()),
            C_ObservationPlanes().getAxisColors().getByAxis(plane.getVerticalAxis()),
            plane.getColor(),
        )
        assert len(set(canvas.getInternalCrosshairColors())) == 3
        assert not canvas.getHost().grab().isNull()

    # 比较附属截面与完整导出掩码，覆盖擦除及空层结果。
    @pytest.mark.parametrize("index", [1, 2, 4, 6, 7])
    def test_companion_masks_match_export_with_erasures_and_empty_slices(
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
        index: int,
    ) -> None:
        from med_image_seg.Concrete.Algorithms.Observation import (
            C_ObservationPlanes,
        )

        from .C_ObservationFixtures import C_ObservationFixtures

        expected = C_ObservationFixtures().seed_masks(window)
        window.getObserveRadio().setChecked(True)
        window._observation_clicked("LP", QPointF(5.5, 5.5))
        window.set_slice(index)
        np.testing.assert_array_equal(window.requireInternalObservationMask(), expected)
        for name in ("PS", "SL"):
            plane = C_ObservationPlanes().getPlanes().getByName(name)
            canvas = C_ObservationFixtures().canvas(window, name)
            np.testing.assert_array_equal(
                C_ObservationFixtures().overlay_mask(canvas),
                plane.section(expected, window.getObservationPosition()),
            )
            assert not canvas.getHandleCount()
            assert not canvas.getPolygonItemCount()
        if index in (1, 7):
            assert window.getCanvas().getHandleCount()
            assert window.getCanvas().getInternalInterpolationItem() is None
        elif index == 4:
            assert not window.getCanvas().getHandleCount()
            assert window.getCanvas().getInternalInterpolationItem() is None
        else:
            np.testing.assert_array_equal(
                C_ObservationFixtures().overlay_mask(window.getCanvas()),
                expected[:, :, index].T,
            )

    # 监测掩码生成次数，验证观察切层和调窗复用缓存。
    def test_observation_reuses_mask_for_navigation_and_contrast(
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

        from .C_ObservationFixtures import C_ObservationFixtures

        C_ObservationFixtures().seed_masks(window)
        calls = []
        original = C_AnnotationProject.to_mask

        # 记录完整掩码构建次数并调用原实现，用于核对观察缓存是否复用。
        def tracked(project: I_MutableAnnotationProject, *, interpolate: bool = True):
            assert isinstance(project, C_AnnotationProject)
            calls.append(interpolate)
            assert not window.getHost().isEnabled()
            assert not window.getAutosaveTimer().isActive()
            return original(project, interpolate=interpolate)

        monkeypatch.setattr(C_AnnotationProject, "to_mask", tracked)
        window.getObserveRadio().setChecked(True)
        assert calls == [True]

        # 拦截导航时重复执行的插值计算，调用即判定缓存测试失败。
        def unexpected(*args, **kwargs):
            pytest.fail("Navigation must not recompute interpolation")

        monkeypatch.setattr(C_AnnotationProject, "interpolated_plane", unexpected)
        window._observation_clicked("PS", QPointF(5.5, 6.5))
        window.set_slice(3)
        window.getLevelSpin().setValue(window.getLevelSpin().value() + 1)
        window.getWidthSpin().setValue(window.getWidthSpin().value() + 10)
        window.set_language("en")
        assert calls == [True]
        assert "Read-only" in window.getObservationWindow("PS").getHost().windowTitle()

    # 验证只读模式同时阻止按钮、快捷键、直接编辑调用和顶点拖动。
    def test_read_only_blocks_edit_buttons_shortcuts_direct_methods_and_handle_drags(
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
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList

        from .C_ObservationFixtures import C_ObservationFixtures

        C_ObservationFixtures().seed_masks(window)
        window.set_slice(1)
        window.getObserveRadio().setChecked(True)
        original = window.requireProjectPath().read_bytes()
        original_counter = window.requireProject().getEditCounter()
        original_polygons = list(window.requireProject().annotation(1).iterPolygons())
        handle_position = (
            window.getCanvas()
            .getHost()
            .mapFromScene(window.getCanvas().getHandle(0).getHost().pos())
        )
        QTest.mousePress(
            window.getCanvas().getHost().viewport(),
            Qt.MouseButton.LeftButton,
            pos=handle_position,
        )
        QTest.mouseMove(
            window.getCanvas().getHost().viewport(),
            handle_position
            + window.getCanvas().getHost().mapFromScene(QPointF(1, 1))
            - window.getCanvas().getHost().mapFromScene(QPointF(0, 0)),
        )
        QTest.mouseRelease(
            window.getCanvas().getHost().viewport(), Qt.MouseButton.LeftButton
        )
        for key, modifier in (
            (Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier),
            (Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier),
            (Qt.Key.Key_C, Qt.KeyboardModifier.NoModifier),
            (Qt.Key.Key_M, Qt.KeyboardModifier.NoModifier),
        ):
            QTest.keyClick(window.getHost(), key, modifier)
        window.add_polygon(C_PointList([(1, 1), (5, 1), (3, 5)]), "add")
        window.update_polygon(0, C_PointList([(1, 1), (5, 1), (3, 5)]))
        window.delete_last_edited_polygon()
        window.clear_current_slice()
        window.copy_previous_slice()
        window.set_slice_completed(True)
        window.set_force_empty(True)
        window.toggle_completed()
        window.getCanvas().finish_polygon()
        assert window.requireProject().getEditCounter() == original_counter
        assert (
            list(window.requireProject().annotation(1).iterPolygons())
            == original_polygons
        )
        assert not window.requireProject().annotation(1).getCompleted()
        assert not window.requireProject().annotation(1).getForceEmpty()
        assert window.requireProjectPath().read_bytes() == original
        assert not window.getCanvas().getDraftPointCount()
        assert window.getCanvas().getInternalDraggingHandle() is None

    # 验证附属视图非模态、不可独立关闭，并跟随模式和主窗口显示。
    def test_companion_windows_are_nonmodal_unclosable_and_follow_mode_and_parent(
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
        window.getObserveRadio().setChecked(True)
        QApplication.processEvents()
        views = tuple(window.iterObservationWindows())
        for view in views:
            assert view.getHost().isVisible()
            assert view.getHost().parentWidget() is window
            assert view.getHost().windowModality() == Qt.WindowModality.NonModal
            assert (
                not view.getHost().windowFlags() & Qt.WindowType.WindowCloseButtonHint
            )
            assert not view.getHost().close()
            assert view.getHost().isVisible()
        window.getHost().hide()
        assert all(not view.getHost().isVisible() for view in views)
        window.getHost().show()
        assert all(view.getHost().isVisible() for view in views)
        window.getEraseRadio().setChecked(True)
        assert not window.getReadOnly()
        assert not window.getCanvas().getReadOnly()
        assert window.getCanvas().getInternalOperation() == "erase"
        assert window.getCanvas().getInternalCrosshairPosition() is None
        assert all(not view.getHost().isVisible() for view in views)
        assert all(control.isEnabled() for control in window.iterEditingControls())
        assert all(shortcut.isEnabled() for shortcut in window.iterEditingShortcuts())
        window.getObserveRadio().setChecked(True)
        assert tuple(window.iterObservationWindows()) == views
        window.getHost().close()
        assert all(not view.getHost().isVisible() for view in views)

    # 验证观察模式临时显示插值，退出后恢复原显示偏好。
    def test_observation_restores_interpolation_preference(
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
        window.getShowInterpolation().setChecked(False)
        window.getObserveRadio().setChecked(True)
        assert window.getShowInterpolation().isChecked()
        assert not window.getShowInterpolation().isEnabled()
        window.getAddRadio().setChecked(True)
        assert not window.getShowInterpolation().isChecked()
        assert window.getShowInterpolation().isEnabled()

    # 退出观察并修改轮廓后，验证再次进入时重建掩码而不使用旧缓存。
    def test_reentering_observation_rebuilds_mask_after_editing(
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
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList

        window.getObserveRadio().setChecked(True)
        assert not window.requireInternalObservationMask().any()
        window.getAddRadio().setChecked(True)
        window.add_polygon(C_PointList([(2, 2), (9, 2), (5, 9)]), "add")
        window.getObserveRadio().setChecked(True)
        assert window.requireInternalObservationMask().any()

    # 观察模式载入不同尺寸影像，核验交点和截面索引仍有效。
    def test_observation_handles_loading_new_volume_with_different_dimensions(
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
        tmp_path: I_FilePath,
    ) -> None:
        from .C_ObservationFixtures import C_ObservationFixtures

        C_ObservationFixtures().seed_masks(window)
        window.getObserveRadio().setChecked(True)
        old_views = tuple(window.iterObservationWindows())
        C_ObservationFixtures().load_volume(
            window, tmp_path / "second.nii.gz", (5, 7, 3)
        )
        assert window.getObservationPosition() == (2, 3, 1)
        assert window.requireInternalObservationMask().shape == (5, 7, 3)
        assert not window.requireInternalObservationMask().any()
        assert window.getCurrentSlice() == 1
        assert window.getObservationWindow("PS").getSliceSpin().maximum() == 4
        assert window.getObservationWindow("SL").getSliceSpin().maximum() == 6
        assert tuple(window.iterObservationWindows()) == old_views
        assert all(not control.isEnabled() for control in window.iterEditingControls())

    # 验证加载期间附属视图被禁用，完成后恢复正确的只读状态。
    def test_loading_disables_companion_views_and_restores_read_only_state(
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
        window.getObserveRadio().setChecked(True)
        window._show_loading(window.requireCurrentSource())
        assert all(
            not view.getHost().isEnabled() for view in window.iterObservationWindows()
        )
        window._finish_loading_ui()
        assert all(
            view.getHost().isEnabled() for view in window.iterObservationWindows()
        )
        assert all(not control.isEnabled() for control in window.iterEditingControls())

    # 模拟重载期间掩码准备失败，核验原影像未被替换。
    def test_failed_mask_preparation_during_reload_preserves_previous_volume(
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
        tmp_path: I_FilePath,
        monkeypatch: MonkeyPatch,
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_AnnotationProject import (
            C_AnnotationProject,
        )

        from .C_ObservationFixtures import C_ObservationFixtures

        C_ObservationFixtures().seed_masks(window)
        window.getObserveRadio().setChecked(True)
        old_volume = window.requireVolume()
        old_project = window.requireProject()
        old_mask = window.requireInternalObservationMask()
        old_position = window.getObservationPosition()

        # 模拟替换影像所需的掩码分配失败。
        def fail(*args, **kwargs):
            raise MemoryError("cannot allocate replacement mask")

        monkeypatch.setattr(C_AnnotationProject, "to_mask", fail)
        C_ObservationFixtures().load_volume(
            window, tmp_path / "failed-replacement.nii.gz", (5, 7, 3)
        )
        assert "cannot allocate replacement mask" in window.requireInternalLoadError()
        assert window.getVolume() is old_volume
        assert window.getProject() is old_project
        assert window.getInternalObservationMask() is old_mask
        assert window.getObservationPosition() == old_position
        assert window.getReadOnly()
        window._observation_clicked("PS", QPointF(3.5, 6.5))
        assert window.getObservationPosition() == (old_position[0], 3, 6)

    # 模拟观察掩码生成失败，核验界面不会残留禁用状态。
    def test_failed_mask_preparation_restores_editing_and_does_not_leave_disabled_ui(
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

        errors = []

        # 模拟观察模式掩码分配失败，覆盖界面恢复路径。
        def fail(*args, **kwargs):
            raise MemoryError("synthetic mask allocation failure")

        monkeypatch.setattr(C_AnnotationProject, "to_mask", fail)
        monkeypatch.setattr(
            QMessageBox, "critical", lambda *args: errors.append(args[2])
        )
        window.getEraseRadio().setChecked(True)
        window.getObserveRadio().setChecked(True)
        assert errors == ["synthetic mask allocation failure"]
        assert not window.getReadOnly()
        assert window.getEraseRadio().isChecked()
        assert window.getCanvas().getInternalOperation() == "erase"
        assert window.getHost().isEnabled()
        assert window.getAutosaveTimer().isActive()
        assert not window.getInternalClosingPolygon()
        assert not window.getObservationWindowCount()

    # 使用单体素影像，验证交点限制和截面提取无越界。
    def test_single_voxel_volume_has_valid_intersection_and_sections(
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
        tmp_path: I_FilePath,
    ) -> None:
        from med_image_seg.Concrete.Algorithms.Observation import (
            C_ObservationPlanes,
        )

        from .C_ObservationFixtures import C_ObservationFixtures

        C_ObservationFixtures().load_volume(
            window, tmp_path / "single.nii.gz", (1, 1, 1)
        )
        window.getObserveRadio().setChecked(True)
        assert window.getObservationPosition() == (0, 0, 0)
        for name in C_ObservationPlanes().getPlanes():
            canvas = C_ObservationFixtures().canvas(window, name)
            assert canvas.getInternalImageRect().width() == 1
            assert canvas.getInternalImageRect().height() == 1
            assert canvas.getInternalCrosshairPosition() == QPointF(0.5, 0.5)

    # 把 pytest 临时目录转换为路径接口，供业务测试复用。
    @pytest.fixture(name="tmp_path")
    def _adapt_path(self, tmp_path: Path) -> I_FilePath:
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        return C_FilePath(tmp_path)
