from typing import TypeVar, cast, final

from PySide6.QtCore import QThread

from ....Abstract.Application.Tasks.T_Task import T_Task
from ....Abstract.Presentation.Tasks.T_BackgroundTaskThread import (
    T_BackgroundTaskThread,
)
from ..Metaclasses.C_Qt_AbcMeta import C_Qt_AbcMeta

T_Result = TypeVar("T_Result")


# 仅运行纯数据任务并保留 Python 结果与异常，不在后台操作任何 Qt 控件。
@final
class C_Qt_BackgroundTaskThread(
    QThread,
    T_BackgroundTaskThread[QThread, T_Result],
    metaclass=C_Qt_AbcMeta,
):
    # 初始化尚未完成的结果槽，允许任务的合法返回值本身就是 None。
    def __init__(self, task: T_Task[T_Result]) -> None:
        super().__init__()
        self._task = task
        self._result: T_Result | None = None
        self._error: BaseException | None = None
        self._completed = False

    # 捕获任务的结束状态，由等待线程统一处理成功和异常。
    def run(self) -> None:
        try:
            self._result = self._task.execute()
        except BaseException as error:
            self._error = error
        finally:
            self._completed = True

    # 保留框架宿主，供运行器连接结束信号和回收线程。
    def getHost(self) -> QThread:
        return self

    # 先检查完成与异常，再把受任务契约保证的结果交回调用方。
    def getResult(self) -> T_Result:
        if not self._completed:
            raise RuntimeError("任务尚未结束 / Task has not finished")
        if self._error is not None:
            raise self._error
        return cast(T_Result, self._result)
