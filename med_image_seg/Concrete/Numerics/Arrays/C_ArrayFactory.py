from __future__ import annotations

from typing import TypeVar, final

import numpy as np
from numpy.typing import NDArray

from ....Abstract.Numerics.Arrays.T_ArrayFactory import T_ArrayFactory

T_Element = TypeVar("T_Element", bound=np.generic)


# 包装底层数组数据，用泛型保留输入类型而不退化为 Any。
@final
class C_ArrayFactory(T_ArrayFactory[NDArray[np.generic]]):
    # 把输入转换为 NumPy 数组，保留已知元素类型。
    def wrap(self, data: NDArray[T_Element]) -> NDArray[T_Element]:
        return np.asarray(data)
