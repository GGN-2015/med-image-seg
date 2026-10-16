from __future__ import annotations

import time
from typing import final

import numpy as np
from numpy.typing import NDArray
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
    QSlider,
    QSpinBox,
    QSplitter,
    QToolBar,
    QWidget,
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
from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

from ...Abstract.ExternalPreview.T_ExternalMaskGuiFixtures import (
    T_ExternalMaskGuiFixtures,
)


# 构造外置掩码预览窗口，并检查遮罩和界面状态。
@final
class C_ExternalMaskGuiFixtures(
    T_ExternalMaskGuiFixtures[
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
    ]
):
    # 驱动 Qt 事件循环直到后台读取完成，并在超时或失败时终止测试。
    def wait_loaded(
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
        deadline = time.monotonic() + 10
        while (
            window.getExternalMaskThread() is not None and time.monotonic() < deadline
        ):
            QApplication.processEvents()
            time.sleep(0.005)
        assert window.getExternalMaskThread() is None
        QApplication.processEvents()

    # 生成可复现的标注样本，供多个测试场景使用。
    def seed(
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

        window.set_slice(2)
        window.add_polygon(C_PointList([(2, 2), (9, 2), (5, 10)]), "add")
        window.set_slice(6)
        window.add_polygon(C_PointList([(3, 2), (10, 2), (6, 10)]), "add")
        window.set_slice(4)

    # 在测试目录写入掩码，供外置预览加载流程使用。
    def write_mask(
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
        suffix: str = ".nii.gz",
        empty: bool = False,
    ) -> tuple[I_FilePath, NDArray[np.uint8]]:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskWriter import (
            C_MedicalMaskWriter,
        )

        mask = np.zeros(window.requireVolume().getData().shape, dtype=np.uint8)
        if not empty:
            mask[3:12, 5:10, 1] = 1
            mask[5:15, 7:13, 7:9] = 1
        path = C_MedicalMaskWriter().write(
            tmp_path / f"external{suffix}", mask, window.requireVolume()
        )
        return (path, mask)

    # 查询画布的掩码图层，供测试检查颜色和像素。
    def overlay(
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
    ) -> NDArray[np.uint8]:
        image = canvas.requireInternalInterpolationItem().pixmap().toImage()
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
