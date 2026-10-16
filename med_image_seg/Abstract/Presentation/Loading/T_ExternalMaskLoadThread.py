from __future__ import annotations

from typing import TYPE_CHECKING

from ..Window.T_HostedObject import T_HostedObject

if TYPE_CHECKING:
    from ...Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from ...Storage.Paths.I_FilePath import I_FilePath
from abc import abstractmethod
from typing import Generic, TypeVar

T_Host = TypeVar("T_Host", covariant=True)
T_Signal = TypeVar("T_Signal")


# 在后台读取外置掩码，通过信号返回结果和错误以免阻塞界面。
class T_ExternalMaskLoadThread(T_HostedObject[T_Host], Generic[T_Host, T_Signal]):
    # 返回影像输入路径。
    @abstractmethod
    def getPath(self) -> I_FilePath: ...

    # 返回外置掩码需要对齐的参考影像。
    @abstractmethod
    def getReference(self) -> I_MedicalVolume: ...

    # 在线程中读取并对齐外置掩码，通过信号返回结果或错误。
    @abstractmethod
    def run(self) -> None: ...

    # 提供后台读取成功信号，用于把数据交回主线程。
    @abstractmethod
    def getLoaded(self) -> T_Signal: ...

    # 提供后台读取失败信号，由主线程处理错误提示和状态恢复。
    @abstractmethod
    def getFailed(self) -> T_Signal: ...
