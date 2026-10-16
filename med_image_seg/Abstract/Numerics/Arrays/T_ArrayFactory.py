from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

import numpy as np
from numpy.typing import NDArray

T_DataType = TypeVar("T_DataType")


# 包装底层数组数据，用泛型保留输入类型而不退化为 Any。
class T_ArrayFactory(ABC, Generic[T_DataType]):
    # 把输入转换为 NumPy 数组，保留已知元素类型。
    @abstractmethod
    def wrap(self, data: T_DataType) -> NDArray[np.generic]: ...
