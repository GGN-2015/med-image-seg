from abc import abstractmethod

from .I_MessageLog import I_MessageLog


# 在只读消息查询上增加记录入口，供测试拦截提示而不共享全局状态。
class I_MutableMessageLog(I_MessageLog):
    # 保存测试收到的提示文本，供断言代替模态弹窗。
    @abstractmethod
    def record(self, message: str) -> None: ...
