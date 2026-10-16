from __future__ import annotations

from abc import ABC, abstractmethod
from typing import final


# 按 L、P、S 轴提供参考线颜色，统一三个截面的轴向标识。
class I_AxisColors(ABC):
    # 返回标识 L 固定轴的品红参考线颜色。
    @abstractmethod
    def getL(self) -> str: ...

    # 返回标识 P 固定轴的黄色参考线颜色。
    @abstractmethod
    def getP(self) -> str: ...

    # 返回标识 S 固定轴的青色参考线颜色。
    @abstractmethod
    def getS(self) -> str: ...

    # 按体素轴编号取得参考线颜色，拒绝无效轴编号。
    @final
    def getByAxis(self, axis: int) -> str:
        if axis == 0:
            return self.getL()
        if axis == 1:
            return self.getP()
        if axis == 2:
            return self.getS()
        raise KeyError(axis)
