from __future__ import annotations

import os
from pathlib import Path
from tempfile import gettempdir
from typing import final

from ...Abstract.Environment.I_TestEnvironment import I_TestEnvironment


# 设置离屏 Qt 和独立耗时历史，避免界面测试污染用户的 profiling 数据。
@final
class C_TestEnvironment(I_TestEnvironment):
    # 使用离屏渲染和进程独立的临时数据库，不覆盖用户显式配置。
    def configure(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        os.environ.setdefault(
            "MED_IMAGE_SEG_PROFILE_PATH",
            str(
                Path(gettempdir())
                / "med-image-seg-tests"
                / str(os.getpid())
                / "profiling.sqlite3"
            ),
        )
