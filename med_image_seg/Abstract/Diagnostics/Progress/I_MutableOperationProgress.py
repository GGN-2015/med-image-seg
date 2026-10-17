from __future__ import annotations

from abc import abstractmethod
from types import TracebackType
from typing import final

from .I_OperationProgress import I_OperationProgress


# 在只读进度契约上增加结束操作，并以共享上下文逻辑记录成功或异常耗时。
class I_MutableOperationProgress(I_OperationProgress):
    # 固定最终耗时并记录一次结果，重复结束不会产生重复样本。
    @abstractmethod
    def finish(self, success: bool = True) -> None: ...

    # 返回当前计时会话，允许同步操作使用 with 自动记录耗时。
    @final
    def __enter__(self) -> I_MutableOperationProgress:
        return self

    # 根据有无异常结束计时，不吞掉原操作的异常。
    @final
    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.finish(exception_type is None)
