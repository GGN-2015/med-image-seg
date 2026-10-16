from __future__ import annotations

from typing import TYPE_CHECKING

from ..Window.T_HostedObject import T_HostedObject

if TYPE_CHECKING:
    from ...Domain.Imaging.I_ObservationPlane import I_ObservationPlane
from abc import abstractmethod
from typing import Generic, TypeVar

T_Canvas = TypeVar("T_Canvas")
T_Host = TypeVar("T_Host", covariant=True)
T_Label = TypeVar("T_Label")
T_Signal = TypeVar("T_Signal")
T_Spin = TypeVar("T_Spin")


# 承载 PS 或 SL 只读截面，以不可关闭的非模态窗口参与三视图联动。
class T_OrthogonalSliceWindow(
    T_HostedObject[T_Host], Generic[T_Host, T_Label, T_Canvas, T_Spin, T_Signal]
):
    # 返回当前窗口的截面定义。
    @abstractmethod
    def getPlane(self) -> I_ObservationPlane: ...

    # 返回截面轴向标签。
    @abstractmethod
    def getAxesLabel(self) -> T_Label: ...

    # 返回切片画布。
    @abstractmethod
    def getCanvas(self) -> T_Canvas: ...

    # 返回当前切片编号标签。
    @abstractmethod
    def getSliceLabel(self) -> T_Label: ...

    # 返回当前切片编号输入框。
    @abstractmethod
    def getSliceSpin(self) -> T_Spin: ...
