from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from typing import TypeVar

from .T_MaskCoverageBar import T_MaskCoverageBar

T_Host = TypeVar("T_Host", covariant=True)
T_Slider = TypeVar("T_Slider")


# 在区间条查询上增加存在性快照和关联滑块的更新入口。
class T_MutableMaskCoverageBar(T_MaskCoverageBar[T_Host, T_Slider]):
    # 记录区间条对齐所参照的切片滑块。
    @abstractmethod
    def setInternalSlider(self, value: T_Slider) -> None: ...

    # 复制逐层存在性数据，防止外部容器变化影响区间绘制。
    @abstractmethod
    def setInternalPresence(self, value: tuple[bool, ...]) -> None: ...

    # 复制逐层掩码存在性数据并请求重绘区间条。
    @abstractmethod
    def set_presence(self, presence: Iterable[bool]) -> None: ...
