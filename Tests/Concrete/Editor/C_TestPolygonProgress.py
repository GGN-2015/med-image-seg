from pathlib import Path
from threading import get_ident
from time import sleep
from typing import final

import numpy as np
import pytest
from numpy.typing import NDArray
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QProgressBar
from pytest import MonkeyPatch

from med_image_seg.Abstract.Diagnostics.Progress.I_OperationProgress import (
    I_OperationProgress,
)
from med_image_seg.Abstract.Domain.Annotations.I_MutableAnnotationProject import (
    I_MutableAnnotationProject,
)
from med_image_seg.Abstract.Domain.Annotations.I_PolygonAnnotation import (
    I_PolygonAnnotation,
)
from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath
from med_image_seg.Concrete.Domain.Annotations.C_AnnotationProject import (
    C_AnnotationProject,
)
from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
from med_image_seg.Concrete.Presentation.Progress.C_Qt_EstimatedProgressDialog import (
    C_Qt_EstimatedProgressDialog,
)
from med_image_seg.Concrete.Presentation.Window.C_Qt_AnnotationMainWindow import (
    C_Qt_AnnotationMainWindow,
)
from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

from ...Abstract.Editor.T_TestPolygonProgress import T_TestPolygonProgress
from .C_GuiFixtures import C_GuiFixtures


# 用真实空格事件和主线程定时器探测进度，而不是只检查对话框是否被创建。
@final
class C_TestPolygonProgress(T_TestPolygonProgress[MonkeyPatch]):
    # 使用离屏 Qt 以及隔离的耗时历史，避免污染用户配置。
    @pytest.fixture(autouse=True)
    def _configure_environment(self) -> None:
        from ..Environment.C_TestEnvironment import C_TestEnvironment

        C_TestEnvironment().configure()

    # 在测试边界把 pytest 路径转换成应用使用的路径契约。
    @pytest.fixture(name="tmp_path")
    def _adapt_path(self, tmp_path: Path) -> I_FilePath:
        return C_FilePath(tmp_path)

    # 验证三种耗时均在后台执行，真正的进度控件仍持续更新且结束前不到 100%。
    @pytest.mark.parametrize("stage", ["annotation", "save", "coverage"])
    @pytest.mark.parametrize("language", ["en", "zh"])
    def test_space_closure_updates_progress_during_background_work(
        self,
        tmp_path: I_FilePath,
        monkeypatch: MonkeyPatch,
        stage: str,
        language: str,
    ) -> None:
        monkeypatch.setenv(
            "MED_IMAGE_SEG_PROFILE_PATH", str(tmp_path / "profiling.sqlite3")
        )
        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[], language=language)
        window.setInternalLoadingSource(source)
        window.volume_loaded(C_GuiFixtures().volume(source))
        window._finish_loading_ui()
        window.show()
        window.activateWindow()
        window.getCanvas().getHost().setFocus()
        app.processEvents()
        window.getCanvas().setDraftPoints(C_PointList([(2, 2), (8, 2), (5, 8)]))
        window.getCanvas()._update_draft()
        main_thread_id = get_ident()
        worker_thread_ids: list[int] = []
        probe_thread_ids: list[int] = []
        progress_values: list[int] = []
        sessions: list[I_OperationProgress] = []
        probe_errors: list[BaseException] = []
        add_polygon = C_AnnotationProject.add_polygon
        save = C_AnnotationProject.save
        mask_presence = C_AnnotationProject.mask_presence
        timer = QTimer(window)

        # 人为延长被选中的数据阶段，给界面定时器留下可重复的观察窗口。
        def delay() -> None:
            worker_thread_ids.append(get_ident())
            sleep(0.45)

        # 延迟添加后仍执行原实现，避免用假结果掩盖标注行为变化。
        def delayed_add(
            self: I_MutableAnnotationProject, index: int, polygon: I_PolygonAnnotation
        ) -> None:
            assert isinstance(self, C_AnnotationProject)
            delay()
            add_polygon(self, index, polygon)

        # 延迟真实写盘，保留零号和编号标注的保存语义。
        def delayed_save(
            self: I_MutableAnnotationProject,
            path: I_FilePath,
            *,
            delete_if_empty: bool = False,
        ) -> I_FilePath:
            assert isinstance(self, C_AnnotationProject)
            delay()
            return save(self, path, delete_if_empty=delete_if_empty)

        # 延迟真实区间计算，确认计算后的覆盖条仍能反映新增轮廓。
        def delayed_presence(
            self: I_MutableAnnotationProject, *, interpolate: bool = True
        ) -> NDArray[np.bool_]:
            assert isinstance(self, C_AnnotationProject)
            delay()
            return mask_presence(self, interpolate=interpolate)

        # 只在主线程读取控件；把回调异常带回测试，避免 Qt 吞掉断言失败。
        def observe_progress() -> None:
            dialog = window.getBusyProgressDialog()
            if dialog is None:
                return
            try:
                assert isinstance(dialog, C_Qt_EstimatedProgressDialog)
                assert dialog.isVisible()
                assert dialog.windowTitle() == (
                    "正在闭合多边形" if language == "zh" else "Closing polygon"
                )
                C_GuiFixtures().assert_polygon_busy(window)
                session = dialog.getOperationProgress()
                if not sessions:
                    sessions.append(session)
                assert session is sessions[0]
                assert not session.getFinished()
                assert session.getOperation() == "polygon.close"
                bar = dialog.findChild(QProgressBar)
                assert bar is not None
                assert 0 <= bar.value() < 100
                progress_values.append(bar.value())
                probe_thread_ids.append(get_ident())
            except BaseException as error:
                probe_errors.append(error)
                timer.stop()

        timer.timeout.connect(observe_progress)
        try:
            with monkeypatch.context() as patch:
                if stage == "annotation":
                    patch.setattr(C_AnnotationProject, "add_polygon", delayed_add)
                elif stage == "save":
                    patch.setattr(C_AnnotationProject, "save", delayed_save)
                else:
                    patch.setattr(
                        C_AnnotationProject, "mask_presence", delayed_presence
                    )
                timer.start(20)
                QTest.keyClick(
                    window.getCanvas().getHost().viewport(), Qt.Key.Key_Space
                )
                timer.stop()
            if probe_errors:
                raise probe_errors[0]
            assert len(progress_values) >= 3
            assert len(set(progress_values)) >= 2
            assert progress_values == sorted(progress_values)
            assert probe_thread_ids and set(probe_thread_ids) == {main_thread_id}
            assert worker_thread_ids and main_thread_id not in worker_thread_ids
            assert len(sessions) == 1
            assert sessions[0].getFinished()
            assert sessions[0].getSucceeded() is True
            assert sessions[0].getPercent() == 100
            assert window.getBusyProgressDialog() is None
            assert window.isEnabled()
            assert not window.getInternalClosingPolygon()
            assert not window.getInternalDirty()
            assert window.getAutosaveTimer().isActive()
            assert source.getAnnotationPath().is_file()
            current = window.getCurrentSlice()
            assert window.requireProject().annotation(current).getPolygonCount() == 1
            assert window.getMaskCoverageBar().getPresence()[current]
        finally:
            timer.stop()
            window.close()
            app.processEvents()

    # 验证分批绘制期间能刷新进度，同时保留全部顶点和正常编辑的非重入行为。
    @pytest.mark.parametrize("enabled", [False, True])
    def test_large_polygon_refresh_yields_only_while_locked(
        self, enabled: bool
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )
        from med_image_seg.Concrete.Presentation.Canvas.C_Qt_SliceCanvas import (
            C_Qt_SliceCanvas,
        )

        app = C_GuiFixtures().app()
        canvas = C_Qt_SliceCanvas()
        canvas.setEnabled(enabled)
        canvas.show()
        app.processEvents()
        points = C_PointList(
            [
                (float(32 + 20 * np.cos(angle)), float(32 + 20 * np.sin(angle)))
                for angle in np.linspace(0, 2 * np.pi, 300, endpoint=False)
            ]
        )
        polygon = C_PolygonAnnotation(points)
        observed_handle_counts: list[int] = []
        timer = QTimer(canvas)

        # 用零间隔计时器确认事件是在绘制中间处理，而不是在绘制结束之后处理。
        def observe_render() -> None:
            observed_handle_counts.append(canvas.getHandleCount())
            timer.stop()

        timer.timeout.connect(observe_render)
        try:
            timer.start(0)
            canvas.set_slice(np.zeros((64, 64), dtype=np.uint8), [polygon])
            timer.stop()
            assert canvas.getHandleCount() == 300
            assert observed_handle_counts == ([] if enabled else [128])
        finally:
            timer.stop()
            canvas.close()
            app.processEvents()

    # 区分传播异常和保存失败返回值，确认两条路径都拒绝进度且解除界面锁定。
    @pytest.mark.parametrize("stage", ["annotation", "save", "coverage"])
    def test_failed_closure_rejects_progress_and_restores_editor(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch, stage: str
    ) -> None:
        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[])
        window.setInternalLoadingSource(source)
        window.volume_loaded(C_GuiFixtures().volume(source))
        window._finish_loading_ui()
        window.show()
        app.processEvents()
        sessions: list[I_OperationProgress] = []
        timer = QTimer(window)

        # 添加失败发生在保存前，原异常必须原样交回界面线程。
        def failed_add(
            self: I_MutableAnnotationProject, index: int, polygon: I_PolygonAnnotation
        ) -> None:
            sleep(0.2)
            raise RuntimeError("background polygon failure")

        # 保存失败应保留 dirty 状态供重试，不能在进度条显示成功。
        def failed_save(
            self: I_MutableAnnotationProject, path: I_FilePath
        ) -> I_FilePath:
            sleep(0.2)
            raise OSError("background JSON save failure")

        # 区间计算失败发生在写盘后，也必须被视为闭合流程失败。
        def failed_presence(
            self: I_MutableAnnotationProject, *, interpolate: bool = True
        ) -> NDArray[np.bool_]:
            sleep(0.2)
            raise RuntimeError("background polygon failure")

        # 在任务运行中保留只读会话，关闭对话框后仍可验证最终结果。
        def observe_session() -> None:
            dialog = window.getBusyProgressDialog()
            if isinstance(dialog, C_Qt_EstimatedProgressDialog) and not sessions:
                sessions.append(dialog.getOperationProgress())

        timer.timeout.connect(observe_session)
        try:
            with monkeypatch.context() as patch:
                if stage == "annotation":
                    patch.setattr(C_AnnotationProject, "add_polygon", failed_add)
                elif stage == "save":
                    patch.setattr(C_AnnotationProject, "save", failed_save)
                else:
                    patch.setattr(C_AnnotationProject, "mask_presence", failed_presence)
                timer.start(20)
                if stage == "save":
                    window.add_polygon(C_PointList([(2, 2), (8, 2), (5, 8)]), "add")
                    assert window.getInternalDirty()
                    assert (
                        "background JSON save failure"
                        in window.getAutosaveStatus().text()
                    )
                else:
                    with pytest.raises(
                        RuntimeError, match="background polygon failure"
                    ):
                        window.add_polygon(C_PointList([(2, 2), (8, 2), (5, 8)]), "add")
                timer.stop()
            assert len(sessions) == 1
            assert sessions[0].getFinished()
            assert sessions[0].getSucceeded() is False
            assert sessions[0].getPercent() < 100
            assert window.getBusyProgressDialog() is None
            assert window.isEnabled()
            assert not window.getInternalClosingPolygon()
            assert window.getAutosaveTimer().isActive()
        finally:
            timer.stop()
            window.close()
            app.processEvents()
