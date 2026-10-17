from time import perf_counter
from typing import final

from ....Abstract.Diagnostics.Timing.I_Clock import I_Clock


# 用高精度单调时钟测量操作耗时，不依赖会发生跳变的系统时间。
@final
class C_MonotonicClock(I_Clock):
    # 返回高精度计时读数，调用方只计算开始与结束之差。
    def getSeconds(self) -> float:
        return perf_counter()
