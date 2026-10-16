from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Application.Startup.I_ApplicationLauncher import I_ApplicationLauncher

if TYPE_CHECKING:
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
from collections.abc import Iterable
from typing import final


# 把命令行选项转换为应用配置，再交给界面宿主启动。
@final
class C_ApplicationLauncher(I_ApplicationLauncher):
    # 用启动选项构造应用，再将影像集合、间距和语言传入界面宿主。
    def launch(
        self,
        paths: Iterable[str | I_FilePath] = (),
        *,
        spacing_mm: float = 0.8,
        language: str = "en",
    ) -> int:
        from .C_ApplicationFactory import C_ApplicationFactory

        return (
            C_ApplicationFactory()
            .from_paths(paths, spacing_mm=spacing_mm, language=language)
            .run()
        )
