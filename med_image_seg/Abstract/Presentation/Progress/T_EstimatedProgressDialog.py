from abc import abstractmethod
from typing import Generic, TypeVar

from ...Diagnostics.Progress.I_OperationProgress import I_OperationProgress
from ..Window.T_HostedObject import T_HostedObject

T_Host = TypeVar("T_Host", covariant=True)
T_CloseEvent = TypeVar("T_CloseEvent", contravariant=True)
T_KeyEvent = TypeVar("T_KeyEvent", contravariant=True)


# 约定进度窗口的展示和真实结束事件，不让业务接口依赖界面框架。
class T_EstimatedProgressDialog(
    T_HostedObject[T_Host], Generic[T_Host, T_CloseEvent, T_KeyEvent]
):
    # 返回只读进度会话，供诊断和测试查询实际耗时与预估百分比。
    @abstractmethod
    def getOperationProgress(self) -> I_OperationProgress: ...

    # 刷新估计值和耗时文本，不把预估到达上限视为任务完成。
    @abstractmethod
    def refresh(self) -> None: ...

    # 处理真正的成功事件，固定最终耗时并显示 100%。
    @abstractmethod
    def accept(self) -> None: ...

    # 处理真正的失败事件，记录失败耗时但不显示成功完成。
    @abstractmethod
    def reject(self) -> None: ...

    # 拒绝提前关闭运行中的任务；真正结束后才交给界面宿主关闭。
    @abstractmethod
    def closeEvent(self, event: T_CloseEvent) -> None: ...

    # 禁止用户以退出快捷键关闭仍在运行的不可取消任务。
    @abstractmethod
    def keyPressEvent(self, event: T_KeyEvent) -> None: ...
