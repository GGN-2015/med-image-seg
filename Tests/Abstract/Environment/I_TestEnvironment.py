from __future__ import annotations

from abc import ABC, abstractmethod


# 设置离屏 Qt 测试环境，让界面用例不依赖可见桌面。
class I_TestEnvironment(ABC):
    # 设置离屏渲染环境，供无可见桌面的 Qt 测试运行。
    @abstractmethod
    def configure(self) -> None: ...
