from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T_Host = TypeVar("T_Host", covariant=True)


# 用泛型提供界面宿主，避免抽象层导入 Qt 控件类型。
class T_HostedObject(ABC, Generic[T_Host]):
    # 返回底层界面宿主。
    @abstractmethod
    def getHost(self) -> T_Host: ...
