from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T_Result = TypeVar("T_Result", covariant=True)


# 把不访问界面的数据操作封装为任务，让运行器决定其执行线程。
class T_Task(ABC, Generic[T_Result]):
    # 执行一次数据操作并返回明确类型的结果，异常由运行器转交调用方。
    @abstractmethod
    def execute(self) -> T_Result: ...
