from __future__ import annotations

from typing import TYPE_CHECKING

from .I_AxisColors import I_AxisColors
from .I_ObservationPlaneSet import I_ObservationPlaneSet

if TYPE_CHECKING:
    pass
from abc import ABC, abstractmethod


# 定义 LP、PS、SL 的轴顺序和颜色，供截面提取与十字线联动共用。
class I_ObservationPlanes(ABC):
    # 通过具名接口取得 LP、PS、SL 定义，不依赖固定键字典。
    @abstractmethod
    def getPlanes(self) -> I_ObservationPlaneSet: ...

    # 按 L、P、S 轴取得三个视图共用的参考线配色。
    @abstractmethod
    def getAxisColors(self) -> I_AxisColors: ...
