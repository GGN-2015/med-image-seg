from __future__ import annotations

from abc import ABCMeta
from typing import final

from PySide6.QtWidgets import QMainWindow

from ....Abstract.Presentation.Metaclasses.I_Qt_MetaFactory import I_Qt_MetaFactory


# 组合 Qt 与 ABC 的元类，保留控件继承和抽象方法检查。
@final
class C_Qt_AbcMeta(ABCMeta, type(QMainWindow), I_Qt_MetaFactory):
    # 返回尚未实现的抽象方法数量。
    def getAbstractMethodCount(self) -> int:
        return len(self.__abstractmethods__)
