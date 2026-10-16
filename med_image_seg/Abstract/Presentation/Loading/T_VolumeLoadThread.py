from __future__ import annotations

from typing import TYPE_CHECKING

from ..Window.T_HostedObject import T_HostedObject

if TYPE_CHECKING:
    from ...Domain.Imaging.I_ImageSource import I_ImageSource
from abc import abstractmethod
from typing import Generic, TypeVar

T_Host = TypeVar("T_Host", covariant=True)
T_Signal = TypeVar("T_Signal")


# 在后台读取与重采样影像，通过信号把结果交回主线程。
class T_VolumeLoadThread(T_HostedObject[T_Host], Generic[T_Host, T_Signal]):
    # 返回当前处理的影像来源。
    @abstractmethod
    def getSource(self) -> I_ImageSource: ...

    # 返回 LPS 网格间距，单位为毫米。
    @abstractmethod
    def getSpacingMm(self) -> float: ...

    # 在线程中读取影像，通过成功或失败信号把结果交回主线程。
    @abstractmethod
    def run(self) -> None: ...

    # 提供后台读取成功信号，用于把数据交回主线程。
    @abstractmethod
    def getLoaded(self) -> T_Signal: ...

    # 提供后台读取失败信号，由主线程处理错误提示和状态恢复。
    @abstractmethod
    def getFailed(self) -> T_Signal: ...
