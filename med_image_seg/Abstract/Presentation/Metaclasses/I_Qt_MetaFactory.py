from __future__ import annotations

from abc import ABC, abstractmethod


# 提供元类的抽象方法计数契约，供 Qt 与 ABC 组合时检查实现完整性。
class I_Qt_MetaFactory(ABC):
    # 返回尚未实现的抽象方法数量。
    @abstractmethod
    def getAbstractMethodCount(self) -> int: ...
