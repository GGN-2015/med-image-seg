from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Storage.Paths.I_FilePath import I_FilePath
from abc import ABC, abstractmethod
from collections.abc import Iterable


# 把命令行选项转换为应用配置，再交给界面宿主启动。
class I_ApplicationLauncher(ABC):
    # 用启动选项构造应用，再将影像集合、间距和语言传入界面宿主。
    @abstractmethod
    def launch(
        self,
        paths: Iterable[str | I_FilePath] = (),
        *,
        spacing_mm: float = 0.8,
        language: str = "en",
    ) -> int: ...
