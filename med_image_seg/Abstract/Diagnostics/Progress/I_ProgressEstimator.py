from abc import ABC, abstractmethod


# 只定义耗时到百分比的转换，将第三方预估算法限制在具体适配层。
class I_ProgressEstimator(ABC):
    # 返回 0 至 99 的估计百分比；100 留给操作的真实完成事件。
    @abstractmethod
    def estimate(self, elapsed_seconds: float) -> int: ...
