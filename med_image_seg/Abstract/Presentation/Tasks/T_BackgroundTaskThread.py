from abc import abstractmethod
from typing import Generic, TypeVar

from ..Window.T_HostedObject import T_HostedObject

T_Host = TypeVar("T_Host", covariant=True)
T_Result = TypeVar("T_Result", covariant=True)


# 为框架线程约定任务执行与结果读取，接口不依赖具体线程库。
class T_BackgroundTaskThread(T_HostedObject[T_Host], Generic[T_Host, T_Result]):
    # 在线程内运行任务，保存结果或异常供调用线程领取。
    @abstractmethod
    def run(self) -> None: ...

    # 在线程结束后读取真实结果，若任务失败则重新抛出原异常。
    @abstractmethod
    def getResult(self) -> T_Result: ...
