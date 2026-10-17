from abc import abstractmethod

from .I_DurationHistory import I_DurationHistory


# 在只读耗时历史上增加样本写入，使读取统计与修改历史具有不同的能力边界。
class I_MutableDurationHistory(I_DurationHistory):
    # 记录真实耗时与成功状态，失败样本用于诊断但不参与耗时预测。
    @abstractmethod
    def record(self, operation: str, elapsed_seconds: float, success: bool) -> None: ...
