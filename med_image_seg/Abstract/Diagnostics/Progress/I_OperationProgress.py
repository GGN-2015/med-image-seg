from abc import ABC, abstractmethod


# 提供单次操作的只读计时和进度快照，不允许界面直接更改计时状态。
class I_OperationProgress(ABC):
    # 返回不包含影像路径的操作类别，供统计同类任务耗时。
    @abstractmethod
    def getOperation(self) -> str: ...

    # 返回实际经过的秒数，操作结束后保持最终值。
    @abstractmethod
    def getElapsedSeconds(self) -> float: ...

    # 返回本次启动时根据历史确定的预期耗时。
    @abstractmethod
    def getExpectedSeconds(self) -> float: ...

    # 返回不回退的百分比，只有成功结束的操作能够到达 100。
    @abstractmethod
    def getPercent(self) -> int: ...

    # 返回操作是否已经结束，便于停止界面的周期刷新。
    @abstractmethod
    def getFinished(self) -> bool: ...

    # 返回结束结果；尚未结束时使用空值，而不是把运行中误判为失败。
    @abstractmethod
    def getSucceeded(self) -> bool | None: ...
