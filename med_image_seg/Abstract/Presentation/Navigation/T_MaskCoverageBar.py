from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar

from ..Window.T_HostedObject import T_HostedObject

T_Host = TypeVar("T_Host", covariant=True)
T_Slider = TypeVar("T_Slider")


# 按滑块几何绘制掩码区间，保证绿色层位置与切片编号对齐且不可拖动。
class T_MaskCoverageBar(T_HostedObject[T_Host], Generic[T_Host, T_Slider]):
    # 返回区间条对齐所参照的切片滑块。
    @abstractmethod
    def getInternalSlider(self) -> T_Slider: ...

    # 返回逐层掩码存在性快照。
    @abstractmethod
    def getInternalPresence(self) -> tuple[bool, ...]: ...

    # 返回逐层前景存在性快照，保留分离区间和孤立层。
    @abstractmethod
    def getPresence(self) -> tuple[bool, ...]: ...

    # 使用原生滑块的槽和滑块宽度计算每层中心，保证区间条逐层对齐。
    @abstractmethod
    def slice_centers(self) -> tuple[int, ...]: ...
