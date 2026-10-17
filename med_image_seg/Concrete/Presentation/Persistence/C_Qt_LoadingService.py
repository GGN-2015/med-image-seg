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

from PySide6.QtCore import QPointF, QRectF, QThread, QTimer, SignalInstance
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


# 管理影像加载与卸载，统一处理项目保存、视图释放和 Qt 控件状态恢复。
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
        from ..Progress.C_Qt_EstimatedProgressDialog import C_Qt_EstimatedProgressDialog

        context.requireCentralWidget().setEnabled(False)
        for view in context.iterObservationWindows():
            view.getHost().setEnabled(False)
        context.getExportAction().setEnabled(False)
        context.getExportUbdAction().setEnabled(False)
        context.getExportJsonAction().setEnabled(False)
        dialog = C_Qt_EstimatedProgressDialog(
            context._text("loading_message", path=str(source.getPath())),
            context._text("loading_title"),
            f"volume.load.{source.getKind().value}",
            default_seconds=30.0,
            language=context.getLanguage(),
            parent=context.getHost(),
        )
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
            if context.getInternalLoadError() is None:
                context.requireLoadingDialog().accept()
            else:
                context.requireLoadingDialog().reject()
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

    # 保存成功后释放影像及三视图缓存，仅从集合移除来源，不操作影像文件。
    def unload_imported_image(
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
    ) -> bool:
        source = context.getCurrentSource()
        if (
            source is None
            or context.getVolume() is None
            or context.getProject() is None
            or context.getLoadThread() is not None
            or context.getExternalMaskThread() is not None
            or context.getInternalClosingPolygon()
            or context.getInternalSwitchingAnnotation()
        ):
            return False
        context.getCanvas().finish_polygon()
        editing_interpolation = (
            context.getInternalEditingInterpolationVisible()
            if context.getReadOnly()
            else context.getShowInterpolation().isChecked()
        )
        with context._polygon_busy_ui("unloading_image_status"):
            if not context.save_project(notify=True, force=True):
                return False
            context.getSources().removeByFingerprint(source.getFingerprint())
            context.setCurrentSource(None)
            context.setVolume(None)
            context.setProject(None)
            context.setProjectPath(None)
            context.setInternalLoadingSource(None)
            context.setInternalLoadError(None)
            context.setInternalDirty(False)
            context.setInternalMaskCoverageDirty(True)
            context.setInternalObservationMask(None)
            context.setObservationPosition((0, 0, 0))
            context.setCurrentSlice(0)
            context.setAnnotationIndex(0)
            context.setReadOnly(False)
            context.setExternalMask(None)
            context.setExternalMaskPath(None)
            context.setInternalExternalViewState(None)
            context.setInternalExternalMaskError(None)
            context.getCanvas().clear_slice()
            context.getCanvas().set_read_only(False)
            context.getCanvas().set_operation("add")
            context.getAddRadio().setChecked(True)
            for view in context.iterObservationWindows():
                view.getCanvas().clear_slice()
                view.getCanvas().set_crosshair(None, (0, 0, 0))
                view.getSliceSpin().setRange(0, 0)
                view.getHost().hide()
            context.getSliceSlider().setRange(0, 0)
            context.getSliceSpin().setRange(0, 0)
            context.getMaskCoverageBar().set_presence(())
            context.getReviewProgress().setRange(0, 1)
            context.getReviewProgress().reset()
            context.getCompletedCheck().setChecked(False)
            context.getForceEmptyCheck().setChecked(False)
            context.getShowInterpolation().setChecked(editing_interpolation)
            context.setInternalEditingInterpolationVisible(editing_interpolation)
            context._sync_annotation_index_spin()
            context._refresh_source_list()
        self.finish_loading_ui(context)
        context._retranslate_ui()
        context.getHost().statusBar().showMessage(
            context._text("image_unloaded", name=source.getDisplayName())
        )
        return True

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
            if project.getSourceFingerprint() != source.getFingerprint():
                raise ValueError("annotation fingerprint does not match this image")
            project.validate_volume(volume)
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
