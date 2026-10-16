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

from ...Abstract.Observation.T_ObservationFixtures import T_ObservationFixtures

if TYPE_CHECKING:
    from med_image_seg.Abstract.Presentation.Window import (
        T_MutableAnnotationMainWindow,
    )
    from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath
import json
from typing import final

import numpy as np
from numpy.typing import NDArray


# 构造三视图测试窗口和掩码，供定位、配色及只读验证使用。
@final
class C_ObservationFixtures(
    T_ObservationFixtures[
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
    # 按指定间距读取并重采样医学影像，返回体积接口。
    def load_volume(
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
            origin_lps_mm=(10.0, 20.0, 30.0),
            metadata=C_Metadata(json.dumps({})),
            source=source.getPath(),
        )
        window.setInternalLoadingSource(source)
        window.volume_loaded(volume)
        window._finish_loading_ui()

    # 生成带已知前景位置的掩码，供截面和区间比较使用。
    def seed_masks(
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
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )
        from med_image_seg.Concrete.Numerics.Arrays.C_ArrayFactory import C_ArrayFactory

        polygon = C_PolygonAnnotation(points=((3, 3), (15, 3), (15, 12), (3, 12)))
        erase = C_PolygonAnnotation(
            points=((8, 6), (10, 6), (10, 8), (8, 8)), operation="erase"
        )
        for index in (1, 7):
            window.requireProject().add_polygon(index, polygon)
            window.requireProject().add_polygon(index, erase)
        window.requireProject().set_force_empty(4, True)
        window.commit_change()
        window.refresh_slice()
        return C_ArrayFactory().wrap(window.requireProject().to_mask(interpolate=True))

    # 构造带测试切片的画布，供鼠标交互和显示断言使用。
    def canvas(
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
        return (
            window.getCanvas()
            if name == "LP"
            else window.getObservationWindow(name).getCanvas()
        )

    # 提取画布遮罩的前景像素，用于比较显示结果和预期掩码。
    def overlay_mask(
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
        from med_image_seg.Concrete.Numerics.Arrays.C_ArrayFactory import C_ArrayFactory

        image = canvas.requireInternalInterpolationItem().pixmap().toImage()
        return C_ArrayFactory().wrap(
            np.array(
                [
                    [
                        image.pixelColor(horizontal, vertical).alpha() > 0
                        for horizontal in range(image.width())
                    ]
                    for vertical in range(image.height())
                ],
                dtype=bool,
            )
        )
