from __future__ import annotations

from typing import final

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem

from ....Abstract.Presentation.Canvas.T_MutableVertexHandle import T_MutableVertexHandle
from ..Metaclasses.C_Qt_AbcMeta import C_Qt_AbcMeta


# 表示可拖动顶点，携带多边形和顶点索引以定位编辑目标。
@final
class C_Qt_VertexHandle(
    QGraphicsEllipseItem,
    T_MutableVertexHandle[QGraphicsEllipseItem],
    metaclass=C_Qt_AbcMeta,
):
    # 返回顶点控件所属的多边形索引。
    def getPolygonIndex(self) -> int:
        return self._state_polygon_index

    # 记录顶点控件所属的多边形索引。
    def setPolygonIndex(self, value: int) -> None:
        self._state_polygon_index = value

    # 返回顶点在所属轮廓中的索引。
    def getVertexIndex(self) -> int:
        return self._state_vertex_index

    # 记录顶点在所属多边形中的索引。
    def setVertexIndex(self, value: int) -> None:
        self._state_vertex_index = value

    # 创建顶点图元，并记录所属轮廓及顶点索引。
    def __init__(self, polygon_index: int, vertex_index: int, color: QColor) -> None:
        super().__init__(-4.5, -4.5, 9.0, 9.0)
        self.setPolygonIndex(polygon_index)
        self.setVertexIndex(vertex_index)
        self.setPen(QPen(QColor("#ffffff"), 1.0))
        self.setBrush(QBrush(color))
        self.setZValue(4)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        self.setCursor(Qt.CursorShape.SizeAllCursor)

    # 返回底层界面宿主。
    def getHost(self) -> QGraphicsEllipseItem:
        return self
