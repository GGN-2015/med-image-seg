from abc import ABC, abstractmethod

from .I_MutableOperationProgress import I_MutableOperationProgress


# 装配时钟、历史和预估算法，使业务操作只依赖计时会话接口。
class I_OperationProgressFactory(ABC):
    # 启动独立会话，优先使用历史成功耗时而不是固定的初始估计。
    @abstractmethod
    def start(
        self, operation: str, default_seconds: float = 10.0
    ) -> I_MutableOperationProgress: ...
