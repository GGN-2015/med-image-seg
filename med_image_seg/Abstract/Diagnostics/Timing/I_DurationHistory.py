from abc import ABC, abstractmethod

from ...Storage.Paths.I_FilePath import I_FilePath


# 保存各类操作的耗时样本，供进度预估复用，不接触影像或标注数据。
class I_DurationHistory(ABC):
    # 返回历史文件的位置，便于用户查看 profiling 结果。
    @abstractmethod
    def getPath(self) -> I_FilePath: ...

    # 从同类成功样本估计耗时；没有可用历史时使用调用方的初始值。
    @abstractmethod
    def getExpectedSeconds(self, operation: str, default_seconds: float) -> float: ...
