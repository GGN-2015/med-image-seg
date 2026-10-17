from pathlib import Path
from threading import get_ident
from time import sleep
from typing import final

import numpy as np
import pytest
from numpy.typing import NDArray
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMessageBox,
    QProgressBar,
    QProgressDialog,
    QWidget,
)
from pytest import MonkeyPatch

from med_image_seg.Abstract.Diagnostics.Progress.I_OperationProgress import (
    I_OperationProgress,
)
from med_image_seg.Abstract.Domain.Annotations.I_AnnotationProject import (
    I_AnnotationProject,
)
from med_image_seg.Abstract.Domain.Annotations.I_MutableAnnotationProject import (
    I_MutableAnnotationProject,
)
from med_image_seg.Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
from med_image_seg.Abstract.Storage.Masks.I_MedicalMaskWriter import I_MedicalMaskWriter
from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath
from med_image_seg.Concrete.Diagnostics.Timing.C_DurationHistory import (
    C_DurationHistory,
)
from med_image_seg.Concrete.Domain.Annotations.C_AnnotationProject import (
    C_AnnotationProject,
)
from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
    C_PolygonAnnotation,
)
from med_image_seg.Concrete.Localization.C_Localizer import C_Localizer
from med_image_seg.Concrete.Presentation.Progress.C_Qt_EstimatedProgressDialog import (
    C_Qt_EstimatedProgressDialog,
)
from med_image_seg.Concrete.Presentation.Window.C_Qt_AnnotationMainWindow import (
    C_Qt_AnnotationMainWindow,
)
from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskWriter import C_MedicalMaskWriter
from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

from ...Abstract.Editor.T_TestExportProgress import T_TestExportProgress
from .C_GuiFixtures import C_GuiFixtures


# 用主线程计时器探测真实导出，覆盖进度、保存顺序、错误处理和只读模式恢复。
@final
class C_TestExportProgress(T_TestExportProgress[MonkeyPatch]):
    # 配置离屏 Qt 和隔离的耗时历史，不影响用户的界面或 profiling 数据。
    @pytest.fixture(autouse=True)
    def _configure_environment(self) -> None:
        from ..Environment.C_TestEnvironment import C_TestEnvironment

        C_TestEnvironment().configure()

    # 将 pytest 路径转换成应用使用的路径契约。
    @pytest.fixture(name="tmp_path")
    def _adapt_path(self, tmp_path: Path) -> I_FilePath:
        return C_FilePath(tmp_path)

    # 使用真实导出实现，只延长选定阶段，确认进度控件本身在界面线程持续刷新。
    @pytest.mark.parametrize("suffix", [".nii.gz", ".ubd.npz"])
    @pytest.mark.parametrize("language", ["en", "zh"])
    @pytest.mark.parametrize("stage", ["save", "compute", "write"])
    def test_progress_updates_through_save_compute_and_write(
        self,
        tmp_path: I_FilePath,
        monkeypatch: MonkeyPatch,
        suffix: str,
        language: str,
        stage: str,
    ) -> None:
        monkeypatch.setenv(
            "MED_IMAGE_SEG_PROFILE_PATH", str(tmp_path / "profiling.sqlite3")
        )
        operation = (
            "ui.mask.export.ubd" if suffix == ".ubd.npz" else "ui.mask.export.nifti"
        )
        other_operation = (
            "ui.mask.export.nifti" if suffix == ".ubd.npz" else "ui.mask.export.ubd"
        )
        C_DurationHistory().record(operation, 2.0, True)
        C_DurationHistory().record(other_operation, 20.0, True)
        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[], language=language)
        window.setInternalLoadingSource(source)
        window.volume_loaded(C_GuiFixtures().volume(source))
        window._finish_loading_ui()
        for index in (1, 3):
            window.requireProject().add_polygon(
                index, C_PolygonAnnotation([(2, 2), (8, 2), (5, 8)])
            )
        window.setInternalDirty(True)
        expected = window.requireProject().to_mask(interpolate=True)
        assert expected[:, :, 2].any()
        window.show()
        window.statusBar().showMessage("before export")
        app.processEvents()
        output = tmp_path / "另存目录" / f"导出掩码{suffix}"
        dialog_calls: list[str] = []
        stages: list[str] = []
        worker_ids: list[int] = []
        main_thread_id = get_ident()
        progress_values: list[int] = []
        sessions: list[I_OperationProgress] = []
        probe_errors: list[BaseException] = []
        written_masks: list[NDArray[np.generic]] = []
        messages: list[str] = []
        save = C_AnnotationProject.save
        to_mask = C_AnnotationProject.to_mask
        write = C_MedicalMaskWriter.write
        timer = QTimer(window)

        # 文件选择仍在主线程完成；记录调用次数以探测导出期间的重复请求。
        def select_output(
            parent: QWidget, title: str, directory: str, file_filter: str
        ) -> tuple[str, str]:
            assert get_ident() == main_thread_id
            dialog_calls.append(title)
            return str(output), ""

        # 记录执行线程与顺序，只延迟当前参数指定的一个阶段。
        def checkpoint(current: str) -> None:
            stages.append(current)
            worker_ids.append(get_ident())
            if stage == current:
                sleep(0.5)

        # 延迟自动保存后调用原实现，确认导出不会跳过尚未保存的标注。
        def delayed_save(
            self: I_MutableAnnotationProject, path: I_FilePath
        ) -> I_FilePath:
            assert isinstance(self, C_AnnotationProject)
            checkpoint("save")
            return save(self, path)

        # 检查插值体积生成同样发生在后台，而非仅把最终写盘移入线程。
        def delayed_mask(
            self: I_AnnotationProject, *, interpolate: bool = True
        ) -> NDArray[np.uint8]:
            assert isinstance(self, C_AnnotationProject)
            checkpoint("compute")
            return to_mask(self, interpolate=interpolate)

        # 保存写入器收到的体积快照，并执行实际的格式编码和中文路径写盘。
        def delayed_write(
            self: I_MedicalMaskWriter,
            path: str | I_FilePath,
            mask: NDArray[np.generic],
            reference: I_MedicalVolume,
        ) -> I_FilePath:
            assert isinstance(self, C_MedicalMaskWriter)
            checkpoint("write")
            written_masks.append(mask.copy())
            return write(self, path, mask, reference)

        # 成功提示必须在进度真实结束和界面解锁后发出，且仍位于主线程。
        def record_success(parent: QWidget, title: str, message: str) -> None:
            assert get_ident() == main_thread_id
            assert window.isEnabled()
            assert window.getBusyProgressDialog() is None
            assert sessions[0].getSucceeded() is True
            messages.append(message)

        # 从主线程定时器读取实际进度条，并验证锁定期间不会重入另存为流程。
        def observe_progress() -> None:
            dialog = window.getBusyProgressDialog()
            if dialog is None:
                return
            try:
                assert get_ident() == main_thread_id
                assert isinstance(dialog, C_Qt_EstimatedProgressDialog)
                assert dialog.isVisible()
                assert dialog.windowTitle() == C_Localizer().translate(
                    "export_mask_progress_title", language
                )
                assert not window.isEnabled()
                assert not window.getCanvas().getHost().isEnabled()
                assert window.getInternalClosingPolygon()
                assert not window.getAutosaveTimer().isActive()
                assert all(
                    not action.isEnabled()
                    for action in window.getAnnotationToolbar().actions()
                )
                assert all(
                    not shortcut.isEnabled()
                    for shortcut in window.findChildren(QShortcut)
                )
                session = dialog.getOperationProgress()
                if not sessions:
                    sessions.append(session)
                    window.export_mask()
                    window.export_ubd_mask()
                    window.export_annotations()
                    assert not window.close()
                assert session is sessions[0]
                assert session.getOperation() == operation
                assert session.getExpectedSeconds() == 2.0
                assert not session.getFinished()
                bar = dialog.findChild(QProgressBar)
                assert bar is not None and 0 <= bar.value() < 100
                progress_values.append(bar.value())
            except BaseException as error:
                probe_errors.append(error)
                timer.stop()

        timer.timeout.connect(observe_progress)
        try:
            with monkeypatch.context() as patch:
                patch.setattr(QFileDialog, "getSaveFileName", select_output)
                patch.setattr(QMessageBox, "information", record_success)
                patch.setattr(
                    QMessageBox, "critical", lambda *args: pytest.fail(str(args))
                )
                patch.setattr(C_AnnotationProject, "save", delayed_save)
                patch.setattr(C_AnnotationProject, "to_mask", delayed_mask)
                patch.setattr(C_MedicalMaskWriter, "write", delayed_write)
                timer.start(20)
                if suffix == ".nii.gz":
                    window.export_mask()
                else:
                    window.export_ubd_mask()
                timer.stop()
            if probe_errors:
                raise probe_errors[0]
            assert stages == ["save", "compute", "write"]
            assert main_thread_id not in worker_ids
            assert len(progress_values) >= 3
            assert len(set(progress_values)) >= 2
            assert progress_values == sorted(progress_values)
            assert len(sessions) == 1 and sessions[0].getFinished()
            assert sessions[0].getSucceeded() is True
            assert sessions[0].getPercent() == 100
            assert len(dialog_calls) == 1
            assert len(messages) == 1
            assert output.is_file()
            assert len(written_masks) == 1
            np.testing.assert_array_equal(written_masks[0], expected)
            assert not source.getMaskPath().exists()
            assert not source.getUbdMaskPath().exists()
            assert window.getProjectPath() == source.getAnnotationPath()
            assert not window.getInternalDirty()
            assert window.getBusyProgressDialog() is None
            assert not window.getInternalClosingPolygon()
            assert window.isEnabled()
            assert window.getAutosaveTimer().isActive()
            assert window.statusBar().currentMessage() == "before export"
            assert QApplication.overrideCursor() is None
        finally:
            timer.stop()
            window.close()
            app.processEvents()

    # 每条失败路径都保留既有文件和原控件状态，包括保存仅返回 False 的情况。
    @pytest.mark.parametrize("suffix", [".nii.gz", ".ubd.npz"])
    @pytest.mark.parametrize("stage", ["save", "compute", "write", "precondition"])
    def test_failures_never_report_success_and_restore_ui(
        self,
        tmp_path: I_FilePath,
        monkeypatch: MonkeyPatch,
        suffix: str,
        stage: str,
    ) -> None:
        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[])
        window.setInternalLoadingSource(source)
        window.volume_loaded(C_GuiFixtures().volume(source))
        window._finish_loading_ui()
        window.setInternalDirty(stage != "precondition")
        window.getFileButton().setEnabled(False)
        window.getExportJsonAction().setEnabled(False)
        window.getAutosaveTimer().stop()
        window.show()
        window.statusBar().showMessage("previous status")
        app.processEvents()
        output = tmp_path / f"existing{suffix}"
        output.write_bytes(b"previous mask")
        previous_json = source.getAnnotationPath().read_bytes()
        sessions: list[I_OperationProgress] = []
        errors: list[str] = []
        save = C_AnnotationProject.save
        to_mask = C_AnnotationProject.to_mask
        timer = QTimer(window)

        # 保存阶段可能失败，但失败前不得改动原来的自动保存文件。
        def failing_save(
            self: I_MutableAnnotationProject, path: I_FilePath
        ) -> I_FilePath:
            assert isinstance(self, C_AnnotationProject)
            if stage == "save":
                sleep(0.2)
                raise OSError("simulated mask export failure")
            return save(self, path)

        # 模拟插值体积生成失败，确保不会继续执行写入器。
        def failing_mask(
            self: I_AnnotationProject, *, interpolate: bool = True
        ) -> NDArray[np.uint8]:
            assert isinstance(self, C_AnnotationProject)
            if stage == "compute":
                sleep(0.2)
                raise OSError("simulated mask export failure")
            return to_mask(self, interpolate=interpolate)

        # 在实际落盘前失败，让测试能够核验既有目标没有被后续逻辑覆盖。
        def failing_write(
            self: I_MedicalMaskWriter,
            path: str | I_FilePath,
            mask: NDArray[np.generic],
            reference: I_MedicalVolume,
        ) -> I_FilePath:
            assert stage == "write", "writer must not run after an earlier failure"
            sleep(0.2)
            raise OSError("simulated mask export failure")

        # 某些保存检查仅返回失败；即使项目原本干净，也不能把导出进度记为成功。
        def reject_save(*, notify: bool) -> bool:
            observe_session()
            return False

        # 保留运行中的只读会话，以便对话框销毁后核验最终结果。
        def observe_session() -> None:
            dialog = window.getBusyProgressDialog()
            if isinstance(dialog, C_Qt_EstimatedProgressDialog) and not sessions:
                sessions.append(dialog.getOperationProgress())

        timer.timeout.connect(observe_session)
        QApplication.setOverrideCursor(Qt.CursorShape.CrossCursor)
        try:
            with monkeypatch.context() as patch:
                patch.setattr(
                    QFileDialog, "getSaveFileName", lambda *args: (str(output), "")
                )
                patch.setattr(
                    QMessageBox,
                    "critical",
                    lambda parent, title, message: errors.append(message),
                )
                patch.setattr(
                    QMessageBox,
                    "information",
                    lambda *args: pytest.fail("failed export must not report success"),
                )
                patch.setattr(C_AnnotationProject, "save", failing_save)
                patch.setattr(C_AnnotationProject, "to_mask", failing_mask)
                patch.setattr(C_MedicalMaskWriter, "write", failing_write)
                if stage == "precondition":
                    patch.setattr(window, "save_project", reject_save)
                timer.start(20)
                if suffix == ".nii.gz":
                    window.export_mask()
                else:
                    window.export_ubd_mask()
                timer.stop()
            assert len(sessions) == 1
            assert sessions[0].getFinished()
            assert sessions[0].getSucceeded() is False
            assert sessions[0].getPercent() < 100
            assert errors == (
                [] if stage == "precondition" else ["simulated mask export failure"]
            )
            assert output.read_bytes() == b"previous mask"
            if stage in ("save", "precondition"):
                assert source.getAnnotationPath().read_bytes() == previous_json
            assert window.getInternalDirty() is (stage == "save")
            assert window.isEnabled()
            assert not window.getFileButton().isEnabled()
            assert not window.getExportJsonAction().isEnabled()
            assert not window.getAutosaveTimer().isActive()
            assert not window.getInternalClosingPolygon()
            assert window.getBusyProgressDialog() is None
            assert window.statusBar().currentMessage() == "previous status"
            cursor = QApplication.overrideCursor()
            assert cursor is not None and cursor.shape() == Qt.CursorShape.CrossCursor
        finally:
            timer.stop()
            QApplication.restoreOverrideCursor()
            window.close()
            app.processEvents()

    # 文件选择取消后不得进入忙碌范围，也不得偷偷保存或生成掩码。
    @pytest.mark.parametrize("suffix", [".nii.gz", ".ubd.npz"])
    def test_cancel_does_not_start_work(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch, suffix: str
    ) -> None:
        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[])
        window.setInternalLoadingSource(source)
        window.volume_loaded(C_GuiFixtures().volume(source))
        window._finish_loading_ui()
        previous_json = source.getAnnotationPath().read_bytes()
        window.setInternalDirty(True)

        # 若取消后仍创建可见进度窗口，直接让测试失败。
        def unexpected_progress(self: QProgressDialog) -> None:
            pytest.fail("cancelled export must not show progress")

        # 若取消后仍执行数据任务，直接让测试失败而不是容忍无效工作。
        def unexpected_mask(
            self: I_AnnotationProject, *, interpolate: bool = True
        ) -> NDArray[np.uint8]:
            pytest.fail("cancelled export must not compute a mask")

        try:
            with monkeypatch.context() as patch:
                patch.setattr(QFileDialog, "getSaveFileName", lambda *args: ("", ""))
                patch.setattr(C_Qt_EstimatedProgressDialog, "show", unexpected_progress)
                patch.setattr(C_AnnotationProject, "to_mask", unexpected_mask)
                if suffix == ".nii.gz":
                    window.export_mask()
                else:
                    window.export_ubd_mask()
            assert window.getBusyProgressDialog() is None
            assert not window.getInternalClosingPolygon()
            assert window.getInternalDirty()
            assert source.getAnnotationPath().read_bytes() == previous_json
            assert not source.getMaskPath().exists()
            assert not source.getUbdMaskPath().exists()
            assert QApplication.overrideCursor() is None
        finally:
            window.close()
            app.processEvents()

    # 在观察模式下导出不应启用编辑控件、关闭三视图或更改标注文件编号。
    @pytest.mark.parametrize("suffix", [".nii.gz", ".ubd.npz"])
    def test_observation_export_preserves_readonly_state(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch, suffix: str
    ) -> None:
        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[])
        window.setInternalLoadingSource(source)
        window.volume_loaded(C_GuiFixtures().volume(source))
        window._finish_loading_ui()
        window.show()
        app.processEvents()
        window.getObserveRadio().setChecked(True)
        previous_path = window.getProjectPath()
        output = tmp_path / f"observation{suffix}"
        try:
            with monkeypatch.context() as patch:
                patch.setattr(
                    QFileDialog, "getSaveFileName", lambda *args: (str(output), "")
                )
                patch.setattr(QMessageBox, "information", lambda *args: None)
                patch.setattr(
                    QMessageBox, "critical", lambda *args: pytest.fail(str(args))
                )
                if suffix == ".nii.gz":
                    window.export_mask()
                else:
                    window.export_ubd_mask()
            assert output.is_file()
            assert window.isEnabled()
            assert window.getReadOnly()
            assert window.getCanvas().getReadOnly()
            assert window.getProjectPath() == previous_path
            assert all(
                not control.isEnabled() for control in window.iterEditingControls()
            )
            assert all(
                not shortcut.isEnabled() for shortcut in window.iterEditingShortcuts()
            )
            assert all(
                view.getHost().isVisible() for view in window.iterObservationWindows()
            )
            assert window.getSliceSlider().isEnabled()
            assert window.getExportAction().isEnabled()
            assert window.getExportUbdAction().isEnabled()
            assert window.getBusyProgressDialog() is None
        finally:
            window.close()
            app.processEvents()
