from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QGraphicsPathItem

from ....Abstract.Presentation.Canvas.T_MutableSliceCanvas import T_MutableSliceCanvas
from ....Abstract.Presentation.Canvas.T_MutableVertexHandle import T_MutableVertexHandle
from ....Abstract.Presentation.Observation import (
    T_MutableOrthogonalSliceWindow,
)
from ..Metaclasses.C_Qt_AbcMeta import C_Qt_AbcMeta

if TYPE_CHECKING:
    from ....Abstract.Domain.Imaging.I_ObservationPlane import I_ObservationPlane
from typing import final

from PySide6.QtCore import QPointF, QRectF, Qt, SignalInstance
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsPixmapItem,
    QGraphicsPolygonItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


# 承载 PS 或 SL 只读截面，以不可关闭的非模态窗口参与三视图联动。
@final
class C_Qt_OrthogonalSliceWindow(
    QWidget,
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
    metaclass=C_Qt_AbcMeta,
):
    # 返回当前窗口的截面定义。
    def getPlane(self) -> I_ObservationPlane:
        return self._state_plane

    # 记录当前窗口的截面定义。
    def setPlane(self, value: I_ObservationPlane) -> None:
        self._state_plane = value

    # 返回截面轴向标签。
    def getAxesLabel(self) -> QLabel:
        return self._state_axes_label

    # 记录截面轴向标签。
    def setAxesLabel(self, value: QLabel) -> None:
        self._state_axes_label = value

    # 返回切片画布。
    def getCanvas(
        self,
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
        return self._state_canvas

    # 记录切片画布。
    def setCanvas(
        self,
        value: T_MutableSliceCanvas[
            QGraphicsView,
            QPointF,
            QRectF,
            QGraphicsPixmapItem,
            QGraphicsPathItem,
            QGraphicsPolygonItem,
            T_MutableVertexHandle[QGraphicsEllipseItem],
            SignalInstance,
        ],
    ) -> None:
        self._state_canvas = value

    # 返回当前切片编号标签。
    def getSliceLabel(self) -> QLabel:
        return self._state_slice_label

    # 记录当前切片编号标签。
    def setSliceLabel(self, value: QLabel) -> None:
        self._state_slice_label = value

    # 返回当前切片编号输入框。
    def getSliceSpin(self) -> QSpinBox:
        return self._state_slice_spin

    # 记录当前切片编号输入框。
    def setSliceSpin(self, value: QSpinBox) -> None:
        self._state_slice_spin = value

    # 创建只读截面画布和层号控件，禁用独立关闭并保持非模态。
    def __init__(self, parent: QWidget, plane: I_ObservationPlane) -> None:
        from ..Canvas.C_Qt_SliceCanvas import C_Qt_SliceCanvas

        super().__init__(
            parent,
            Qt.WindowType.Window
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowMinMaxButtonsHint,
        )
        self.setPlane(plane)
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.resize(560, 540)
        layout = QVBoxLayout(self)
        self.setAxesLabel(QLabel())
        layout.addWidget(self.getAxesLabel())
        self.setCanvas(C_Qt_SliceCanvas())
        self.getCanvas().set_read_only(True)
        layout.addWidget(self.getCanvas().getHost(), 1)
        navigation = QHBoxLayout()
        self.setSliceLabel(QLabel())
        navigation.addWidget(self.getSliceLabel())
        self.setSliceSpin(QSpinBox())
        navigation.addWidget(self.getSliceSpin())
        layout.addLayout(navigation)

    # 忽略独立关闭请求，让附属视图的可见性由主窗口控制。
    def closeEvent(self, event: QCloseEvent) -> None:
        event.ignore()

    # 返回底层界面宿主。
    def getHost(self) -> QWidget:
        return self
