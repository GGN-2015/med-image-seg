from __future__ import annotations

import os
from typing import final

from ...Abstract.Environment.I_TestEnvironment import I_TestEnvironment


# 设置离屏 Qt 测试环境，让界面用例不依赖可见桌面。
@final
class C_TestEnvironment(I_TestEnvironment):
    # 设置离屏渲染环境，供无可见桌面的 Qt 测试运行。
    def configure(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
