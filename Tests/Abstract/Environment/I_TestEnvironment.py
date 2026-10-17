from __future__ import annotations

from abc import ABC, abstractmethod


# 设置离屏 Qt 和独立耗时历史，避免界面测试污染用户的 profiling 数据。
class I_TestEnvironment(ABC):
    # 使用离屏渲染和进程独立的临时数据库，不覆盖用户显式配置。
    @abstractmethod
    def configure(self) -> None: ...
