from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from PySide6.QtCore import QRect
from PySide6.QtWidgets import QGraphicsPathItem

from ....Abstract.Domain.Annotations.I_PolygonAnnotation import I_PolygonAnnotation
from ....Abstract.Domain.Geometry.I_PointList import I_PointList
from ....Abstract.Domain.Imaging.I_ObservationPlane import I_ObservationPlane
from ....Abstract.Presentation.Canvas.T_MutableSliceCanvas import T_MutableSliceCanvas
from ....Abstract.Presentation.Canvas.T_MutableVertexHandle import T_MutableVertexHandle
from ..Metaclasses.C_Qt_AbcMeta import C_Qt_AbcMeta

if TYPE_CHECKING:
    from ....Abstract.Domain.Annotations.I_PolygonAnnotation import I_PolygonAnnotation
    from ....Abstract.Domain.Imaging.I_ObservationPlane import I_ObservationPlane
from typing import final

import numpy as np
from numpy.typing import NDArray
from PySide6.QtCore import QEventLoop, QPointF, QRectF, Qt, Signal, SignalInstance
from PySide6.QtGui import (
    QBrush,
    QColor,
    QImage,
    QMouseEvent,
    QPainter,
    QPen,
    QPixmap,
    QPolygonF,
    QResizeEvent,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsEllipseItem,
    QGraphicsPixmapItem,
    QGraphicsPolygonItem,
    QGraphicsScene,
    QGraphicsView,
)


# 绘制切片、轮廓和十字线，并将鼠标操作转换为编辑或定位信号。
@final
class C_Qt_SliceCanvas(
    QGraphicsView,
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
    metaclass=C_Qt_AbcMeta,
):
    # 返回显示插值或外置掩码的图元。
    def getInternalInterpolationItem(self) -> QGraphicsPixmapItem | None:
        return self._state_interpolation_item

    # 记录显示插值或外置掩码的图元。
    def setInternalInterpolationItem(self, value: QGraphicsPixmapItem | None) -> None:
        self._state_interpolation_item = value

    # 返回未闭合轮廓的路径图元。
    def getInternalDraftItem(self) -> QGraphicsPathItem | None:
        return self._state_draft_item

    # 记录未闭合轮廓的路径图元。
    def setInternalDraftItem(self, value: QGraphicsPathItem | None) -> None:
        self._state_draft_item = value

    # 返回当前正在拖动的顶点控件。
    def getInternalDraggingHandle(
        self,
    ) -> T_MutableVertexHandle[QGraphicsEllipseItem] | None:
        return self._state_dragging_handle

    # 记录当前正在拖动的顶点控件。
    def setInternalDraggingHandle(
        self, value: T_MutableVertexHandle[QGraphicsEllipseItem] | None
    ) -> None:
        self._state_dragging_handle = value

    # 返回当前添加或擦除操作。
    def getInternalOperation(self) -> str:
        return self._state_operation

    # 记录当前添加或擦除操作。
    def setInternalOperation(self, value: str) -> None:
        self._state_operation = value

    # 返回画布中当前图像的有效矩形。
    def getInternalImageRect(self) -> QRectF:
        return self._state_image_rect

    # 记录画布中当前图像的有效矩形。
    def setInternalImageRect(self, value: QRectF) -> None:
        self._state_image_rect = value

    # 返回画布是否尚未完成首次图像适配。
    def getInternalFirstImage(self) -> bool:
        return self._state_first_image

    # 记录画布是否尚未完成首次图像适配。
    def setInternalFirstImage(self, value: bool) -> None:
        self._state_first_image = value

    # 返回缩放是否继续自动适应窗口。
    def getInternalAutoFit(self) -> bool:
        return self._state_auto_fit

    # 记录缩放是否继续自动适应窗口。
    def setInternalAutoFit(self, value: bool) -> None:
        self._state_auto_fit = value

    # 返回是否处于禁止编辑的观察状态。
    def getReadOnly(self) -> bool:
        return self._state_read_only

    # 记录是否处于禁止编辑的观察状态。
    def setReadOnly(self, value: bool) -> None:
        self._state_read_only = value

    # 返回当前截面中的十字星坐标。
    def getInternalCrosshairPosition(self) -> QPointF | None:
        return self._state_crosshair_position

    # 记录当前截面中的十字星坐标。
    def setInternalCrosshairPosition(self, value: QPointF | None) -> None:
        self._state_crosshair_position = value

    # 返回十字星及两条参考线的颜色。
    def getInternalCrosshairColors(self) -> tuple[str, str, str]:
        return self._state_crosshair_colors

    # 记录十字星及两条参考线的颜色。
    def setInternalCrosshairColors(self, value: tuple[str, str, str]) -> None:
        self._state_crosshair_colors = value

    polygon_finished = Signal(object, str)
    polygon_changed = Signal(int, object)
    position_clicked = Signal(QPointF)

    # 创建场景并初始化图元、草稿和只读状态，准备接收显示与鼠标事件。
    def __init__(self) -> None:
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setBackgroundBrush(QColor("#111318"))
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setInternalInterpolationItem(None)
        self.setInternalDraftItem(None)
        self._state_draft_points = []
        self._state_polygon_items = []
        self._state_polygon_points = []
        self._state_handles = []
        self.setInternalDraggingHandle(None)
        self.setInternalOperation("add")
        self.setInternalImageRect(QRectF())
        self.setInternalFirstImage(True)
        self.setInternalAutoFit(True)
        self.setReadOnly(False)
        self.setInternalCrosshairPosition(None)
        self.setInternalCrosshairColors(("", "", ""))

    # 切换只读交互状态，清除拖动和草稿并更新顶点控件光标。
    def set_read_only(self, read_only: bool) -> None:
        self.setReadOnly(read_only)
        self.setInternalDraggingHandle(None)
        self.cancel_polygon()
        for handle in self._state_handles:
            handle.getHost().setCursor(
                Qt.CursorShape.ArrowCursor
                if read_only
                else Qt.CursorShape.SizeAllCursor
            )

    # 把共享体素交点投影到当前截面，并设置与其他截面一致的参考线颜色。
    def set_crosshair(
        self, plane: I_ObservationPlane | None, position: tuple[int, int, int]
    ) -> None:
        from ...Algorithms.Observation.C_ObservationPlanes import C_ObservationPlanes

        if plane is None:
            self.setInternalCrosshairPosition(None)
        else:
            self.setInternalCrosshairPosition(
                QPointF(
                    position[plane.getHorizontalAxis()] + 0.5,
                    position[plane.getVerticalAxis()] + 0.5,
                )
            )
            self.setInternalCrosshairColors(
                (
                    C_ObservationPlanes()
                    .getAxisColors()
                    .getByAxis(plane.getHorizontalAxis()),
                    C_ObservationPlanes()
                    .getAxisColors()
                    .getByAxis(plane.getVerticalAxis()),
                    plane.getColor(),
                )
            )
        self.viewport().update()

    # 在图像上绘制十字星及两条轴向参考线，不参与多边形编辑。
    def drawForeground(self, painter: QPainter, rect: QRectF | QRect) -> None:
        super().drawForeground(painter, rect)
        point = self.getInternalCrosshairPosition()
        if point is None:
            return
        painter.save()
        painter.setClipRect(self.getInternalImageRect())
        vertical_color, horizontal_color, center_color = (
            self.getInternalCrosshairColors()
        )
        for color, start, end in (
            (
                vertical_color,
                QPointF(point.x(), 0),
                QPointF(point.x(), self.getInternalImageRect().height()),
            ),
            (
                horizontal_color,
                QPointF(0, point.y()),
                QPointF(self.getInternalImageRect().width(), point.y()),
            ),
        ):
            pen = QPen(QColor(color), 1.0)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.drawLine(start, end)
        pen = QPen(QColor(center_color), 2.0)
        pen.setCosmetic(True)
        painter.setPen(pen)
        radius = 6.0 / max(abs(self.transform().m11()), 0.001)
        painter.drawLine(
            point + QPointF(-radius, -radius), point + QPointF(radius, radius)
        )
        painter.drawLine(
            point + QPointF(-radius, radius), point + QPointF(radius, -radius)
        )
        painter.drawEllipse(point, radius / 2, radius / 2)
        painter.restore()

    # 切换添加或擦除操作，同时丢弃尚未闭合的草稿。
    def set_operation(self, operation: str) -> None:
        self.setInternalOperation(operation)
        self.cancel_polygon()

    # 替换图像、轮廓与遮罩，清空上一层图元并按需要适配视野。
    def set_slice(
        self,
        image: NDArray[np.generic],
        polygons: Iterable[I_PolygonAnnotation],
        interpolated_mask: NDArray[np.generic] | None = None,
        *,
        overlay_color: tuple[int, int, int, int] = (49, 180, 255, 72),
    ) -> None:
        from .C_Qt_VertexHandle import C_Qt_VertexHandle

        self.scene().clear()
        self.setInternalInterpolationItem(None)
        self.setInternalDraftItem(None)
        self._state_draft_points.clear()
        self._state_polygon_items.clear()
        self._state_polygon_points.clear()
        self._state_handles.clear()
        self.setInternalDraggingHandle(None)
        grayscale = np.ascontiguousarray(image, dtype=np.uint8)
        height, width = grayscale.shape
        qimage = QImage(
            grayscale.data,
            width,
            height,
            grayscale.strides[0],
            QImage.Format.Format_Grayscale8,
        ).copy()
        image_item = self.scene().addPixmap(QPixmap.fromImage(qimage))
        image_item.setZValue(0)
        image_rect = QRectF(0, 0, width, height)
        image_size_changed = image_rect != self.getInternalImageRect()
        self.setInternalImageRect(image_rect)
        self.scene().setSceneRect(self.getInternalImageRect())
        if interpolated_mask is not None:
            overlay = np.zeros((height, width, 4), dtype=np.uint8)
            overlay[np.asarray(interpolated_mask, dtype=bool)] = overlay_color
            overlay_image = QImage(
                overlay.data,
                width,
                height,
                overlay.strides[0],
                QImage.Format.Format_RGBA8888,
            ).copy()
            self.setInternalInterpolationItem(
                self.scene().addPixmap(QPixmap.fromImage(overlay_image))
            )
            self.requireInternalInterpolationItem().setZValue(1)
        for polygon_index, polygon in enumerate(polygons):
            points = [
                QPointF(point.getX(), point.getY()) for point in polygon.getPoints()
            ]
            item = QGraphicsPolygonItem(QPolygonF(points))
            if polygon.getSource() == "prototype" and polygon.getOperation() == "add":
                color = QColor(255, 183, 77, 230)
                fill = QColor(255, 183, 77, 48)
            elif polygon.getSource() == "prototype":
                color = QColor(186, 104, 200, 230)
                fill = QColor(186, 104, 200, 45)
            elif polygon.getOperation() == "add":
                color = QColor(0, 224, 135, 220)
                fill = QColor(0, 224, 135, 45)
            else:
                color = QColor(255, 92, 92, 230)
                fill = QColor(255, 92, 92, 45)
            item.setPen(QPen(color, 1.5))
            item.setBrush(QBrush(fill))
            item.setZValue(2)
            self.scene().addItem(item)
            self._state_polygon_items.append(item)
            self._state_polygon_points.append(points)
            for vertex_index, point in enumerate(points):
                handle = C_Qt_VertexHandle(polygon_index, vertex_index, color)
                handle.setPos(point)
                if self.getReadOnly():
                    handle.setCursor(Qt.CursorShape.ArrowCursor)
                self.scene().addItem(handle)
                self._state_handles.append(handle)
                if not self.isEnabled() and len(self._state_handles) % 128 == 0:
                    QApplication.processEvents(
                        QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents
                    )
        if self.getInternalFirstImage() or image_size_changed:
            self.fitInView(
                self.getInternalImageRect(), Qt.AspectRatioMode.KeepAspectRatio
            )
            self.setInternalFirstImage(False)
            self.setInternalAutoFit(True)

    # 释放本层全部图元与交互状态，避免卸载后仍显示旧图或保留缩放。
    def clear_slice(self) -> None:
        self.scene().clear()
        self.setInternalInterpolationItem(None)
        self.setInternalDraftItem(None)
        self._state_draft_points.clear()
        self._state_polygon_items.clear()
        self._state_polygon_points.clear()
        self._state_handles.clear()
        self.setInternalDraggingHandle(None)
        self.setInternalCrosshairPosition(None)
        self.setInternalCrosshairColors(("", "", ""))
        self.setInternalImageRect(QRectF())
        self.scene().setSceneRect(QRectF())
        self.resetTransform()
        self.setInternalFirstImage(True)
        self.setInternalAutoFit(True)
        self.viewport().update()

    # 重建未闭合轮廓的路径图元，使鼠标绘制结果及时显示。
    def _update_draft(self) -> None:
        from ..Layout.C_Qt_CanvasRenderer import C_Qt_CanvasRenderer

        return C_Qt_CanvasRenderer().update_draft(self)

    # 仅在可编辑且顶点足够时闭合草稿，通过信号提交轮廓快照。
    def finish_polygon(self) -> None:
        from ...Domain.Geometry.C_PointList import C_PointList

        if (
            self.getReadOnly()
            or not self.isEnabled()
            or len(self._state_draft_points) < 3
        ):
            return
        points = [(point.x(), point.y()) for point in self._state_draft_points]
        self._state_draft_points.clear()
        self._update_draft()
        self.polygon_finished.emit(C_PointList(points), self.getInternalOperation())

    # 丢弃尚未闭合的草稿并清除其路径图元，不影响已有轮廓。
    def cancel_polygon(self) -> None:
        self._state_draft_points.clear()
        self._update_draft()

    # 按模式开始绘制、选择顶点或移动观察交点，禁止只读编辑。
    def mousePressEvent(self, event: QMouseEvent) -> None:
        from .C_Qt_VertexHandle import C_Qt_VertexHandle

        if self.getReadOnly():
            if event.button() == Qt.MouseButton.LeftButton:
                point = self.mapToScene(event.position().toPoint())
                if self.getInternalImageRect().contains(point):
                    self.position_clicked.emit(point)
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton:
            if not self._state_draft_points:
                item = self.itemAt(event.position().toPoint())
                if isinstance(item, C_Qt_VertexHandle):
                    self.setInternalDraggingHandle(item)
                    event.accept()
                    return
            point = self.mapToScene(event.position().toPoint())
            if self.getInternalImageRect().contains(point):
                self._state_draft_points.append(point)
                self._update_draft()
                event.accept()
                return
        if event.button() == Qt.MouseButton.RightButton:
            self.finish_polygon()
            event.accept()
            return
        super().mousePressEvent(event)

    # 拖动顶点时更新轮廓几何，未处理的鼠标移动交回 Qt。
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.getInternalDraggingHandle() is not None:
            point = self.mapToScene(event.position().toPoint())
            point = QPointF(
                float(
                    np.clip(
                        point.x(),
                        self.getInternalImageRect().left(),
                        self.getInternalImageRect().right(),
                    )
                ),
                float(
                    np.clip(
                        point.y(),
                        self.getInternalImageRect().top(),
                        self.getInternalImageRect().bottom(),
                    )
                ),
            )
            handle = self.requireInternalDraggingHandle()
            points = self._state_polygon_points[handle.getPolygonIndex()]
            points[handle.getVertexIndex()] = point
            handle.getHost().setPos(point)
            self._state_polygon_items[handle.getPolygonIndex()].setPolygon(
                QPolygonF(points)
            )
            event.accept()
            return
        super().mouseMoveEvent(event)

    # 结束顶点拖动并提交坐标快照，其余释放事件交回 Qt。
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        from ...Domain.Geometry.C_PointList import C_PointList

        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.getInternalDraggingHandle() is not None
        ):
            handle = self.requireInternalDraggingHandle()
            polygon_index = handle.getPolygonIndex()
            points = [
                (point.x(), point.y())
                for point in self._state_polygon_points[polygon_index]
            ]
            self.setInternalDraggingHandle(None)
            self.polygon_changed.emit(polygon_index, C_PointList(points))
            event.accept()
            return
        super().mouseReleaseEvent(event)

    # 把双击转换为轮廓闭合或只读定位，并保留 Qt 事件回溯。
    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if self.getReadOnly():
            self.mousePressEvent(event)
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.finish_polygon()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    # 根据滚轮调整画布缩放，并记录用户已主动改变视野。
    def wheelEvent(self, event: QWheelEvent) -> None:
        self.setInternalAutoFit(False)
        factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
        self.scale(factor, factor)
        event.accept()

    # 窗口缩放时按自动适配设置调整图像，保留用户主动缩放的结果。
    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if self.getInternalAutoFit() and (not self.getInternalImageRect().isEmpty()):
            self.fitInView(
                self.getInternalImageRect(), Qt.AspectRatioMode.KeepAspectRatio
            )

    # 返回底层界面宿主。
    def getHost(self) -> QGraphicsView:
        return self

    # 提供草稿闭合信号，交由项目层接收和保存轮廓。
    def getPolygonFinished(self) -> SignalInstance:
        return self.polygon_finished

    # 提供顶点编辑完成信号，载荷使用只读坐标快照。
    def getPolygonChanged(self) -> SignalInstance:
        return self.polygon_changed

    # 提供只读定位信号，供三个截面更新共享交点。
    def getPositionClicked(self) -> SignalInstance:
        return self.position_clicked

    # 返回尚未闭合的草稿顶点数量。
    def getDraftPointCount(self) -> int:
        return len(self._state_draft_points)

    # 按索引返回草稿点副本，防止外部修改画布坐标。
    def getDraftPoint(self, index: int) -> QPointF:
        return QPointF(self._state_draft_points[index])

    # 返回当前显示的轮廓图元数量。
    def getPolygonItemCount(self) -> int:
        return len(self._state_polygon_items)

    # 按索引查询轮廓图元，不暴露图元列表。
    def getPolygonItem(self, index: int) -> QGraphicsPolygonItem:
        return self._state_polygon_items[index]

    # 返回当前显示的多边形顶点控件数量。
    def getHandleCount(self) -> int:
        return len(self._state_handles)

    # 按索引取得顶点控件，不暴露控件存储列表。
    def getHandle(self, index: int) -> T_MutableVertexHandle[QGraphicsEllipseItem]:
        return self._state_handles[index]

    # 查询指定轮廓的顶点数量。
    def getPolygonPointCount(self, polygon_index: int) -> int:
        return len(self._state_polygon_points[polygon_index])

    # 按轮廓和顶点索引返回坐标副本，避免外部篡改画布几何。
    def getPolygonPoint(self, polygon_index: int, vertex_index: int) -> QPointF:
        return QPointF(self._state_polygon_points[polygon_index][vertex_index])

    # 复制只读顶点集合为画布草稿坐标，不接管调用方的可变存储。
    def setDraftPoints(self, points: I_PointList) -> None:
        self._state_draft_points = [
            QPointF(point.getX(), point.getY()) for point in points
        ]
