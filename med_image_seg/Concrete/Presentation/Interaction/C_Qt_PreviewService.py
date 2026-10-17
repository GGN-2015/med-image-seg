from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QGraphicsPathItem

from ....Abstract.Presentation.Canvas.T_MutableSliceCanvas import T_MutableSliceCanvas
from ....Abstract.Presentation.Canvas.T_MutableVertexHandle import T_MutableVertexHandle
from ....Abstract.Presentation.Interaction.T_PreviewService import T_PreviewService
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


# 协调外置掩码的只读预览，并刷新三个联动截面。
@final
class C_Qt_PreviewService(
    T_PreviewService[
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
    # 保存编辑状态并进入只读模式，为外置掩码选择和加载做准备。
    def begin_external_preview(
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
        from ...Domain.ViewState.C_ExternalMaskViewState import C_ExternalMaskViewState

        if (
            context.getExternalPreviewActive()
            or context.getLoadThread() is not None
            or context.getInternalClosingPolygon()
        ):
            return False
        if context.getVolume() is None or context.getProject() is None:
            QMessageBox.information(
                context.getHost(),
                context._text("external_mask_title"),
                context._text("external_mask_no_image"),
            )
            return False
        context.getCanvas().finish_polygon()
        if not context.save_project(notify=True):
            return False
        context.setInternalExternalViewState(
            C_ExternalMaskViewState(
                mode="observe"
                if context.getReadOnly()
                else context.getCanvas().getInternalOperation(),
                annotation_index=context.getAnnotationIndex(),
                position=context.getObservationPosition(),
                coverage=context.getMaskCoverageBar().getPresence(),
                autosave_active=context.getAutosaveTimer().isActive(),
            )
        )
        context.getAutosaveTimer().stop()
        context.getMaskCoverageBar().set_presence(
            [False] * context.requireVolume().getData().shape[2]
        )
        context.getObserveRadio().setChecked(True)
        context._apply_mode_ui()
        context.refresh_slice()
        return True

    # 在后台读取选中的外置掩码，并锁定相关操作直到结果返回。
    def start_external_mask_load(
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
        path: I_FilePath,
    ) -> None:
        from ..Loading.C_Qt_ExternalMaskLoadThread import C_Qt_ExternalMaskLoadThread

        assert context.getVolume() is not None
        context.setExternalMaskPath(path.expanduser().resolve())
        context.setInternalExternalMaskError(None)
        context.clearExternalLoadingWidgetStates()
        for widget in (
            context.requireCentralWidget(),
            context.getAnnotationToolbar(),
            *(view.getHost() for view in context.iterObservationWindows()),
        ):
            _state_item = (widget, widget.isEnabled())
            context.rememberExternalLoadingWidget(_state_item[0], _state_item[1])
        context.clearExternalLoadingShortcutStates()
        for shortcut in context.getHost().findChildren(QShortcut):
            _state_item = (shortcut, shortcut.isEnabled())
            context.rememberExternalLoadingShortcut(_state_item[0], _state_item[1])
        for _state_index in range(context.getExternalLoadingWidgetCount()):
            widget = context.getExternalLoadingWidget(_state_index)
            _enabled = context.getExternalLoadingWidgetEnabled(_state_index)
            widget.setEnabled(False)
        for _state_index in range(context.getExternalLoadingShortcutCount()):
            shortcut = context.getExternalLoadingShortcut(_state_index)
            _enabled = context.getExternalLoadingShortcutEnabled(_state_index)
            shortcut.setEnabled(False)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        from ..Progress.C_Qt_EstimatedProgressDialog import C_Qt_EstimatedProgressDialog

        dialog = C_Qt_EstimatedProgressDialog(
            context._text(
                "external_mask_loading", path=str(context.getExternalMaskPath())
            ),
            context._text("external_mask_title"),
            "external-mask.load",
            default_seconds=10.0,
            language=context.getLanguage(),
            parent=context.getHost(),
        )
        dialog.show()
        context.setExternalLoadingDialog(dialog)
        context.setExternalMaskThread(
            C_Qt_ExternalMaskLoadThread(
                context.requireExternalMaskPath(),
                context.requireVolume(),
                context.getHost(),
            )
        )
        context.requireExternalMaskThread().getLoaded().connect(
            context.external_mask_loaded
        )
        context.requireExternalMaskThread().getFailed().connect(
            context.external_mask_load_failed
        )
        context.requireExternalMaskThread().getHost().finished.connect(
            context.external_mask_thread_finished
        )
        context.requireExternalMaskThread().getHost().start()

    # 按共享交点刷新 LP、PS、SL 切片、掩码和参考线。
    def refresh_observation_views(
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
        from ...Algorithms.Observation.C_ObservationPlanes import C_ObservationPlanes
        from ...Algorithms.Observation.C_OverlayPalette import C_OverlayPalette

        assert context.getVolume() is not None
        external = context.getExternalPreviewActive()
        mask = (
            context.getExternalMask()
            if external
            else context.getInternalObservationMask()
        )
        if not external:
            assert mask is not None
        context.getCanvas().set_crosshair(
            C_ObservationPlanes().getPlanes().getLP(), context.getObservationPosition()
        )
        context.getObservationStatus().setText(
            context._text(
                "observation_position",
                **dict(zip("LPS", context.getObservationPosition(), strict=True)),
            )
        )
        for view in context.iterObservationWindows():
            plane = view.getPlane()
            index = context.getObservationPosition()[plane.getFixedAxis()]
            axis = "LPS"[plane.getFixedAxis()]
            view.getCanvas().set_slice(
                context._windowed_plane(
                    plane.section(
                        context.requireVolume().getData(),
                        context.getObservationPosition(),
                    )
                ),
                [],
                None
                if mask is None
                else plane.section(mask, context.getObservationPosition()),
                overlay_color=C_OverlayPalette().getExternalMaskColor()
                if external
                else (49, 180, 255, 72),
            )
            view.getCanvas().set_crosshair(plane, context.getObservationPosition())
            view.getSliceSpin().blockSignals(True)
            view.getSliceSpin().setRange(
                0, context.requireVolume().getData().shape[plane.getFixedAxis()] - 1
            )
            view.getSliceSpin().setValue(index)
            view.getSliceSpin().blockSignals(False)
            view.getSliceLabel().setText(context._text("observation_slice", axis=axis))
            view.getAxesLabel().setText(
                context._text(
                    "observation_axes",
                    horizontal="LPS"[plane.getHorizontalAxis()],
                    vertical="LPS"[plane.getVerticalAxis()],
                )
            )
            view.getHost().setWindowTitle(
                context._text(
                    "observation_title", plane=plane.getName(), axis=axis, index=index
                )
            )
            if context.getHost().isVisible():
                view.getHost().show()
