from typing import TypeVar, final

from PySide6.QtCore import QEventLoop, Qt, QThread
from PySide6.QtWidgets import QApplication

from ....Abstract.Application.Tasks.T_Task import T_Task
from ....Abstract.Application.Tasks.T_TaskRunner import T_TaskRunner

T_Result = TypeVar("T_Result")


# 等待后台结果时保留 Qt 绘制和定时事件，同时排除用户输入及异步行为漂移。
@final
class C_Qt_BackgroundTaskRunner(T_TaskRunner[T_Result]):
    # 用局部事件循环保持同步调用语义，真正结束后才返回结果或抛出原异常。
    def run(self, task: T_Task[T_Result]) -> T_Result:
        from .C_Qt_BackgroundTaskThread import C_Qt_BackgroundTaskThread

        application = QApplication.instance()
        if application is None or QThread.currentThread() != application.thread():
            raise RuntimeError(
                "后台任务必须由界面线程启动 / Tasks must be started on the GUI thread"
            )
        loop = QEventLoop()
        thread = C_Qt_BackgroundTaskThread(task)
        thread.getHost().finished.connect(loop.quit, Qt.ConnectionType.QueuedConnection)
        try:
            thread.getHost().start()
            loop.exec(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
            thread.getHost().wait()
            return thread.getResult()
        finally:
            thread.getHost().wait()
            thread.getHost().deleteLater()
