from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar, final

from ..Window.T_HostedObject import T_HostedObject

T_Handle = TypeVar("T_Handle")
T_Host = TypeVar("T_Host", covariant=True)
T_PixmapItem = TypeVar("T_PixmapItem")
T_Point = TypeVar("T_Point")
T_PolygonItem = TypeVar("T_PolygonItem")
T_Rect = TypeVar("T_Rect")
T_Signal = TypeVar("T_Signal")
T_DraftItem = TypeVar("T_DraftItem")


# 绘制切片、轮廓和十字线，并将鼠标操作转换为编辑或定位信号。
class T_SliceCanvas(
    T_HostedObject[T_Host],
    Generic[
        T_Host,
        T_Point,
        T_Rect,
        T_PixmapItem,
        T_DraftItem,
        T_PolygonItem,
        T_Handle,
        T_Signal,
    ],
):
    # 返回显示插值或外置掩码的图元。
    @abstractmethod
    def getInternalInterpolationItem(self) -> T_PixmapItem | None: ...

    # 返回未闭合轮廓的路径图元。
    @abstractmethod
    def getInternalDraftItem(self) -> T_DraftItem | None: ...

    # 返回当前正在拖动的顶点控件。
    @abstractmethod
    def getInternalDraggingHandle(self) -> T_Handle | None: ...

    # 返回当前添加或擦除操作。
    @abstractmethod
    def getInternalOperation(self) -> str: ...

    # 返回画布中当前图像的有效矩形。
    @abstractmethod
    def getInternalImageRect(self) -> T_Rect: ...

    # 返回画布是否尚未完成首次图像适配。
    @abstractmethod
    def getInternalFirstImage(self) -> bool: ...

    # 返回缩放是否继续自动适应窗口。
    @abstractmethod
    def getInternalAutoFit(self) -> bool: ...

    # 返回是否处于禁止编辑的观察状态。
    @abstractmethod
    def getReadOnly(self) -> bool: ...

    # 返回当前截面中的十字星坐标。
    @abstractmethod
    def getInternalCrosshairPosition(self) -> T_Point | None: ...

    # 返回十字星及两条参考线的颜色。
    @abstractmethod
    def getInternalCrosshairColors(self) -> tuple[str, str, str]: ...

    # 提供草稿闭合信号，交由项目层接收和保存轮廓。
    @abstractmethod
    def getPolygonFinished(self) -> T_Signal: ...

    # 提供顶点编辑完成信号，载荷使用只读坐标快照。
    @abstractmethod
    def getPolygonChanged(self) -> T_Signal: ...

    # 取得显示插值或外置掩码的图元；尚未就绪时抛出明确错误。
    @final
    def requireInternalInterpolationItem(self) -> T_PixmapItem:
        value = self.getInternalInterpolationItem()
        if value is None:
            raise RuntimeError("数据尚未就绪 / Data is not available")
        return value

    # 返回尚未闭合的草稿顶点数量。
    @abstractmethod
    def getDraftPointCount(self) -> int: ...

    # 按索引返回草稿点副本，防止外部修改画布坐标。
    @abstractmethod
    def getDraftPoint(self, index: int) -> T_Point: ...

    # 返回当前显示的轮廓图元数量。
    @abstractmethod
    def getPolygonItemCount(self) -> int: ...

    # 按索引查询轮廓图元，不暴露图元列表。
    @abstractmethod
    def getPolygonItem(self, index: int) -> T_PolygonItem: ...

    # 返回当前显示的多边形顶点控件数量。
    @abstractmethod
    def getHandleCount(self) -> int: ...

    # 按索引取得顶点控件，不暴露控件存储列表。
    @abstractmethod
    def getHandle(self, index: int) -> T_Handle: ...

    # 查询指定轮廓的顶点数量。
    @abstractmethod
    def getPolygonPointCount(self, polygon_index: int) -> int: ...

    # 按轮廓和顶点索引返回坐标副本，避免外部篡改画布几何。
    @abstractmethod
    def getPolygonPoint(self, polygon_index: int, vertex_index: int) -> T_Point: ...

    # 提供只读定位信号，供三个截面更新共享交点。
    @abstractmethod
    def getPositionClicked(self) -> T_Signal: ...

    # 取得未闭合轮廓的路径图元；尚未就绪时抛出明确错误。
    @final
    def requireInternalDraftItem(self) -> T_DraftItem:
        value = self.getInternalDraftItem()
        if value is None:
            raise RuntimeError("数据尚未就绪 / Data is not available")
        return value

    # 取得当前正在拖动的顶点控件；尚未就绪时抛出明确错误。
    @final
    def requireInternalDraggingHandle(self) -> T_Handle:
        value = self.getInternalDraggingHandle()
        if value is None:
            raise RuntimeError("数据尚未就绪 / Data is not available")
        return value

    # 取得当前截面中的十字星坐标；尚未就绪时抛出明确错误。
    @final
    def requireInternalCrosshairPosition(self) -> T_Point:
        value = self.getInternalCrosshairPosition()
        if value is None:
            raise RuntimeError("数据尚未就绪 / Data is not available")
        return value
