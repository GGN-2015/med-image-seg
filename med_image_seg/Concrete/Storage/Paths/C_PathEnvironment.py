from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Storage.Paths.I_PathEnvironment import I_PathEnvironment

if TYPE_CHECKING:
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
from pathlib import Path
from typing import final


# 提供工作目录，供临时路径回退策略查询运行环境。
@final
class C_PathEnvironment(I_PathEnvironment):
    # 返回进程当前工作目录。
    def getWorkingDirectory(self) -> I_FilePath:
        from .C_FilePath import C_FilePath

        return C_FilePath(Path.cwd())
