from __future__ import annotations

from typing import final

from ....Abstract.Algorithms.Observation.I_ObservationPlaneSet import (
    I_ObservationPlaneSet,
)
from ....Abstract.Domain.Imaging.I_ObservationPlane import I_ObservationPlane


# 以具名只读接口提供三个截面，避免依赖固定字符串键的字典。
@final
class C_ObservationPlaneSet(I_ObservationPlaneSet):
    # 分别保存 LP、PS、SL 截面，提供固定的具名查询。
    def __init__(
        self, lp: I_ObservationPlane, ps: I_ObservationPlane, sl: I_ObservationPlane
    ) -> None:
        self._lp = lp
        self._ps = ps
        self._sl = sl

    # 取得固定 S 轴的 LP 截面，沿用青色截面标识。
    def getLP(self) -> I_ObservationPlane:
        return self._lp

    # 取得固定 L 轴的 PS 截面，沿用品红截面标识。
    def getPS(self) -> I_ObservationPlane:
        return self._ps

    # 取得固定 P 轴的 SL 截面，沿用黄色截面标识。
    def getSL(self) -> I_ObservationPlane:
        return self._sl
