from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QGraphicsPathItem

from ....Abstract.Presentation.Canvas.T_MutableSliceCanvas import T_MutableSliceCanvas
from ....Abstract.Presentation.Canvas.T_MutableVertexHandle import T_MutableVertexHandle
from ....Abstract.Presentation.Loading.T_MutableExternalMaskLoadThread import (
    T_MutableExternalMaskLoadThread,
)
from ....Abstract.Presentation.Loading.T_MutableVolumeLoadThread import (
    T_MutableVolumeLoadThread,
)
from ....Abstract.Presentation.Navigation import (
    T_MutableAnnotationIndexSpinBox,
)
from ....Abstract.Presentation.Navigation.T_MutableMaskCoverageBar import (
    T_MutableMaskCoverageBar,
)
from ....Abstract.Presentation.Observation import (
    T_MutableOrthogonalSliceWindow,
)
from ....Abstract.Presentation.Persistence.T_ExportService import T_ExportService
from ....Abstract.Presentation.Window.T_MutableAnnotationMainWindow import (
    T_MutableAnnotationMainWindow,
)

if TYPE_CHECKING:
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
from typing import final

from PySide6.QtCore import QPointF, QRectF, Qt, QThread, QTimer, SignalInstance
from PySide6.QtGui import QAction, QShortcut
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGraphicsEllipseItem,
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


# 处理界面导出请求和成功失败提示，把写盘工作交给导出接口。
@final
class C_Qt_ExportService(
    T_ExportService[
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
    # 检查导出条件并执行掩码写入，只在成功后显示完成提示。
    def export_mask(
        self,
        context: T_MutableAnnotationMainWindow[
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
        output: I_FilePath,
    ) -> None:
        from ...Application.Projects.C_AnnotationExporter import C_AnnotationExporter

        if (
            context.getProject() is None
            or context.getVolume() is None
            or context.getExternalPreviewActive()
        ):
            return
        if not context.save_project(notify=True):
            return
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            C_AnnotationExporter().export(
                context.requireProject(),
                context.requireVolume(),
                output,
                interpolate=True,
            )
        except Exception as exc:
            QMessageBox.critical(
                context.getHost(), context._text("export_failed_title"), str(exc)
            )
            return
        finally:
            QApplication.restoreOverrideCursor()
        QMessageBox.information(
            context.getHost(),
            context._text("export_complete_title"),
            context._text(
                "export_complete_message",
                path=str(output),
                count=context.requireProject().getInterpolatedSliceCount(),
            ),
        )
