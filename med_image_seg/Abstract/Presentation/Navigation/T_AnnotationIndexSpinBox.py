from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar

from ..Window.T_HostedObject import T_HostedObject

T_Host = TypeVar("T_Host", covariant=True)
T_Signal = TypeVar("T_Signal")


# 用文本和 Python 整数表示标注编号，避免 Qt 原生整数范围限制。
class T_AnnotationIndexSpinBox(T_HostedObject[T_Host], Generic[T_Host, T_Signal]):
    # 返回编号输入控件保存的 Python 整数。
    @abstractmethod
    def getInternalValue(self) -> int: ...

    # 返回已提交的非负 Python 整数编号，不受 Qt 原生整数范围限制。
    @abstractmethod
    def value(self) -> int: ...

    # 提供标注编号变更信号，避免依赖 Qt 原生整数范围。
    @abstractmethod
    def getValueChanged(self) -> T_Signal: ...
