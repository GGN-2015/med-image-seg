from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

from ...Domain.Geometry.I_PointList import I_PointList
from .T_SliceCanvas import T_SliceCanvas

if TYPE_CHECKING:
    from ...Domain.Annotations.I_PolygonAnnotation import I_PolygonAnnotation
    from ...Domain.Imaging.I_ObservationPlane import I_ObservationPlane
from abc import abstractmethod
from typing import TypeVar

T_Handle = TypeVar("T_Handle")
T_Host = TypeVar("T_Host", covariant=True)
T_PixmapItem = TypeVar("T_PixmapItem")
T_Point = TypeVar("T_Point")
T_PolygonItem = TypeVar("T_PolygonItem")
T_Rect = TypeVar("T_Rect")
T_Signal = TypeVar("T_Signal")
T_DraftItem = TypeVar("T_DraftItem")


# 在画布查询上增加图像显示与编辑操作，保留坐标集合的封装边界。
class T_MutableSliceCanvas(
    T_SliceCanvas[
        T_Host,
        T_Point,
        T_Rect,
        T_PixmapItem,
        T_DraftItem,
        T_PolygonItem,
        T_Handle,
        T_Signal,
    ]
):
    # 记录显示插值或外置掩码的图元。
    @abstractmethod
    def setInternalInterpolationItem(self, value: T_PixmapItem | None) -> None: ...

    # 记录未闭合轮廓的路径图元。
    @abstractmethod
    def setInternalDraftItem(self, value: T_DraftItem | None) -> None: ...

    # 记录当前正在拖动的顶点控件。
    @abstractmethod
    def setInternalDraggingHandle(self, value: T_Handle | None) -> None: ...

    # 记录当前添加或擦除操作。
    @abstractmethod
    def setInternalOperation(self, value: str) -> None: ...

    # 记录画布中当前图像的有效矩形。
    @abstractmethod
    def setInternalImageRect(self, value: T_Rect) -> None: ...

    # 记录画布是否尚未完成首次图像适配。
    @abstractmethod
    def setInternalFirstImage(self, value: bool) -> None: ...

    # 记录缩放是否继续自动适应窗口。
    @abstractmethod
    def setInternalAutoFit(self, value: bool) -> None: ...

    # 记录是否处于禁止编辑的观察状态。
    @abstractmethod
    def setReadOnly(self, value: bool) -> None: ...

    # 记录当前截面中的十字星坐标。
    @abstractmethod
    def setInternalCrosshairPosition(self, value: T_Point | None) -> None: ...

    # 记录十字星及两条参考线的颜色。
    @abstractmethod
    def setInternalCrosshairColors(self, value: tuple[str, str, str]) -> None: ...

    # 切换只读交互状态，清除拖动和草稿并更新顶点控件光标。
    @abstractmethod
    def set_read_only(self, read_only: bool) -> None: ...

    # 把共享体素交点投影到当前截面，并设置与其他截面一致的参考线颜色。
    @abstractmethod
    def set_crosshair(
        self, plane: I_ObservationPlane | None, position: tuple[int, int, int]
    ) -> None: ...

    # 切换添加或擦除操作，同时丢弃尚未闭合的草稿。
    @abstractmethod
    def set_operation(self, operation: str) -> None: ...

    # 替换图像、轮廓与遮罩，清空上一层图元并按需要适配视野。
    @abstractmethod
    def set_slice(
        self,
        image: NDArray[np.generic],
        polygons: Iterable[I_PolygonAnnotation],
        interpolated_mask: NDArray[np.generic] | None = None,
        *,
        overlay_color: tuple[int, int, int, int] = (49, 180, 255, 72),
    ) -> None: ...

    # 仅在可编辑且顶点足够时闭合草稿，通过信号提交轮廓快照。
    @abstractmethod
    def finish_polygon(self) -> None: ...

    # 丢弃尚未闭合的草稿并清除其路径图元，不影响已有轮廓。
    @abstractmethod
    def cancel_polygon(self) -> None: ...

    # 重建未闭合轮廓的路径图元，使鼠标绘制结果及时显示。
    @abstractmethod
    def _update_draft(self) -> None: ...

    # 复制只读顶点集合为画布草稿坐标，不接管调用方的可变存储。
    @abstractmethod
    def setDraftPoints(self, points: I_PointList) -> None: ...
