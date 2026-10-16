from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Algorithms.Observation.I_AxisColors import I_AxisColors
from ....Abstract.Algorithms.Observation.I_ObservationPlanes import I_ObservationPlanes
from ....Abstract.Algorithms.Observation.I_ObservationPlaneSet import (
    I_ObservationPlaneSet,
)

if TYPE_CHECKING:
    pass
from typing import final


# 定义 LP、PS、SL 的轴顺序和颜色，供截面提取与十字线联动共用。
@final
class C_ObservationPlanes(I_ObservationPlanes):
    # 通过具名接口取得 LP、PS、SL 定义，不依赖固定键字典。
    def getPlanes(self) -> I_ObservationPlaneSet:
        from ...Domain.Imaging.C_ObservationPlane import C_ObservationPlane
        from .C_ObservationPlaneSet import C_ObservationPlaneSet

        return C_ObservationPlaneSet(
            C_ObservationPlane("LP", 0, 1, 2, "#00ffff"),
            C_ObservationPlane("PS", 1, 2, 0, "#ff00ff"),
            C_ObservationPlane("SL", 2, 0, 1, "#ffff00"),
        )

    # 按 L、P、S 轴取得三个视图共用的参考线配色。
    def getAxisColors(self) -> I_AxisColors:
        from .C_AxisColors import C_AxisColors

        return C_AxisColors()
