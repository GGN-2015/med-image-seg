from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Application.Startup.I_ApplicationHost import I_ApplicationHost
from ....Abstract.Domain.Collections.I_ImageCollection import I_ImageCollection

if TYPE_CHECKING:
    pass
import sys
from typing import final

from PySide6.QtCore import QEventLoop
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
        from ...Localization.C_Localizer import C_Localizer
        from ...Presentation.Appearance.C_Qt_FontSetup import C_Qt_FontSetup
        from ...Presentation.Progress.C_Qt_EstimatedProgressDialog import (
            C_Qt_EstimatedProgressDialog,
        )

        app = QApplication.instance() or QApplication(sys.argv)
        C_Qt_FontSetup().configure()
        localizer = C_Localizer()
        dialog = C_Qt_EstimatedProgressDialog(
            localizer.translate("startup_message", language),
            localizer.translate("startup_title", language),
            "startup.window",
            default_seconds=3.0,
            language=language,
        )
        try:
            dialog.show()
            QApplication.processEvents(
                QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents
            )
            from ...Presentation.Window.C_Qt_AnnotationMainWindow import (
                C_Qt_AnnotationMainWindow,
            )

            window = C_Qt_AnnotationMainWindow(
                sources=None if sources is None else list(sources),
                spacing_mm=spacing_mm,
                language=language,
            )
            dialog.refresh()
            window.show()
            dialog.accept()
        except BaseException:
            dialog.reject()
            raise
        finally:
            dialog.deleteLater()
        return app.exec()
