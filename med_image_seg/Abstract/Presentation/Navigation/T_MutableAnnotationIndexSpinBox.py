from __future__ import annotations

from abc import abstractmethod
from typing import TypeVar

from .T_AnnotationIndexSpinBox import T_AnnotationIndexSpinBox

T_Host = TypeVar("T_Host", covariant=True)
T_Signal = TypeVar("T_Signal")


# 在只读编号查询上增加提交入口，支持 Python 任意精度整数。
class T_MutableAnnotationIndexSpinBox(T_AnnotationIndexSpinBox[T_Host, T_Signal]):
    # 记录编号输入控件保存的 Python 整数。
    @abstractmethod
    def setInternalValue(self, value: int) -> None: ...

    # 提交非负整数编号，更新显示文本并仅在实际变化时发出信号。
    @abstractmethod
    def setValue(self, value: int) -> None: ...

    # 提交非负编号；空文本回退到原值，避免误切换标注文件。
    @abstractmethod
    def _commit_text(self) -> None: ...
