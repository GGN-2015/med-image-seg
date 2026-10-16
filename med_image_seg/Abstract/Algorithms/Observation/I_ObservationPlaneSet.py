from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import final

from ...Domain.Imaging.I_ObservationPlane import I_ObservationPlane


# 以具名只读接口提供三个截面，避免依赖固定字符串键的字典。
class I_ObservationPlaneSet(ABC):
    # 取得固定 S 轴的 LP 截面，沿用青色截面标识。
    @abstractmethod
    def getLP(self) -> I_ObservationPlane: ...

    # 取得固定 L 轴的 PS 截面，沿用品红截面标识。
    @abstractmethod
    def getPS(self) -> I_ObservationPlane: ...

    # 取得固定 P 轴的 SL 截面，沿用黄色截面标识。
    @abstractmethod
    def getSL(self) -> I_ObservationPlane: ...

    # 按 LP、PS、SL 名称查询截面，未知名称报错。
    @final
    def getByName(self, name: str) -> I_ObservationPlane:
        if name == "LP":
            return self.getLP()
        if name == "PS":
            return self.getPS()
        if name == "SL":
            return self.getSL()
        raise KeyError(name)

    # 依次查询集合元素，保留原有顺序且不暴露存储容器。
    @final
    def __iter__(self) -> Iterator[str]:
        return iter(("LP", "PS", "SL"))

    # 按既定顺序迭代截面名称和截面接口，不返回固定键字典。
    @final
    def getItems(self) -> Iterator[tuple[str, I_ObservationPlane]]:
        return iter((("LP", self.getLP()), ("PS", self.getPS()), ("SL", self.getSL())))
