from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypeVar, overload

from ....Abstract.Storage.Paths.I_FilePath import I_FilePath

if TYPE_CHECKING:
    from ....Abstract.Storage.Resources.I_FileStatus import I_FileStatus
    from ....Abstract.Storage.Resources.T_FileStream import T_FileStream
from collections.abc import Iterator
from pathlib import Path
from typing import final

T_ComparedValue = TypeVar("T_ComparedValue")


# 用路径接口封装文件系统操作，避免业务接口直接依赖 pathlib。
@final
class C_FilePath(I_FilePath):
    # 把路径文本或路径接口包装为本地文件系统路径。
    def __init__(self, value: str | I_FilePath | Path = ".") -> None:
        self._path = Path(value)

    # 提供文件系统路径文本，供原生文件接口调用。
    def __fspath__(self) -> str:
        return str(self._path)

    # 返回可显示和传给文件操作的路径文本。
    def __str__(self) -> str:
        return str(self._path)

    # 提供底层路径的调试表示。
    def __repr__(self) -> str:
        return repr(self._path)

    # 沿用底层路径的哈希，支持作为去重键。
    def __hash__(self) -> int:
        return hash(self._path)

    # 按底层路径比较相等性，使路径包装与路径接口保持一致。
    def __eq__(self: T_ComparedValue, other: T_ComparedValue) -> bool:
        from ....Abstract.Storage.Paths.I_FilePath import I_FilePath

        if not isinstance(self, I_FilePath):
            return False
        if isinstance(other, I_FilePath):
            return Path(self) == Path(other)
        return Path(self) == other

    # 拼接子路径并返回路径接口，不修改原路径。
    def __truediv__(self, other: str | I_FilePath) -> I_FilePath:
        return C_FilePath(self._path / other)

    # 沿用底层路径排序规则比较两个路径。
    def __lt__(self, other: I_FilePath) -> bool:
        return self._path < Path(other)

    # 返回文件名。
    def getName(self) -> str:
        return self._path.name

    # 返回去掉最后一个后缀的文件名。
    def getStem(self) -> str:
        return self._path.stem

    # 返回文件的最后一个后缀。
    def getSuffix(self) -> str:
        return self._path.suffix

    # 返回父目录路径。
    def getParent(self) -> I_FilePath:
        return C_FilePath(self._path.parent)

    # 检查路径对应的文件或目录是否存在。
    def exists(self) -> bool:
        return self._path.exists()

    # 检查路径是否指向普通文件。
    def is_file(self) -> bool:
        return self._path.is_file()

    # 检查路径是否指向目录。
    def is_dir(self) -> bool:
        return self._path.is_dir()

    # 解析为绝对路径并返回路径接口。
    def resolve(self) -> I_FilePath:
        return C_FilePath(self._path.resolve())

    # 展开用户主目录缩写并返回新的路径接口。
    def expanduser(self) -> I_FilePath:
        return C_FilePath(self._path.expanduser())

    # 逐项返回目录下的路径接口，不把原生路径对象交给业务层。
    def iterdir(self) -> Iterator[I_FilePath]:
        return (C_FilePath(item) for item in self._path.iterdir())

    # 仅替换路径末尾名称，保留原父目录。
    def with_name(self, name: str) -> I_FilePath:
        return C_FilePath(self._path.with_name(name))

    # 按参数创建目录，支持创建父级和容许目录已存在。
    def mkdir(self, parents: bool = False, exist_ok: bool = False) -> None:
        self._path.mkdir(parents=parents, exist_ok=exist_ok)

    # 删除文件，并按参数决定文件不存在时是否报错。
    def unlink(self, missing_ok: bool = False) -> None:
        self._path.unlink(missing_ok=missing_ok)

    # 读取文件的原始字节。
    def read_bytes(self) -> bytes:
        return self._path.read_bytes()

    # 写入原始字节并返回写入长度。
    def write_bytes(self, data: bytes) -> int:
        return self._path.write_bytes(data)

    # 按指定编码读取完整文本。
    def read_text(self, encoding: str = "utf-8") -> str:
        return self._path.read_text(encoding=encoding)

    # 按指定编码写入文本并返回写入长度。
    def write_text(self, data: str, encoding: str = "utf-8") -> int:
        return self._path.write_text(data, encoding=encoding)

    # 将原生文件状态转换为只含大小与修改时间的接口。
    def stat(self) -> I_FileStatus:
        from ..Resources.C_FileStatus import C_FileStatus

        status = self._path.stat()
        return C_FileStatus(status.st_size, status.st_mtime_ns)

    # 按文本或二进制模式打开文件，返回对应内容类型的文件流接口。
    @overload
    def open(
        self,
        mode: Literal["rb", "wb", "ab", "r+b", "w+b", "a+b"],
        encoding: None = None,
    ) -> T_FileStream[bytes]: ...

    # 按文本或二进制模式打开文件，返回对应内容类型的文件流接口。
    @overload
    def open(
        self,
        mode: Literal["r", "w", "a", "r+", "w+", "a+"] = "r",
        encoding: str | None = None,
    ) -> T_FileStream[str]: ...

    # 按文本或二进制模式打开文件，返回对应内容类型的文件流接口。
    def open(
        self, mode: str = "r", encoding: str | None = None
    ) -> T_FileStream[str] | T_FileStream[bytes]:
        from ..Resources.C_BinaryFileStream import C_BinaryFileStream
        from ..Resources.C_TextFileStream import C_TextFileStream

        if "b" in mode:
            return C_BinaryFileStream(self._path.open(mode))
        return C_TextFileStream(self._path.open(mode, encoding=encoding))
