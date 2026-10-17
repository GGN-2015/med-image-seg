from __future__ import annotations

from typing import final

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent, QKeyEvent
from PySide6.QtWidgets import QProgressBar, QProgressDialog, QWidget

from ....Abstract.Diagnostics.Progress.I_OperationProgress import I_OperationProgress
from ....Abstract.Diagnostics.Progress.I_OperationProgressFactory import (
    I_OperationProgressFactory,
)
from ....Abstract.Presentation.Progress.T_EstimatedProgressDialog import (
    T_EstimatedProgressDialog,
)
from ..Metaclasses.C_Qt_AbcMeta import C_Qt_AbcMeta


# 用主线程定时器显示估计百分比，保留真实结束事件与不可取消的任务语义。
@final
class C_Qt_EstimatedProgressDialog(
    QProgressDialog,
    T_EstimatedProgressDialog[QProgressDialog, QCloseEvent, QKeyEvent],
    metaclass=C_Qt_AbcMeta,
):
    # 装配独立进度会话和定时器，不把耗时估计库直接暴露给 Qt 界面。
    def __init__(
        self,
        label: str,
        title: str,
        operation: str,
        *,
        default_seconds: float = 10.0,
        language: str = "en",
        parent: QWidget | None = None,
        factory: I_OperationProgressFactory | None = None,
    ) -> None:
        from ...Diagnostics.Progress.C_OperationProgressFactory import (
            C_OperationProgressFactory,
        )
        from ...Localization.C_Localizer import C_Localizer

        super().__init__(label, "", 0, 100, parent)
        progress_factory = (
            factory if factory is not None else C_OperationProgressFactory()
        )
        self._progress = progress_factory.start(operation, default_seconds)
        self._label = label
        self._localizer = C_Localizer()
        self._language = self._localizer.normalize_language(language)
        self._bar = QProgressBar(self)
        self._bar.setRange(0, 100)
        self._bar.setTextVisible(True)
        self._bar.setFormat(
            self._localizer.translate("estimated_progress_format", language)
        )
        self.setBar(self._bar)
        self.setWindowTitle(title)
        self.setCancelButton(None)
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setMinimumDuration(0)
        self.setAutoClose(False)
        self.setAutoReset(False)
        self._timer = QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self.refresh)
        self.refresh()
        self._timer.start()

    # 返回兼容现有加载状态接口的 Qt 进度窗口。
    def getHost(self) -> QProgressDialog:
        return self

    # 提供只读计时会话，不允许外部改动任务的结束状态。
    def getOperationProgress(self) -> I_OperationProgress:
        return self._progress

    # 直接更新进度条，避免模态对话框 setValue 引发嵌套事件处理。
    def refresh(self) -> None:
        if self._progress.getFinished():
            return
        self._bar.setValue(self._progress.getPercent())
        details = self._localizer.translate(
            "estimated_progress_details",
            self._language,
            elapsed=self._progress.getElapsedSeconds(),
            expected=self._progress.getExpectedSeconds(),
        )
        self.setLabelText(f"{self._label}\n\n{details}")

    # 只有实际成功事件才停止估计并显示 100%，再沿 Qt 事件链结束窗口。
    def accept(self) -> None:
        self._timer.stop()
        self._progress.finish(True)
        self._bar.setFormat(
            self._localizer.translate("completed_progress_format", self._language)
        )
        self._bar.setValue(self._progress.getPercent())
        super().accept()

    # 失败时停止定时器并保留未完成百分比，不把错误表现为成功完成。
    def reject(self) -> None:
        self._timer.stop()
        self._progress.finish(False)
        self._bar.setValue(self._progress.getPercent())
        super().reject()

    # 拒绝提前关闭运行中的任务；真正结束后才交给 Qt 关闭窗口。
    def closeEvent(self, event: QCloseEvent) -> None:
        if not self._progress.getFinished():
            event.ignore()
            return
        self._timer.stop()
        super().closeEvent(event)

    # 拦截 Esc，避免用户关闭对话框后误以为后台任务已经停止。
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            event.accept()
            return
        super().keyPressEvent(event)
