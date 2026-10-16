from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Application.Startup.I_ApplicationHost import I_ApplicationHost
from ....Abstract.Domain.Collections.I_ImageCollection import I_ImageCollection

if TYPE_CHECKING:
    pass
import sys
from typing import final

from PySide6.QtWidgets import QApplication


# 运行图形界面及事件循环，将界面框架隔离在应用入口之外。
@final
class C_Qt_ApplicationHost(I_ApplicationHost):
    # 创建 Qt 应用和主窗口，进入事件循环并返回退出码。
    def run(
        self,
        *,
        sources: I_ImageCollection | None = None,
        spacing_mm: float = 0.8,
        language: str = "en",
    ) -> int:
        from ...Presentation.Window.C_Qt_AnnotationMainWindow import (
            C_Qt_AnnotationMainWindow,
        )

        app = QApplication.instance() or QApplication(sys.argv)
        window = C_Qt_AnnotationMainWindow(
            sources=None if sources is None else list(sources),
            spacing_mm=spacing_mm,
            language=language,
        )
        window.show()
        return app.exec()
