from __future__ import annotations

from enum import Enum, auto


# 用显式哨兵区分未传入的构造参数与实际业务值。
class E_DefaultValue(Enum):
    Unset = auto()
