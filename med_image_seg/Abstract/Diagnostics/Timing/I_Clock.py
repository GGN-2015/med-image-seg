from abc import ABC, abstractmethod


# 提供单调时间读数，使操作计时不受系统校时影响，也便于确定性测试。
class I_Clock(ABC):
    # 返回只用于计算时间差的秒数，不将其解释为日历时间。
    @abstractmethod
    def getSeconds(self) -> float: ...
