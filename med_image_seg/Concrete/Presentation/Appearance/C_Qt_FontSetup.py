import sys
from typing import final

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

from ....Abstract.Presentation.Appearance.I_FontSetup import I_FontSetup


# 集中准备 Windows 中文字体，避免主窗口创建前的启动提示显示方框。
@final
class C_Qt_FontSetup(I_FontSetup):
    # 沿用主界面的微软雅黑设置，仅在字体未登记时载入本机字体文件。
    def configure(self) -> None:
        application = QApplication.instance()
        if sys.platform == "win32" and isinstance(application, QApplication):
            if not QFontDatabase.hasFamily("Microsoft YaHei"):
                QFontDatabase.addApplicationFont("C:/Windows/Fonts/msyh.ttc")
            application.setFont(QFont("Microsoft YaHei UI", 9))
