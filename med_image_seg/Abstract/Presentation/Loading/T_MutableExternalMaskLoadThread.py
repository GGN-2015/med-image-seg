from __future__ import annotations

from typing import TYPE_CHECKING

from .T_ExternalMaskLoadThread import T_ExternalMaskLoadThread

if TYPE_CHECKING:
    from ...Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from ...Storage.Paths.I_FilePath import I_FilePath
from abc import abstractmethod
from typing import TypeVar

T_Host = TypeVar("T_Host", covariant=True)
T_Signal = TypeVar("T_Signal")


# 在后台任务查询上增加路径、参考网格和结果状态的配置。
class T_MutableExternalMaskLoadThread(T_ExternalMaskLoadThread[T_Host, T_Signal]):
    # 记录影像输入路径。
    @abstractmethod
    def setPath(self, value: I_FilePath) -> None: ...

    # 记录外置掩码需要对齐的参考影像。
    @abstractmethod
    def setReference(self, value: I_MedicalVolume) -> None: ...
