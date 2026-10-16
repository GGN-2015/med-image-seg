from __future__ import annotations

import json
from typing import final

import numpy as np
from PySide6.QtCore import QPointF, QRectF, QThread, QTimer, SignalInstance
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

from med_image_seg.Abstract.Domain.Annotations import (
    I_MutableAnnotationProject,
)
from med_image_seg.Abstract.Domain.Geometry.I_PointList import I_PointList
from med_image_seg.Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
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

from ...Abstract.Projects.T_NumberedAnnotationsFixtures import (
    T_NumberedAnnotationsFixtures,
)


# 构造多编号项目及写盘样本，供编号切换和删除策略测试使用。
@final
class C_NumberedAnnotationsFixtures(
    T_NumberedAnnotationsFixtures[
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
    ]
):
    # 启动影像读取前保存当前项目，避免切换来源时丢失标注。
    def load_source(
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
    ) -> I_ImageSource:
        from med_image_seg.Concrete.Domain.Imaging.C_MedicalVolume import (
            C_MedicalVolume,
        )
        from med_image_seg.Concrete.Domain.Imaging.C_Metadata import C_Metadata
        from med_image_seg.Concrete.Storage.Volumes.C_ImageSourceFactory import (
            C_ImageSourceFactory,
        )

        path.write_bytes(b"synthetic-image")
        source = C_ImageSourceFactory().from_path(path)
        volume = C_MedicalVolume(
            data=np.arange(np.prod(shape), dtype=np.float32).reshape(shape),
            spacing_mm=(0.8, 0.8, 0.8),
            origin_lps_mm=(1.0, 2.0, 3.0),
            metadata=C_Metadata(json.dumps({})),
            source=source.getPath(),
        )
        window.setInternalLoadingSource(source)
        window.volume_loaded(volume)
        window._finish_loading_ui()
        return source

    # 构造指定位置的轮廓样本，供标注行为测试使用。
    def polygon(self, offset: float = 0) -> I_PointList:
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList

        return C_PointList([(2 + offset, 2), (9 + offset, 2), (5 + offset, 10)])

    # 使用当前影像和网格创建空项目。
    def new_project(
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
    ) -> I_MutableAnnotationProject:
        from med_image_seg.Concrete.Application.Projects.C_ProjectFactory import (
            C_ProjectFactory,
        )

        return C_ProjectFactory().create(
            image_id=window.requireCurrentSource().getSourceId(),
            source_fingerprint=window.requireCurrentSource().getFingerprint(),
            volume=window.requireVolume(),
        )

    # 确认外置掩码操作没有生成或修改标注配套文件。
    def assert_no_sidecars(self, path: I_FilePath) -> None:
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        assert all(
            not C_FilePath(f"{path}{suffix}").exists()
            for suffix in ("", ".bak", ".tmp", ".bak.tmp")
        )
