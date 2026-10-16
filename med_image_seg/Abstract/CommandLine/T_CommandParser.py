from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Generic, TypeVar

T_Options = TypeVar("T_Options", covariant=True)


# 解析影像路径、标注间距和语言选项，隔离命令行解析库。
class T_CommandParser(ABC, Generic[T_Options]):
    # 解析命令行输入并封装启动选项，保留解析器原有错误行为。
    @abstractmethod
    def parse_args(self, argv: Iterable[str] | None = None) -> T_Options: ...

    # 返回命令行用法说明，供帮助入口和测试检查。
    @abstractmethod
    def format_help(self) -> str: ...
