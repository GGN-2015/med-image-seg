from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar, final

import numpy as np
from numpy.typing import NDArray

from ....Abstract.Domain.Imaging.I_ObservationPlane import I_ObservationPlane
from ....Abstract.Domain.Records.I_RecordFieldList import I_RecordFieldList

T_Element = TypeVar("T_Element", bound=np.generic)


# 描述截面的固定轴、显示轴和颜色，使坐标转换不依赖窗口控件。
@final
@dataclass(slots=True, frozen=True, init=False)
class C_ObservationPlane(I_ObservationPlane):
    _state_name: str
    _state_horizontal_axis: int
    _state_vertical_axis: int
    _state_fixed_axis: int
    _state_color: str

    # 保存固定轴、显示轴和颜色，用于三个截面的坐标转换。
    def __init__(
        self,
        name: str,
        horizontal_axis: int,
        vertical_axis: int,
        fixed_axis: int,
        color: str,
    ) -> None:
        object.__setattr__(self, "_state_name", name)
        object.__setattr__(self, "_state_horizontal_axis", horizontal_axis)
        object.__setattr__(self, "_state_vertical_axis", vertical_axis)
        object.__setattr__(self, "_state_fixed_axis", fixed_axis)
        object.__setattr__(self, "_state_color", color)

    # 返回 LP、PS 或 SL 截面名称。
    def getName(self) -> str:
        return self._state_name

    # 返回截面水平方向对应的体素轴。
    def getHorizontalAxis(self) -> int:
        return self._state_horizontal_axis

    # 返回截面垂直方向对应的体素轴。
    def getVerticalAxis(self) -> int:
        return self._state_vertical_axis

    # 返回截面保持不变的体素轴编号。
    def getFixedAxis(self) -> int:
        return self._state_fixed_axis

    # 返回当前截面的十字星颜色，其他视图以同色参考线标识它。
    def getColor(self) -> str:
        return self._state_color

    # 返回有序的记录字段名，供序列化读取。
    def getRecordFields(self) -> I_RecordFieldList:
        from ..Records.C_RecordFieldList import C_RecordFieldList

        return C_RecordFieldList(
            ("name", "horizontal_axis", "vertical_axis", "fixed_axis", "color")
        )

    # 按截面的固定轴提取数组，并排列为对应的水平和垂直显示方向。
    def section(
        self, data: NDArray[T_Element], position: tuple[int, int, int]
    ) -> NDArray[T_Element]:
        from ...Numerics.Arrays.C_ArrayFactory import C_ArrayFactory

        selection: list[slice | int] = [slice(None), slice(None), slice(None)]
        selection[self.getFixedAxis()] = position[self.getFixedAxis()]
        section = data[tuple(selection)]
        remaining_axes = [axis for axis in range(3) if axis != self.getFixedAxis()]
        if remaining_axes == [self.getVerticalAxis(), self.getHorizontalAxis()]:
            return C_ArrayFactory().wrap(section)
        return C_ArrayFactory().wrap(section.T)

    # 把截面点击映射到共享体素交点，并将坐标限制在影像范围内。
    def position_at(
        self,
        position: tuple[int, int, int],
        horizontal: float,
        vertical: float,
        shape: tuple[int, int, int],
    ) -> tuple[int, int, int]:
        updated = list(position)
        for axis, coordinate in (
            (self.getHorizontalAxis(), horizontal),
            (self.getVerticalAxis(), vertical),
        ):
            updated[axis] = int(np.clip(np.floor(coordinate), 0, shape[axis] - 1))
        return (updated[0], updated[1], updated[2])
