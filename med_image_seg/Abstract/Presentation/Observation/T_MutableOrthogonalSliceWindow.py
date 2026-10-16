from __future__ import annotations

from typing import TYPE_CHECKING

from .T_OrthogonalSliceWindow import T_OrthogonalSliceWindow

if TYPE_CHECKING:
    from ...Domain.Imaging.I_ObservationPlane import I_ObservationPlane
from abc import abstractmethod
from typing import TypeVar

T_Canvas = TypeVar("T_Canvas")
T_Host = TypeVar("T_Host", covariant=True)
T_Label = TypeVar("T_Label")
T_Signal = TypeVar("T_Signal")
T_Spin = TypeVar("T_Spin")


# 在只读截面窗口查询上增加切片、标题和显示内容的更新入口。
class T_MutableOrthogonalSliceWindow(
    T_OrthogonalSliceWindow[T_Host, T_Label, T_Canvas, T_Spin, T_Signal]
):
    # 记录当前窗口的截面定义。
    @abstractmethod
    def setPlane(self, value: I_ObservationPlane) -> None: ...

    # 记录截面轴向标签。
    @abstractmethod
    def setAxesLabel(self, value: T_Label) -> None: ...

    # 记录切片画布。
    @abstractmethod
    def setCanvas(self, value: T_Canvas) -> None: ...

    # 记录当前切片编号标签。
    @abstractmethod
    def setSliceLabel(self, value: T_Label) -> None: ...

    # 记录当前切片编号输入框。
    @abstractmethod
    def setSliceSpin(self, value: T_Spin) -> None: ...
