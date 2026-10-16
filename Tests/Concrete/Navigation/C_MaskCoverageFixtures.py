from __future__ import annotations

from typing import TYPE_CHECKING

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

from ...Abstract.Navigation.T_MaskCoverageFixtures import T_MaskCoverageFixtures

if TYPE_CHECKING:
    from med_image_seg.Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
    from med_image_seg.Abstract.Presentation.Window import (
        T_MutableAnnotationMainWindow,
    )
    from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath
import json
from typing import final

import numpy as np
from PySide6.QtWidgets import QApplication


# 构造区间条测试窗口，并生成带关键层的标注样本。
@final
class C_MaskCoverageFixtures(
    T_MaskCoverageFixtures[
        QApplication,
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
    ]
):
    # 复用或创建 QApplication，供测试驱动界面事件。
    def app(self) -> QApplication:
        application = QApplication.instance()
        if not isinstance(application, QApplication):
            application = QApplication([])
        return application

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
            data=np.arange(20 * 18 * 5, dtype=np.float32).reshape(20, 18, 5),
            spacing_mm=(0.8, 0.8, 0.8),
            origin_lps_mm=(0.0, 0.0, 0.0),
            metadata=C_Metadata(json.dumps({})),
            source=source.getPath(),
        )
        window.setInternalLoadingSource(source)
        window.volume_loaded(volume)
        window._finish_loading_ui()
        return source
