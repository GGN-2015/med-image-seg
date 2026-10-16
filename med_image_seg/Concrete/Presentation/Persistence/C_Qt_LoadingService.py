from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QGraphicsPathItem

from ....Abstract.Domain.Annotations.I_MutableAnnotationProject import (
    I_MutableAnnotationProject,
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
from ....Abstract.Presentation.Persistence.T_LoadingService import T_LoadingService
from ....Abstract.Presentation.Window.T_MutableAnnotationMainWindow import (
    T_MutableAnnotationMainWindow,
)

if TYPE_CHECKING:
    from ....Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
    from ....Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
from typing import final

from PySide6.QtCore import QPointF, QRectF, Qt, QThread, QTimer, SignalInstance
from PySide6.QtGui import QAction, QShortcut
from PySide6.QtWidgets import (
    QAbstractSpinBox,
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


# 管理加载提示及控件禁用状态，打开当前编号项目并更新自动保存提示。
@final
class C_Qt_LoadingService(
    T_LoadingService[
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
    # 禁用三个视图和编辑入口，并显示不可取消的加载进度提示。
    def show_loading(
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
        source: I_ImageSource,
    ) -> None:
        context.requireCentralWidget().setEnabled(False)
        for view in context.iterObservationWindows():
            view.getHost().setEnabled(False)
        context.getExportAction().setEnabled(False)
        context.getExportUbdAction().setEnabled(False)
        context.getExportJsonAction().setEnabled(False)
        dialog = QProgressDialog(
            context._text("loading_message", path=str(source.getPath())),
            "",
            0,
            0,
            context.getHost(),
        )
        dialog.setWindowTitle(context._text("loading_title"))
        dialog.setCancelButton(None)
        dialog.setMinimumDuration(0)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.setAutoClose(False)
        dialog.setAutoReset(False)
        dialog.show()
        context.setLoadingDialog(dialog)
        context.getHost().statusBar().showMessage(
            context._text("loading_status", name=source.getDisplayName())
        )

    # 关闭加载提示并恢复先前控件状态，结束影像加载阶段。
    def finish_loading_ui(
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
    ) -> None:
        if context.getLoadingDialog() is not None:
            context.requireLoadingDialog().close()
            context.requireLoadingDialog().deleteLater()
            context.setLoadingDialog(None)
        context.requireCentralWidget().setEnabled(True)
        has_volume = (
            context.getVolume() is not None and context.getProject() is not None
        )
        for widget in context.iterEditorWidgets():
            widget.setEnabled(has_volume)
        context.getExportAction().setEnabled(has_volume)
        context.getExportUbdAction().setEnabled(has_volume)
        context.getExportJsonAction().setEnabled(has_volume)
        for view in context.iterObservationWindows():
            view.getHost().setEnabled(has_volume)
        context._apply_mode_ui()

    # 打开当前编号的 JSON 或备份；文件不存在时创建对应的新项目。
    def open_annotation_project(
        self, source: I_ImageSource, volume: I_MedicalVolume, index: int
    ) -> tuple[I_MutableAnnotationProject, I_FilePath]:
        from ...Application.Projects.C_ProjectFactory import C_ProjectFactory
        from ...Storage.Paths.C_FilePath import C_FilePath
        from ...Storage.Projects.C_ProjectRepository import C_ProjectRepository

        path = source.annotation_path_for_index(index)
        if path.is_file() or C_FilePath(f"{path}.bak").is_file():
            project = C_ProjectRepository().load(path)
            project.validate_volume(volume)
            if project.getSourceFingerprint() != source.getFingerprint():
                raise ValueError("annotation fingerprint does not match this image")
        else:
            project = C_ProjectFactory().create(
                image_id=source.getSourceId(),
                source_fingerprint=source.getFingerprint(),
                volume=volume,
            )
            if index == 0:
                project.save(path)
        if index > 0 and (not project.getHasPolygons()):
            project.save(path, delete_if_empty=True)
        return (project, path)

    # 显示当前编号及落盘路径，外置预览时明确标注保存已暂停。
    def show_annotation_path(
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
    ) -> None:
        if context.getExternalPreviewActive():
            context.getAutosaveStatus().setText(
                context._text(
                    "external_mask_json_paused",
                    index=context.getAnnotationIndex(),
                    path=str(context.getProjectPath()),
                )
            )
            return
        empty_numbered = (
            context.getAnnotationIndex() > 0
            and context.getProject() is not None
            and (not context.requireProject().getHasPolygons())
        )
        context.getAutosaveStatus().setText(
            context._text(
                "annotation_empty_status" if empty_numbered else "autosave_path",
                index=context.getAnnotationIndex(),
                path=str(context.getProjectPath()),
            )
        )
