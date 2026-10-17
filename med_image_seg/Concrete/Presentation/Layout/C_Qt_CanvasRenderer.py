from __future__ import annotations

from typing import final

from PySide6.QtCore import QPointF, QRectF, SignalInstance
from PySide6.QtGui import QBrush, QColor, QPainterPath, QPen
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsPathItem,
    QGraphicsPixmapItem,
    QGraphicsPolygonItem,
    QGraphicsView,
)

from ....Abstract.Presentation.Canvas.T_MutableSliceCanvas import T_MutableSliceCanvas
from ....Abstract.Presentation.Canvas.T_MutableVertexHandle import T_MutableVertexHandle
from ....Abstract.Presentation.Layout.T_CanvasRenderer import T_CanvasRenderer


# 重绘多边形草稿路径，让画布事件处理不承担路径构造细节。
@final
class C_Qt_CanvasRenderer(
    T_CanvasRenderer[
        T_MutableSliceCanvas[
            QGraphicsView,
            QPointF,
            QRectF,
            QGraphicsPixmapItem,
            QGraphicsPathItem,
            QGraphicsPolygonItem,
            T_MutableVertexHandle[QGraphicsEllipseItem],
            SignalInstance,
        ]
    ]
):
    # 重建未闭合轮廓的路径图元，使鼠标绘制结果及时显示。
    def update_draft(
        self,
        context: T_MutableSliceCanvas[
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
        draft_item = context.getInternalDraftItem()
        if draft_item is not None:
            context.getHost().scene().removeItem(draft_item)
        if context.getDraftPointCount() == 0:
            context.setInternalDraftItem(None)
            return
        path = QPainterPath(context.getDraftPoint(0))
        for index in range(1, context.getDraftPointCount()):
            path.lineTo(context.getDraftPoint(index))
        draft_item = (
            context.getHost().scene().addPath(path, QPen(QColor("#ffd166"), 2.0))
        )
        first_point_marker = QGraphicsEllipseItem(-3.5, -3.5, 7.0, 7.0, draft_item)
        first_point_marker.setPos(context.getDraftPoint(0))
        first_point_marker.setPen(QPen(QColor("#ffd166"), 1.0))
        first_point_marker.setBrush(QBrush(QColor("#ffd166")))
        first_point_marker.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True
        )
        context.setInternalDraftItem(draft_item)
        context.requireInternalDraftItem().setZValue(3)
