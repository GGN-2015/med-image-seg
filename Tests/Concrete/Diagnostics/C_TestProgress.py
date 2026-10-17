from __future__ import annotations

import math
import sqlite3
import sys
from contextlib import closing
from pathlib import Path
from typing import final
from unittest.mock import patch

import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFontDatabase
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QProgressBar
from pytest import MonkeyPatch

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath
from med_image_seg.Concrete.Diagnostics.Progress.C_FakeProcessEstimation import (
    C_FakeProcessEstimation,
)
from med_image_seg.Concrete.Diagnostics.Progress.C_OperationProgressFactory import (
    C_OperationProgressFactory,
)
from med_image_seg.Concrete.Diagnostics.Timing.C_DurationHistory import (
    C_DurationHistory,
)
from med_image_seg.Concrete.Diagnostics.Timing.C_MonotonicClock import C_MonotonicClock
from med_image_seg.Concrete.Presentation.Progress.C_Qt_EstimatedProgressDialog import (
    C_Qt_EstimatedProgressDialog,
)

from ...Abstract.Diagnostics.T_TestProgress import T_TestProgress


# 用可控时钟与独立数据库验证预估与 profiling，不依赖真实等待长任务。
@final
class C_TestProgress(T_TestProgress[MonkeyPatch]):
    # 为本类启用离屏渲染和隔离的默认 profiling 目录。
    @pytest.fixture(autouse=True)
    def _configure_environment(self) -> None:
        from ..Environment.C_TestEnvironment import C_TestEnvironment

        C_TestEnvironment().configure()

    # 把 pytest 原生临时路径适配为项目路径接口。
    @pytest.fixture(name="tmp_path")
    def _adapt_path(self, tmp_path: Path) -> I_FilePath:
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        return C_FilePath(tmp_path)

    # 检查 S 曲线单调有界，超出预计耗时也不能提前返回 100。
    def test_estimator_is_monotonic_and_reserves_completion(self) -> None:
        estimator = C_FakeProcessEstimation(10.0)
        values = [estimator.estimate(elapsed) for elapsed in (0, 2.5, 5, 10, 20, 10000)]
        assert values == sorted(values)
        assert values[:4] == [0, 20, 50, 80]
        assert all(0 <= value < 100 for value in values)
        assert values[-1] == 99

    # 没有历史时采用初始耗时，但不为查询创建空数据库。
    def test_missing_history_uses_default_without_creating_file(
        self, tmp_path: I_FilePath
    ) -> None:
        history = C_DurationHistory(tmp_path / "history.sqlite3")
        assert history.getExpectedSeconds("load", 30.0) == 30.0
        assert not history.getPath().exists()

    # 仅使用最近的成功样本估计耗时，并限制每个操作类别的保留数量。
    def test_history_uses_recent_successes_and_bounds_retention(
        self, tmp_path: I_FilePath
    ) -> None:
        history = C_DurationHistory(tmp_path / "history.sqlite3")
        for seconds in range(1, 141):
            history.record("load", float(seconds), True)
        history.record("load", 10000.0, False)
        history.record("unrelated", 10000.0, True)
        assert history.getExpectedSeconds("load", 30.0) == pytest.approx(130.5)
        with closing(sqlite3.connect(str(history.getPath()))) as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM operation_samples WHERE operation = 'load'"
            ).fetchone()
        assert count == (128,)
        history.getPath().unlink()
        assert not history.getPath().exists()

    # 损坏的历史或不可写目录不得阻止正常影像操作。
    @pytest.mark.parametrize("state", ["corrupt", "unwritable"])
    def test_history_failures_are_nonfatal(
        self, tmp_path: I_FilePath, state: str
    ) -> None:
        blocked = tmp_path / "blocked"
        blocked.write_bytes(b"not-a-database")
        path = blocked if state == "corrupt" else blocked / "history.sqlite3"
        history = C_DurationHistory(path)
        assert history.getExpectedSeconds("load", 30.0) == 30.0
        history.record("load", 1.0, True)
        assert blocked.read_bytes() == b"not-a-database"

    # 拒绝会让估计器退化的无效初始耗时。
    @pytest.mark.parametrize("default_seconds", [0.0, -1.0, math.inf, math.nan])
    def test_invalid_default_duration_is_rejected(
        self, tmp_path: I_FilePath, default_seconds: float
    ) -> None:
        history = C_DurationHistory(tmp_path / "history.sqlite3")
        with pytest.raises(ValueError, match="Expected duration"):
            history.getExpectedSeconds("load", default_seconds)

    # 数据库被其他进程占用时退回初始值，避免界面无限等待。
    def test_locked_history_uses_default(self, tmp_path: I_FilePath) -> None:
        history = C_DurationHistory(tmp_path / "history.sqlite3")
        history.record("load", 2.0, True)
        with closing(sqlite3.connect(str(history.getPath()))) as connection:
            connection.execute("BEGIN EXCLUSIVE")
            assert history.getExpectedSeconds("load", 30.0) == 30.0
            history.record("load", 1000.0, True)
            connection.rollback()
        assert history.getExpectedSeconds("load", 30.0) == 2.0

    # 重复结束不得产生重复样本，完成后耗时与结果保持不变。
    def test_session_records_real_duration_only_once(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch
    ) -> None:
        history = C_DurationHistory(tmp_path / "history.sqlite3")
        clock = C_MonotonicClock()
        now = [100.0]
        monkeypatch.setattr(clock, "getSeconds", lambda: now[0])
        session = C_OperationProgressFactory(clock, history).start("load", 10.0)
        assert session.getPercent() == 0
        now[0] = 110.0
        assert session.getPercent() == 80
        now[0] = 105.0
        assert session.getPercent() == 80
        now[0] = 112.5
        session.finish(True)
        now[0] = 1000.0
        session.finish(False)
        assert session.getFinished()
        assert session.getSucceeded() is True
        assert session.getPercent() == 100
        assert session.getElapsedSeconds() == 12.5
        with closing(sqlite3.connect(str(history.getPath()))) as connection:
            samples = connection.execute(
                "SELECT elapsed_seconds, success FROM operation_samples"
            ).fetchall()
        assert samples == [(12.5, 1)]

    # 异常结束记录失败且继续抛出异常，失败耗时不能参与下一次校准。
    def test_failed_context_records_failure_without_swallowing_error(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch
    ) -> None:
        history = C_DurationHistory(tmp_path / "history.sqlite3")
        clock = C_MonotonicClock()
        now = [0.0]
        monkeypatch.setattr(clock, "getSeconds", lambda: now[0])
        session = C_OperationProgressFactory(clock, history).start("load", 10.0)
        with pytest.raises(RuntimeError, match="failed operation"), session:
            now[0] = 3.0
            raise RuntimeError("failed operation")
        assert session.getElapsedSeconds() == 3.0
        assert session.getSucceeded() is False
        assert session.getPercent() < 100
        assert history.getExpectedSeconds("load", 30.0) == 30.0
        with closing(sqlite3.connect(str(history.getPath()))) as connection:
            samples = connection.execute(
                "SELECT elapsed_seconds, success FROM operation_samples"
            ).fetchall()
        assert samples == [(3.0, 0)]

    # 同时运行的两个会话必须独立计时，不能共享完成状态。
    def test_sessions_are_independent(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch
    ) -> None:
        history = C_DurationHistory(tmp_path / "history.sqlite3")
        clock = C_MonotonicClock()
        now = [0.0]
        monkeypatch.setattr(clock, "getSeconds", lambda: now[0])
        factory = C_OperationProgressFactory(clock, history)
        first = factory.start("first", 10.0)
        now[0] = 2.0
        second = factory.start("second", 10.0)
        now[0] = 3.0
        first.finish()
        assert not second.getFinished()
        now[0] = 5.0
        second.finish()
        assert first.getElapsedSeconds() == second.getElapsedSeconds() == 3.0

    # 工厂使用当前操作的历史耗时，不借用其他操作的样本。
    def test_factory_calibrates_from_matching_history(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch
    ) -> None:
        history = C_DurationHistory(tmp_path / "history.sqlite3")
        history.record("load", 5.0, True)
        history.record("load", 7.0, True)
        history.record("load", 1000.0, False)
        history.record("other", 1000.0, True)
        clock = C_MonotonicClock()
        now = [0.0]
        monkeypatch.setattr(clock, "getSeconds", lambda: now[0])
        session = C_OperationProgressFactory(clock, history).start("load", 30.0)
        assert session.getExpectedSeconds() == 6.0
        now[0] = 3.0
        assert session.getPercent() == 50
        session.finish()

    # 零耗时和无效样本不应导致除零或破坏后续估计。
    def test_zero_and_invalid_samples_remain_safe(self, tmp_path: I_FilePath) -> None:
        history = C_DurationHistory(tmp_path / "history.sqlite3")
        for seconds in (-1.0, math.inf, math.nan):
            history.record("load", seconds, True)
        assert not history.getPath().exists()
        history.record("load", 0.0, True)
        assert history.getExpectedSeconds("load", 30.0) == 0.05
        history.record("overflow", 1.5e308, True)
        history.record("overflow", 1.5e308, True)
        assert history.getExpectedSeconds("overflow", 30.0) == 30.0

    # 验证界面定时刷新、超时不假完成、中英文案和结束后的定时器清理。
    @pytest.mark.parametrize("language", ["en", "zh"])
    @pytest.mark.parametrize("success", [False, True])
    def test_dialog_updates_until_actual_completion(
        self,
        tmp_path: I_FilePath,
        monkeypatch: MonkeyPatch,
        language: str,
        success: bool,
    ) -> None:
        app = QApplication.instance() or QApplication([])
        history = C_DurationHistory(tmp_path / "history.sqlite3")
        clock = C_MonotonicClock()
        now = [0.0]
        monkeypatch.setattr(clock, "getSeconds", lambda: now[0])
        dialog = C_Qt_EstimatedProgressDialog(
            "Loading",
            "Progress",
            "load",
            default_seconds=1.0,
            language=language,
            factory=C_OperationProgressFactory(clock, history),
        )
        try:
            dialog.show()
            app.processEvents()
            progress = dialog.findChild(QProgressBar)
            assert progress is not None
            assert progress.value() == 0
            assert (
                "预估" in progress.format()
                if language == "zh"
                else "Estimated" in progress.format()
            )
            now[0] = 1.0
            QTest.qWait(160)
            assert progress.value() == 80
            now[0] = 10000.0
            QTest.qWait(160)
            assert progress.value() == 99
            assert dialog.isVisible()
            assert not dialog.getOperationProgress().getFinished()
            assert "10000.0" in dialog.labelText()
            if success:
                dialog.accept()
            else:
                dialog.reject()
            assert progress.value() == (100 if success else 99)
            assert dialog.getOperationProgress().getSucceeded() is success
            assert dialog.getOperationProgress().getElapsedSeconds() == 10000.0
            assert not any(timer.isActive() for timer in dialog.findChildren(QTimer))
        finally:
            if not dialog.getOperationProgress().getFinished():
                dialog.reject()
            dialog.deleteLater()
            app.processEvents()

    # 运行中的不可取消任务不能通过 Esc 或关闭窗口被隐藏。
    def test_dialog_cannot_be_closed_while_running(self, tmp_path: I_FilePath) -> None:
        app = QApplication.instance() or QApplication([])
        dialog = C_Qt_EstimatedProgressDialog(
            "Loading",
            "Progress",
            "load",
            factory=C_OperationProgressFactory(
                history=C_DurationHistory(tmp_path / "history.sqlite3")
            ),
        )
        try:
            dialog.show()
            app.processEvents()
            QTest.keyClick(dialog, Qt.Key.Key_Escape)
            assert dialog.isVisible()
            assert not dialog.close()
            assert not dialog.getOperationProgress().getFinished()
        finally:
            dialog.reject()
            dialog.deleteLater()
            app.processEvents()

    # 窗口启动完成后结束进度会话，但不把应用事件循环计入启动耗时。
    def test_startup_records_window_preparation(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch
    ) -> None:
        from med_image_seg.Concrete.Application.Startup.C_Qt_ApplicationHost import (
            C_Qt_ApplicationHost,
        )
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        app = QApplication.instance() or QApplication([])
        path = tmp_path / "startup.sqlite3"
        monkeypatch.setenv("MED_IMAGE_SEG_PROFILE_PATH", str(path))
        before = {id(widget) for widget in QApplication.topLevelWidgets()}
        try:
            with patch.object(QApplication, "exec", return_value=7):
                assert C_Qt_ApplicationHost().run(language="zh") == 7
            with closing(sqlite3.connect(str(path))) as connection:
                samples = connection.execute(
                    "SELECT success FROM operation_samples "
                    "WHERE operation = 'startup.window'"
                ).fetchall()
            assert samples == [(1,)]
        finally:
            for widget in QApplication.topLevelWidgets():
                if id(widget) not in before and isinstance(
                    widget, C_Qt_AnnotationMainWindow
                ):
                    widget.close()
            app.processEvents()

    # 字体服务可重复调用，并在 Windows 启动框出现前准备中文字体。
    def test_startup_font_setup_loads_only_missing_fonts(
        self, monkeypatch: MonkeyPatch
    ) -> None:
        from med_image_seg.Concrete.Presentation.Appearance import C_Qt_FontSetup

        app = QApplication.instance() or QApplication([])
        assert isinstance(app, QApplication)
        monkeypatch.setattr(sys, "platform", "win32")
        with (
            patch.object(QFontDatabase, "hasFamily", side_effect=[False, True]),
            patch.object(QFontDatabase, "addApplicationFont") as load_font,
        ):
            setup = C_Qt_FontSetup()
            setup.configure()
            setup.configure()
            load_font.assert_called_once_with("C:/Windows/Fonts/msyh.ttc")
            assert app.font().family() == "Microsoft YaHei UI"

    # 窗口初始化失败时保留原异常，并记录失败而非成功进度。
    def test_startup_failure_records_failed_duration(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch
    ) -> None:
        from med_image_seg.Concrete.Application.Startup.C_Qt_ApplicationHost import (
            C_Qt_ApplicationHost,
        )

        app = QApplication.instance() or QApplication([])
        path = tmp_path / "startup.sqlite3"
        monkeypatch.setenv("MED_IMAGE_SEG_PROFILE_PATH", str(path))
        with (
            patch(
                "med_image_seg.Concrete.Presentation.Window.C_Qt_AnnotationMainWindow.C_Qt_AnnotationMainWindow",
                side_effect=RuntimeError("startup failed"),
            ),
            pytest.raises(RuntimeError, match="startup failed"),
        ):
            C_Qt_ApplicationHost().run()
        with closing(sqlite3.connect(str(path))) as connection:
            samples = connection.execute(
                "SELECT success FROM operation_samples "
                "WHERE operation = 'startup.window'"
            ).fetchall()
        assert samples == [(0,)]
        app.processEvents()

    # 主窗口按实际加载结果结束进度，校验失败不能显示 100%。
    @pytest.mark.parametrize("success", [False, True])
    def test_image_loading_finishes_with_actual_result(
        self, tmp_path: I_FilePath, success: bool
    ) -> None:
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from ..Editor.C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[])
        try:
            window._show_loading(source)
            dialog = window.requireLoadingDialog()
            assert isinstance(dialog, C_Qt_EstimatedProgressDialog)
            session = dialog.getOperationProgress()
            if not success:
                window.volume_load_failed("simulated image load failure")
            window._finish_loading_ui()
            assert session.getSucceeded() is success
            assert (
                session.getPercent() == 100 if success else session.getPercent() < 100
            )
            assert window.getLoadingDialog() is None
        finally:
            window.close()
            app.processEvents()
