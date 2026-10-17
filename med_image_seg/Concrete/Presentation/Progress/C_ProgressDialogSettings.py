from typing import final

from ....Abstract.Presentation.Progress.I_ProgressDialogSettings import (
    I_ProgressDialogSettings,
)


# 保存一次耗时流程的只读进度配置，不引入 Qt 或耗时估计库。
@final
class C_ProgressDialogSettings(I_ProgressDialogSettings):
    # 接收操作类别、标题键和初值，避免界面锁定服务硬编码每种导出格式。
    def __init__(self, operation: str, title_key: str, default_seconds: float) -> None:
        self._operation = operation
        self._title_key = title_key
        self._default_seconds = default_seconds

    # 返回用于隔离耗时历史的操作类别。
    def getOperation(self) -> str:
        return self._operation

    # 返回交给应用翻译服务处理的标题键。
    def getTitleKey(self) -> str:
        return self._title_key

    # 返回无历史样本时使用的预期时长。
    def getDefaultSeconds(self) -> float:
        return self._default_seconds
