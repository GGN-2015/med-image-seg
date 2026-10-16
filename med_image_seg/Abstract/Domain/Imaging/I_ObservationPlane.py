from __future__ import annotations

from abc import abstractmethod
from typing import TypeVar

import numpy as np
from numpy.typing import NDArray

from ..Annotations.I_Record import I_Record
from ..Records.I_RecordFieldList import I_RecordFieldList

T_Element = TypeVar("T_Element", bound=np.generic)


# 描述截面的固定轴、显示轴和颜色，使坐标转换不依赖窗口控件。
class I_ObservationPlane(I_Record):
    # 返回 LP、PS 或 SL 截面名称。
    @abstractmethod
    def getName(self) -> str: ...

    # 返回截面水平方向对应的体素轴。
    @abstractmethod
    def getHorizontalAxis(self) -> int: ...

    # 返回截面垂直方向对应的体素轴。
    @abstractmethod
    def getVerticalAxis(self) -> int: ...

    # 返回截面保持不变的体素轴编号。
    @abstractmethod
    def getFixedAxis(self) -> int: ...

    # 返回当前截面的十字星颜色，其他视图以同色参考线标识它。
    @abstractmethod
    def getColor(self) -> str: ...

    # 返回有序的记录字段名，供序列化读取。
    @abstractmethod
    def getRecordFields(self) -> I_RecordFieldList: ...

    # 按截面的固定轴提取数组，并排列为对应的水平和垂直显示方向。
    @abstractmethod
    def section(
        self, data: NDArray[T_Element], position: tuple[int, int, int]
    ) -> NDArray[T_Element]: ...

    # 把截面点击映射到共享体素交点，并将坐标限制在影像范围内。
    @abstractmethod
    def position_at(
        self,
        position: tuple[int, int, int],
        horizontal: float,
        vertical: float,
        shape: tuple[int, int, int],
    ) -> tuple[int, int, int]: ...
