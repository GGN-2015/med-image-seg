from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from .T_Task import T_Task

T_Result = TypeVar("T_Result")


# 约定任务执行与结果交付，不让业务任务依赖线程或事件循环框架。
class T_TaskRunner(ABC, Generic[T_Result]):
    # 等待任务真正结束后返回原类型结果，失败时保留原异常。
    @abstractmethod
    def run(self, task: T_Task[T_Result]) -> T_Result: ...
