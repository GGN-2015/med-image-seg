from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, QThread, QTimer, SignalInstance
from PySide6.QtGui import QAction
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

from ...Abstract.Editor.T_GuiFixtures import T_GuiFixtures

if TYPE_CHECKING:
    from med_image_seg.Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
    from med_image_seg.Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from med_image_seg.Abstract.Presentation.Window import (
        T_MutableAnnotationMainWindow,
    )
    from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath
import json
from typing import final

import numpy as np
import SimpleITK as sitk
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut
from PySide6.QtWidgets import QApplication


# 构造界面测试的影像与窗口，并驱动后台加载和事件循环。
@final
class C_GuiFixtures(
    T_GuiFixtures[
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

    # 创建临时影像源，统一测试项目的配套文件路径和指纹。
    def source(self, tmp_path: I_FilePath) -> I_ImageSource:
        from med_image_seg.Concrete.Storage.Volumes.C_ImageSourceFactory import (
            C_ImageSourceFactory,
        )

        image = tmp_path / "scan.nii.gz"
        image.write_bytes(b"synthetic-nifti-placeholder")
        return C_ImageSourceFactory().from_path(image)

    # 构造与测试影像源对应的体素和几何信息。
    def volume(self, source: I_ImageSource) -> I_MedicalVolume:
        from med_image_seg.Concrete.Domain.Imaging.C_MedicalVolume import (
            C_MedicalVolume,
        )
        from med_image_seg.Concrete.Domain.Imaging.C_Metadata import C_Metadata

        return C_MedicalVolume(
            data=np.arange(20 * 16 * 5, dtype=np.float32).reshape(20, 16, 5),
            spacing_mm=(0.8, 0.8, 0.8),
            origin_lps_mm=(0.0, 0.0, 0.0),
            metadata=C_Metadata(json.dumps({"modality": "CT"})),
            source=source.getPath(),
        )

    # 写入具有已知几何的 NIfTI 测试影像。
    def write_nifti(self, path: I_FilePath) -> None:
        image = sitk.GetImageFromArray(
            np.arange(8 * 12 * 16, dtype=np.float32).reshape(8, 12, 16)
        )
        image.SetSpacing((1.0, 1.0, 1.0))
        sitk.WriteImage(image, str(path))

    # 断言闭合计算期间编辑控件和快捷键均被禁用。
    def assert_polygon_busy(
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

        assert window.getInternalClosingPolygon()
        assert not window.getHost().isEnabled()
        assert not window.requireCentralWidget().isEnabled()
        assert not window.getAnnotationToolbar().isEnabled()
        assert not window.getCanvas().getHost().isEnabled()
        assert all(
            not action.isEnabled() for action in window.getAnnotationToolbar().actions()
        )
        assert all(
            not shortcut.isEnabled()
            for shortcut in window.getHost().findChildren(QShortcut)
        )
        assert not window.getAutosaveTimer().isActive()
        assert window.getHost().statusBar().currentMessage() == C_Localizer().translate(
            "closing_polygon_status", window.getLanguage()
        )
        cursor = QApplication.overrideCursor()
        assert cursor is not None
        assert cursor.shape() == Qt.CursorShape.WaitCursor
