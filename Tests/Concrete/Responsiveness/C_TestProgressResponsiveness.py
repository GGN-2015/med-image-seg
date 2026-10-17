from pathlib import Path
from threading import get_ident
from time import perf_counter
from typing import final

import numpy as np
import pytest
from numpy.typing import NDArray
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox
from pytest import MonkeyPatch

from med_image_seg.Abstract.Algorithms.Masks.I_ManualPlaneAlgorithm import (
    I_ManualPlaneAlgorithm,
)
from med_image_seg.Abstract.Diagnostics.Progress.I_OperationProgress import (
    I_OperationProgress,
)
from med_image_seg.Abstract.Domain.Annotations.I_MutableAnnotationProject import (
    I_MutableAnnotationProject,
)
from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath
from med_image_seg.Concrete.Algorithms.Masks.C_ManualPlaneAlgorithm import (
    C_ManualPlaneAlgorithm,
)
from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
    C_PolygonAnnotation,
)
from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
from med_image_seg.Concrete.Domain.Imaging.C_MedicalVolume import C_MedicalVolume
from med_image_seg.Concrete.Domain.Imaging.C_Metadata import C_Metadata
from med_image_seg.Concrete.Presentation.Progress.C_Qt_EstimatedProgressDialog import (
    C_Qt_EstimatedProgressDialog,
)
from med_image_seg.Concrete.Presentation.Window.C_Qt_AnnotationMainWindow import (
    C_Qt_AnnotationMainWindow,
)
from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

from ...Abstract.Responsiveness.T_TestProgressResponsiveness import (
    T_TestProgressResponsiveness,
)
from ..Editor.C_GuiFixtures import C_GuiFixtures


# 使用真实 512 网格和 1600 顶点，不以 sleep 或替代结果绕开底层库的 GIL 行为。
@final
class C_TestProgressResponsiveness(T_TestProgressResponsiveness[MonkeyPatch]):
    # 使用离屏平台及隔离的耗时历史，不影响用户的图形会话。
    @pytest.fixture(autouse=True)
    def _configure_environment(self) -> None:
        from ..Environment.C_TestEnvironment import C_TestEnvironment

        C_TestEnvironment().configure()

    # 在测试边界将 pytest 路径转换为程序的路径契约。
    @pytest.fixture(name="tmp_path")
    def _adapt_path(self, tmp_path: Path) -> I_FilePath:
        return C_FilePath(tmp_path)

    # 验证真实栅格化发生在子线程，同时量化 GUI 的最长心跳中断而非只数回调次数。
    @pytest.mark.parametrize("operation", ["close", "nifti", "ubd"])
    def test_real_polygon_work_keeps_gui_alive(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch, operation: str
    ) -> None:
        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        volume = C_MedicalVolume(
            data=np.zeros((512, 512, 3), dtype=np.float32),
            spacing_mm=(1.0, 1.0, 1.0),
            origin_lps_mm=(0.0, 0.0, 0.0),
            metadata=C_Metadata("{}"),
            source=source.getPath(),
        )
        window = C_Qt_AnnotationMainWindow(sources=[])
        window.setInternalLoadingSource(source)
        window.volume_loaded(volume)
        window._finish_loading_ui()
        window.show()
        app.processEvents()
        points = C_PointList(
            (
                float(256 + 210 * np.cos(angle)),
                float(256 + 210 * np.sin(angle)),
            )
            for angle in np.linspace(0, 2 * np.pi, 1600, endpoint=False)
        )
        if operation != "close":
            window.requireProject().add_polygon(
                window.getCurrentSlice(), C_PolygonAnnotation(points)
            )
            window.setInternalDirty(True)
        main_thread = get_ident()
        worker_threads: list[int] = []
        ticks: list[float] = []
        labels: list[str] = []
        sessions: list[I_OperationProgress] = []
        probe_errors: list[BaseException] = []
        manual_plane = C_ManualPlaneAlgorithm.manual_plane
        timer = QTimer(window)

        # 只记录线程身份并调用原算法，确保测量的是实际耗时而非测试替身。
        def record_manual_plane(
            self: I_ManualPlaneAlgorithm,
            context: I_MutableAnnotationProject,
            slice_index: int,
        ) -> NDArray[np.bool_]:
            assert isinstance(self, C_ManualPlaneAlgorithm)
            worker_threads.append(get_ident())
            return manual_plane(self, context, slice_index)

        # 进度文本也必须刷新；只让探测用的 QTimer 存活不能算进度窗口正常。
        def observe_progress() -> None:
            try:
                assert get_ident() == main_thread
                dialog = window.getBusyProgressDialog()
                if dialog is None:
                    return
                assert isinstance(dialog, C_Qt_EstimatedProgressDialog)
                assert dialog.isVisible()
                assert not dialog.getOperationProgress().getFinished()
                assert not window.isEnabled()
                ticks.append(perf_counter())
                labels.append(dialog.labelText())
                if not sessions:
                    sessions.append(dialog.getOperationProgress())
            except BaseException as error:
                probe_errors.append(error)
                timer.stop()

        timer.timeout.connect(observe_progress)
        suffix = ".ubd.npz" if operation == "ubd" else ".nii.gz"
        output = tmp_path / f"mask{suffix}"
        try:
            with monkeypatch.context() as patch:
                patch.setattr(
                    C_ManualPlaneAlgorithm, "manual_plane", record_manual_plane
                )
                patch.setattr(QMessageBox, "information", lambda *args: None)
                patch.setattr(
                    QMessageBox, "critical", lambda *args: pytest.fail(str(args))
                )
                ticks.append(perf_counter())
                timer.start(10)
                if operation == "close":
                    window.add_polygon(points, "add")
                else:
                    window._export_mask(output)
                ticks.append(perf_counter())
                timer.stop()
            if probe_errors:
                raise probe_errors[0]
            assert worker_threads and main_thread not in worker_threads
            assert len(ticks) >= 10
            longest_gap = float(np.max(np.diff(ticks)))
            assert longest_gap < 0.35, f"GUI heartbeat paused for {longest_gap:.3f}s"
            assert len(set(labels)) >= 3
            assert len(sessions) == 1
            assert sessions[0].getSucceeded() is True
            assert sessions[0].getPercent() == 100
            assert window.getBusyProgressDialog() is None
            assert window.isEnabled()
            assert not window.getInternalDirty()
            annotation = window.requireProject().annotation(window.getCurrentSlice())
            assert annotation.getPolygonCount() == 1
            assert annotation.getPolygon(0).getPoints().getCount() == 1600
            assert source.getAnnotationPath().is_file()
            if operation != "close":
                assert output.is_file()
        finally:
            timer.stop()
            window.close()
            app.processEvents()
