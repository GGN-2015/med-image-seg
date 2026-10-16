from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType


# 管理临时目录的上下文生命周期，离开作用域时清理暂存文件。
class I_TemporaryDirectory(ABC):
    # 进入资源上下文，提供受管理的流或临时目录。
    @abstractmethod
    def __enter__(self) -> str: ...

    # 离开上下文时释放流或临时目录，即使操作中途发生异常。
    @abstractmethod
    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...
