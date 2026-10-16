from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import final

import numpy as np
from numpy.typing import NDArray
from PySide6.QtCore import (
    QEventLoop,
    QPointF,
    QRectF,
    Qt,
    QThread,
    QTimer,
    SignalInstance,
)
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

from ....Abstract.Presentation.Canvas.T_MutableSliceCanvas import T_MutableSliceCanvas
from ....Abstract.Presentation.Canvas.T_MutableVertexHandle import T_MutableVertexHandle
from ....Abstract.Presentation.Interaction.T_InteractionService import (
    T_InteractionService,
)
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


# 处理界面锁定、窗宽窗位和十字线点击，隔离 Qt 交互细节。
@final
class C_Qt_InteractionService(
    T_InteractionService[
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
        QPointF,
    ]
):
    # 临时禁用主界面、附属窗口和快捷键，在闭合流程结束后恢复原状态。
    @contextmanager
    def polygon_busy_ui(
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
        status_key: str = "closing_polygon_status",
    ) -> Iterator[None]:
        was_enabled = context.getHost().isEnabled()
        action_states = [
            (action, action.isEnabled())
            for action in context.getAnnotationToolbar().actions()
        ]
        shortcut_states = [
            (shortcut, shortcut.isEnabled())
            for shortcut in context.getHost().findChildren(QShortcut)
        ]
        autosave_active = context.getAutosaveTimer().isActive()
        previous_message = context.getHost().statusBar().currentMessage()
        context.setInternalClosingPolygon(True)
        context.getAutosaveTimer().stop()
        context.getHost().setEnabled(False)
        for action, _enabled in action_states:
            action.setEnabled(False)
        for shortcut, _enabled in shortcut_states:
            shortcut.setEnabled(False)
        context.getHost().statusBar().showMessage(context._text(status_key))
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            QApplication.processEvents(
                QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents
            )
            yield
        finally:
            try:
                QApplication.processEvents()
            finally:
                context.getHost().setEnabled(was_enabled)
                for action, enabled in action_states:
                    action.setEnabled(enabled)
                for shortcut, enabled in shortcut_states:
                    shortcut.setEnabled(enabled)
                context.getHost().statusBar().showMessage(previous_message)
                QApplication.restoreOverrideCursor()
                context.setInternalClosingPolygon(False)
                if autosave_active:
                    context.getAutosaveTimer().start()

    # 把截面点击转换为共享体素交点，并同步其余截面的层号。
    def observation_clicked(
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
        name: str,
        point: QPointF,
    ) -> None:
        from ...Algorithms.Observation.C_ObservationPlanes import C_ObservationPlanes

        if not context.getReadOnly() or context.getVolume() is None:
            return
        context.setObservationPosition(
            C_ObservationPlanes()
            .getPlanes()
            .getByName(name)
            .position_at(
                context.getObservationPosition(),
                point.x(),
                point.y(),
                context.requireVolume().getData().shape,
            )
        )
        context.set_slice(context.getObservationPosition()[2])

    # 修改指定截面的固定轴坐标，限制到影像范围后同步三个视图。
    def set_observation_axis(
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
        name: str,
        index: int,
    ) -> None:
        from ...Algorithms.Observation.C_ObservationPlanes import C_ObservationPlanes

        if not context.getReadOnly() or context.getVolume() is None:
            return
        axis = C_ObservationPlanes().getPlanes().getByName(name).getFixedAxis()
        position = list(context.getObservationPosition())
        position[axis] = int(
            np.clip(index, 0, context.requireVolume().getData().shape[axis] - 1)
        )
        context.setObservationPosition((position[0], position[1], position[2]))
        context.set_slice(context.getObservationPosition()[2])

    # 将当前 LP 层按窗宽窗位转换为显示灰度。
    def windowed_slice(
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
    ) -> NDArray[np.uint8]:
        from ...Numerics.Arrays.C_ArrayFactory import C_ArrayFactory

        assert context.getVolume() is not None
        plane = context.requireVolume().getData()[:, :, context.getCurrentSlice()].T
        return C_ArrayFactory().wrap(context._windowed_plane(plane))

    # 将指定截面按当前窗宽窗位转换为显示灰度。
    def windowed_plane(
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
        plane: NDArray[np.float32],
    ) -> NDArray[np.uint8]:
        from ...Numerics.Arrays.C_ArrayFactory import C_ArrayFactory

        level = context.getLevelSpin().value()
        width = context.getWidthSpin().value()
        low = level - width / 2
        scaled = np.clip((plane - low) / width, 0.0, 1.0)
        return C_ArrayFactory().wrap(np.asarray(np.rint(scaled * 255), dtype=np.uint8))
