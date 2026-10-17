from abc import ABC, abstractmethod


# 约定进度窗口所需的操作身份和显示配置，供不同耗时流程复用同一界面锁。
class I_ProgressDialogSettings(ABC):
    # 返回独立的操作类别，避免混用闭合、NIfTI 和 UBD 的历史耗时。
    @abstractmethod
    def getOperation(self) -> str: ...

    # 返回标题的翻译键，让具体界面按当前语言生成文本。
    @abstractmethod
    def getTitleKey(self) -> str: ...

    # 返回尚无历史时的初始估计秒数，不代表任务的完成期限。
    @abstractmethod
    def getDefaultSeconds(self) -> float: ...
