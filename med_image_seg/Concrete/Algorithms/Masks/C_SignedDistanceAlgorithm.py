from __future__ import annotations

from typing import final

import numpy as np
from numpy.typing import NDArray
from scipy.ndimage import distance_transform_edt

from ....Abstract.Algorithms.Masks.I_SignedDistanceAlgorithm import (
    I_SignedDistanceAlgorithm,
)


# 把二值切片转换为有符号距离场，供关键层之间的插值使用。
@final
class C_SignedDistanceAlgorithm(I_SignedDistanceAlgorithm):
    # 计算二值切片的有符号距离场，为关键层之间的插值提供数值。
    def signed_distance(self, plane: NDArray[np.bool_]) -> NDArray[np.float32]:
        from ...Numerics.Arrays.C_ArrayFactory import C_ArrayFactory

        diagonal = float(np.hypot(*plane.shape))
        if not plane.any():
            return C_ArrayFactory().wrap(
                np.full(plane.shape, -diagonal, dtype=np.float32)
            )
        if plane.all():
            return C_ArrayFactory().wrap(
                np.full(plane.shape, diagonal, dtype=np.float32)
            )
        inside = np.asarray(distance_transform_edt(plane))
        outside = np.asarray(distance_transform_edt(~plane))
        return C_ArrayFactory().wrap(np.asarray(inside - outside, dtype=np.float32))
