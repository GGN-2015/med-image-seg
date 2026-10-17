from typing import final

from ....Abstract.Diagnostics.Progress.I_MutableOperationProgress import (
    I_MutableOperationProgress,
)
from ....Abstract.Diagnostics.Progress.I_ProgressEstimator import I_ProgressEstimator
from ....Abstract.Diagnostics.Timing.I_Clock import I_Clock
from ....Abstract.Diagnostics.Timing.I_MutableDurationHistory import (
    I_MutableDurationHistory,
)


# 跟踪单个操作的真实耗时和显示进度，结束时只写入一条 profiling 样本。
@final
class C_OperationProgress(I_MutableOperationProgress):
    # 保存独立的时钟、预估器和历史服务，不共享运行中的任务状态。
    def __init__(
        self,
        operation: str,
        expected_seconds: float,
        clock: I_Clock,
        estimator: I_ProgressEstimator,
        history: I_MutableDurationHistory,
    ) -> None:
        self._operation = operation
        self._expected_seconds = expected_seconds
        self._clock = clock
        self._estimator = estimator
        self._history = history
        self._started_at = clock.getSeconds()
        self._elapsed_seconds = 0.0
        self._percent = 0
        self._succeeded: bool | None = None

    # 返回无影像身份信息的操作类别。
    def getOperation(self) -> str:
        return self._operation

    # 运行时读取单调时钟，结束后返回固定的真实耗时。
    def getElapsedSeconds(self) -> float:
        if self.getFinished():
            return self._elapsed_seconds
        return max(0.0, self._clock.getSeconds() - self._started_at)

    # 返回本次会话使用的历史或初始预期耗时。
    def getExpectedSeconds(self) -> float:
        return self._expected_seconds

    # 运行中保持百分比单调且小于 100，完成后返回已经固定的最终值。
    def getPercent(self) -> int:
        if not self.getFinished():
            self._percent = max(
                self._percent,
                min(99, self._estimator.estimate(self.getElapsedSeconds())),
            )
        return self._percent

    # 判断是否已收到成功、失败或中止的结束事件。
    def getFinished(self) -> bool:
        return self._succeeded is not None

    # 返回结束结果，运行中不预先宣告成功或失败。
    def getSucceeded(self) -> bool | None:
        return self._succeeded

    # 只处理第一次结束事件，成功显示 100，失败保留结束前的估计值。
    def finish(self, success: bool = True) -> None:
        if self.getFinished():
            return
        self._elapsed_seconds = self.getElapsedSeconds()
        self.getPercent()
        self._succeeded = success
        if success:
            self._percent = 100
        self._history.record(self._operation, self._elapsed_seconds, success)
