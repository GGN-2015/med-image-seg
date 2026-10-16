from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Domain.Annotations.I_MutableAnnotationProject import (
        I_MutableAnnotationProject,
    )
from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray


# 在关键层之间插值有符号距离场，保留强制空层和边界层语义。
class I_InterpolationAlgorithm(ABC):
    # 查询当前层两侧的插值关键层，遇到显式状态时不跨越其边界。
    @abstractmethod
    def interpolation_bounds(
        self, context: I_MutableAnnotationProject, slice_index: int
    ) -> tuple[int, int] | None: ...

    # 在相邻关键层距离场之间插值，显式标注或边界层不使用自动结果。
    @abstractmethod
    def interpolated_plane(
        self, context: I_MutableAnnotationProject, slice_index: int
    ) -> NDArray[np.bool_] | None: ...

    # 计算各层是否实际含前景，保留强制空层造成的间断并避免分配完整体积。
    @abstractmethod
    def mask_presence(
        self, context: I_MutableAnnotationProject, *, interpolate: bool = True
    ) -> NDArray[np.bool_]: ...

    # 生成 LPS 三维二值掩码，按参数选择是否填入关键层之间的插值。
    @abstractmethod
    def to_mask(
        self, context: I_MutableAnnotationProject, *, interpolate: bool = True
    ) -> NDArray[np.uint8]: ...
