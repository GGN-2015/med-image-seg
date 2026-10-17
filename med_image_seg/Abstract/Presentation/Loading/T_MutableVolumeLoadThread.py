from __future__ import annotations

from typing import TYPE_CHECKING

from .T_VolumeLoadThread import T_VolumeLoadThread

if TYPE_CHECKING:
    from ...Domain.Imaging.I_ImageSource import I_ImageSource
from abc import abstractmethod
from typing import TypeVar

T_Host = TypeVar("T_Host", covariant=True)
T_Signal = TypeVar("T_Signal")


# 在影像后台任务查询上增加来源、网格间距和结果状态的配置。
class T_MutableVolumeLoadThread(T_VolumeLoadThread[T_Host, T_Signal]):
    # 记录后台任务需要读取的影像源。
    @abstractmethod
    def setSource(self, value: I_ImageSource) -> None: ...

    # 记录LPS 网格间距，单位为毫米。
    @abstractmethod
    def setSpacingMm(self, value: float) -> None: ...

    # 记录加载时需要匹配的标注文件编号。
    @abstractmethod
    def setAnnotationIndex(self, value: int) -> None: ...
