from __future__ import annotations

from tempfile import TemporaryDirectory
from types import TracebackType
from typing import final

from ....Abstract.Storage.Resources.I_TemporaryDirectory import I_TemporaryDirectory


# 管理临时目录的上下文生命周期，离开作用域时清理暂存文件。
@final
class C_TemporaryDirectory(I_TemporaryDirectory):
    # 接管原生临时目录资源，使调用方通过接口管理清理。
    def __init__(self, resource: TemporaryDirectory[str]) -> None:
        self._resource = resource

    # 进入资源上下文，提供受管理的流或临时目录。
    def __enter__(self) -> str:
        return self._resource.__enter__()

    # 离开上下文时释放流或临时目录，即使操作中途发生异常。
    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._resource.__exit__(kind, error, traceback)
