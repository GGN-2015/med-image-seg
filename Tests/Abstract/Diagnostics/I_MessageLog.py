from abc import ABC, abstractmethod


# 收集测试中的提示文本，用于断言消息内容而不弹出阻塞对话框。
class I_MessageLog(ABC):
    # 返回已记录的提示消息数量。
    @abstractmethod
    def getCount(self) -> int: ...

    # 按索引查询测试期间记录的提示文本。
    @abstractmethod
    def getMessage(self, index: int) -> str: ...
