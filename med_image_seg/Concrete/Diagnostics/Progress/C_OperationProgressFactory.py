from __future__ import annotations

from typing import final

from ....Abstract.Diagnostics.Progress.I_MutableOperationProgress import (
    I_MutableOperationProgress,
)
from ....Abstract.Diagnostics.Progress.I_OperationProgressFactory import (
    I_OperationProgressFactory,
)
from ....Abstract.Diagnostics.Timing.I_Clock import I_Clock
from ....Abstract.Diagnostics.Timing.I_MutableDurationHistory import (
    I_MutableDurationHistory,
)


# 装配每次操作自己的计时与 S 曲线，历史文件只用于跨任务校准。
@final
class C_OperationProgressFactory(I_OperationProgressFactory):
    # 允许注入时钟和历史服务，便于测试及调整 profiling 存储位置。
    def __init__(
        self,
        clock: I_Clock | None = None,
        history: I_MutableDurationHistory | None = None,
    ) -> None:
        from ..Timing.C_DurationHistory import C_DurationHistory
        from ..Timing.C_MonotonicClock import C_MonotonicClock

        self._clock = clock if clock is not None else C_MonotonicClock()
        self._history = history if history is not None else C_DurationHistory()

    # 用同类历史成功耗时配置预估器，再启动独立计时会话。
    def start(
        self, operation: str, default_seconds: float = 10.0
    ) -> I_MutableOperationProgress:
        from .C_FakeProcessEstimation import C_FakeProcessEstimation
        from .C_OperationProgress import C_OperationProgress

        expected = self._history.getExpectedSeconds(operation, default_seconds)
        return C_OperationProgress(
            operation,
            expected,
            self._clock,
            C_FakeProcessEstimation(expected),
            self._history,
        )
