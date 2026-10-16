from __future__ import annotations

from types import TracebackType
from typing import IO, final

from ....Abstract.Storage.Resources.T_FileStream import T_FileStream


# 把原生二进制流适配为文件流接口，集中管理读取、写入和关闭。
@final
class C_BinaryFileStream(T_FileStream[bytes]):
    # 保存原生二进制流，由上下文管理其生命周期。
    def __init__(self, stream: IO[bytes]) -> None:
        self._stream = stream

    # 从当前位置读取字节，负长度表示读到文件结束。
    def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)

    # 写入二进制数据并返回写入的字节数。
    def write(self, data: bytes) -> int:
        return self._stream.write(data)

    # 将流缓冲区刷新到底层文件，供后续同步与原子替换使用。
    def flush(self) -> None:
        self._stream.flush()

    # 返回底层文件描述符，供保存流程执行系统级同步。
    def fileno(self) -> int:
        return self._stream.fileno()

    # 关闭底层文件流并释放文件句柄。
    def close(self) -> None:
        self._stream.close()

    # 进入资源上下文，提供受管理的流或临时目录。
    def __enter__(self) -> T_FileStream[bytes]:
        return self

    # 离开上下文时释放流或临时目录，即使操作中途发生异常。
    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
