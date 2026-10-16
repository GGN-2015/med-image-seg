from __future__ import annotations

import argparse
from collections.abc import Iterable
from typing import final

from ...Abstract.CommandLine.I_CommandOptions import I_CommandOptions
from ...Abstract.CommandLine.T_CommandParser import T_CommandParser


# 解析影像路径、标注间距和语言选项，隔离命令行解析库。
@final
class C_CommandParser(T_CommandParser[I_CommandOptions]):
    # 装配参数解析规则，并保存解析器实例供帮助和解析复用。
    def __init__(self, parser: argparse.ArgumentParser) -> None:
        self._parser = parser

    # 解析命令行输入并封装启动选项，保留解析器原有错误行为。
    def parse_args(self, argv: Iterable[str] | None = None) -> I_CommandOptions:
        from .C_CommandOptions import C_CommandOptions

        return C_CommandOptions(
            self._parser.parse_args(None if argv is None else list(argv))
        )

    # 返回命令行用法说明，供帮助入口和测试检查。
    def format_help(self) -> str:
        return self._parser.format_help()
