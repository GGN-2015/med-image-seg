from __future__ import annotations

import operator
from typing import final

from PySide6.QtCore import Signal, SignalInstance
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QAbstractSpinBox

from ....Abstract.Presentation.Navigation import (
    T_MutableAnnotationIndexSpinBox,
)
from ..Metaclasses.C_Qt_AbcMeta import C_Qt_AbcMeta


# 用文本和 Python 整数表示标注编号，避免 Qt 原生整数范围限制。
@final
class C_Qt_AnnotationIndexSpinBox(
    QAbstractSpinBox,
    T_MutableAnnotationIndexSpinBox[QAbstractSpinBox, SignalInstance],
    metaclass=C_Qt_AbcMeta,
):
    # 返回编号输入控件保存的 Python 整数。
    def getInternalValue(self) -> int:
        return self._state_value

    # 记录编号输入控件保存的 Python 整数。
    def setInternalValue(self, value: int) -> None:
        self._state_value = value

    valueChanged = Signal(object)

    # 用文本输入及 Python 整数初始化编号，并连接提交信号。
    def __init__(self) -> None:
        super().__init__()
        self.setInternalValue(0)
        self.lineEdit().setText("0")
        self.setKeyboardTracking(False)
        self.setAccelerated(True)
        self.editingFinished.connect(self._commit_text)

    # 返回已提交的非负 Python 整数编号，不受 Qt 原生整数范围限制。
    def value(self) -> int:
        return self.getInternalValue()

    # 提交非负整数编号，更新显示文本并仅在实际变化时发出信号。
    def setValue(self, value: int) -> None:
        value = operator.index(value)
        if value < 0:
            raise ValueError("annotation index must be nonnegative")
        self.lineEdit().setText(str(value))
        if value != self.getInternalValue():
            self.setInternalValue(value)
            self.valueChanged.emit(value)

    # 只接受 ASCII 非负整数字符串；空输入暂作可继续编辑的中间状态。
    def validate(self, text: str, position: int) -> tuple[QValidator.State, str, int]:
        if not text:
            state = QValidator.State.Intermediate
        elif text.isascii() and text.isdecimal():
            state = QValidator.State.Acceptable
        else:
            state = QValidator.State.Invalid
        return (state, text, position)

    # 把无效或空的编号文本恢复为当前已提交编号。
    def fixup(self, text: str) -> str:
        return str(self.getInternalValue())

    # 提交非负编号；空文本回退到原值，避免误切换标注文件。
    def _commit_text(self) -> None:
        text = self.lineEdit().text()
        self.setValue(int(text) if text else self.getInternalValue())

    # 按箭头步长增减 Python 整数编号，最小值限制为零。
    def stepBy(self, steps: int) -> None:
        text = self.lineEdit().text()
        current = int(text) if text else self.getInternalValue()
        self.setValue(max(0, current + steps))

    # 根据只读状态和当前编号决定上下箭头是否可用。
    def stepEnabled(self) -> QAbstractSpinBox.StepEnabledFlag:
        if self.isReadOnly():
            return QAbstractSpinBox.StepEnabledFlag.StepNone
        flags = QAbstractSpinBox.StepEnabledFlag.StepUpEnabled
        text = self.lineEdit().text()
        if (int(text) if text else self.getInternalValue()) > 0:
            flags |= QAbstractSpinBox.StepEnabledFlag.StepDownEnabled
        return flags

    # 返回底层界面宿主。
    def getHost(self) -> QAbstractSpinBox:
        return self

    # 提供标注编号变更信号，避免依赖 Qt 原生整数范围。
    def getValueChanged(self) -> SignalInstance:
        return self.valueChanged
