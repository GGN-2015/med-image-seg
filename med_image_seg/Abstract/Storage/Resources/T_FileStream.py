from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Generic, TypeVar

T_StreamData = TypeVar("T_StreamData", str, bytes)


# 约定文本或二进制流的读写与资源释放，以泛型区分内容类型。
class T_FileStream(ABC, Generic[T_StreamData]):
    # 从当前位置读取指定长度的文本或字节，负值表示读取剩余内容。
    @abstractmethod
    def read(self, size: int = -1) -> T_StreamData: ...

    # 写入与当前流内容类型一致的数据，并返回写入长度。
    @abstractmethod
    def write(self, data: T_StreamData) -> int: ...

    # 将流缓冲区刷新到底层文件，供后续同步与原子替换使用。
    @abstractmethod
    def flush(self) -> None: ...

    # 返回底层文件描述符，供保存流程执行系统级同步。
    @abstractmethod
    def fileno(self) -> int: ...

    # 关闭底层文件流并释放文件句柄。
    @abstractmethod
    def close(self) -> None: ...

    # 进入资源上下文，提供受管理的流或临时目录。
    @abstractmethod
    def __enter__(self) -> T_FileStream[T_StreamData]: ...

    # 离开上下文时释放流或临时目录，即使操作中途发生异常。
    @abstractmethod
    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...
