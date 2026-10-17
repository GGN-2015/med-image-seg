from __future__ import annotations

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
    QFileDialog,
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
from ....Abstract.Storage.Paths.I_FilePath import I_FilePath


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
    # 打开系统另存为窗口，并在用户未输入格式后缀时补齐所选导出格式。
    def select_output(
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
        suggested_output: I_FilePath,
        title: str,
        file_filter: str,
        required_suffix: str,
    ) -> I_FilePath | None:
        from ...Storage.Paths.C_FilePath import C_FilePath

        selected, _ = QFileDialog.getSaveFileName(
            context.getHost(), title, str(suggested_output), file_filter
        )
        if not selected:
            return None
        has_suffix = selected.casefold().endswith(required_suffix.casefold()) or (
            required_suffix == ".med-image-seg.json"
            and selected.casefold().endswith(".json")
        )
        if not has_suffix:
            selected = f"{selected}{required_suffix}"
        output = C_FilePath(selected).expanduser().resolve()
        if not has_suffix and output.exists():
            answer = QMessageBox.question(
                context.getHost(),
                context._text("export_overwrite_title"),
                context._text("export_overwrite_message", path=str(output)),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return None
        return output

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
        from ...Application.Tasks.C_ExportMaskTask import C_ExportMaskTask
        from ..Progress.C_ProgressDialogSettings import C_ProgressDialogSettings
        from ..Tasks.C_Qt_BackgroundTaskRunner import C_Qt_BackgroundTaskRunner

        if (
            context.getProject() is None
            or context.getVolume() is None
            or context.getExternalPreviewActive()
            or context.getInternalClosingPolygon()
        ):
            return
        operation = (
            "ui.mask.export.ubd"
            if str(output).lower().endswith(".ubd.npz")
            else "ui.mask.export.nifti"
        )
        try:
            with context._polygon_busy_ui(
                "export_mask_status",
                progress_settings=C_ProgressDialogSettings(
                    operation, "export_mask_progress_title", 10.0
                ),
            ):
                if not context.save_project(notify=True):
                    dialog = context.getBusyProgressDialog()
                    if dialog is not None:
                        dialog.reject()
                    return
                C_Qt_BackgroundTaskRunner[I_FilePath]().run(
                    C_ExportMaskTask(
                        C_AnnotationExporter(),
                        context.requireProject(),
                        context.requireVolume(),
                        output,
                    )
                )
        except Exception as exc:
            QMessageBox.critical(
                context.getHost(), context._text("export_failed_title"), str(exc)
            )
            return
        QMessageBox.information(
            context.getHost(),
            context._text("export_complete_title"),
            context._text(
                "export_complete_message",
                path=str(output),
                count=context.requireProject().getInterpolatedSliceCount(),
            ),
        )

    # 保存当前项目到用户选择的 JSON 文件，并保留编号空文件删除规则。
    def export_annotations(
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
        if (
            context.getProject() is None
            or context.getProjectPath() is None
            or context.getExternalPreviewActive()
        ):
            return
        if not context.save_project(notify=True, force=True):
            return
        empty_numbered = context.getAnnotationIndex() > 0 and (
            not context.requireProject().getHasPolygons()
        )
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            if output.resolve() != context.requireProjectPath().resolve():
                context.requireProject().save(output, delete_if_empty=empty_numbered)
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
                "export_annotations_empty_message"
                if empty_numbered
                else "export_annotations_complete_message",
                index=context.getAnnotationIndex(),
                path=str(output),
            ),
        )
