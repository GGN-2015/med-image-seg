from __future__ import annotations

from typing import final

from ....Abstract.Algorithms.Observation.I_AxisColors import I_AxisColors


# 按 L、P、S 轴提供参考线颜色，统一三个截面的轴向标识。
@final
class C_AxisColors(I_AxisColors):
    # 返回标识 L 固定轴的品红参考线颜色。
    def getL(self) -> str:
        return "#ff00ff"

    # 返回标识 P 固定轴的黄色参考线颜色。
    def getP(self) -> str:
        return "#ffff00"

    # 返回标识 S 固定轴的青色参考线颜色。
    def getS(self) -> str:
        return "#00ffff"
