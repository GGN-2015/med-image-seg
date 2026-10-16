from __future__ import annotations

from typing import final

from ...Abstract.Diagnostics.I_MutableMessageLog import I_MutableMessageLog


# 收集测试中的提示文本，用于断言消息内容而不弹出阻塞对话框。
@final
class C_MessageLog(I_MutableMessageLog):
    # 建立独立的提示消息存储，避免测试之间共享状态。
    def __init__(self) -> None:
        self._messages: list[str] = []

    # 返回已记录的提示消息数量。
    def getCount(self) -> int:
        return len(self._messages)

    # 按索引查询测试期间记录的提示文本。
    def getMessage(self, index: int) -> str:
        return self._messages[index]

    # 保存测试收到的提示文本，供断言代替模态弹窗。
    def record(self, message: str) -> None:
        self._messages.append(message)
