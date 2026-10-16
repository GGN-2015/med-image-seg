from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .I_CommandOptions import I_CommandOptions
    from .T_CommandParser import T_CommandParser
from abc import ABC, abstractmethod


# 协调参数解析与应用启动，并返回进程退出码。
class I_CommandLine(ABC):
    # 配置位置参数、重复影像选项、间距和语言的命令行解析规则。
    @abstractmethod
    def build_parser(self) -> T_CommandParser[I_CommandOptions]: ...

    # 解析参数后启动应用，并返回界面宿主的退出码。
    @abstractmethod
    def run(self, argv: Iterable[str] | None = None) -> int: ...
