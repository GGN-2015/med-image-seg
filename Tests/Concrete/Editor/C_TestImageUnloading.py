from pathlib import Path
from time import monotonic
from typing import final
from unittest.mock import patch

import numpy as np
import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath
from med_image_seg.Concrete.Domain.Annotations import C_AnnotationProject
from med_image_seg.Concrete.Domain.Geometry import C_PointList
from med_image_seg.Concrete.Presentation.Loading import (
    C_Qt_ExternalMaskLoadThread,
    C_Qt_VolumeLoadThread,
)
from med_image_seg.Concrete.Presentation.Window import C_Qt_AnnotationMainWindow
from med_image_seg.Concrete.Storage.Paths import C_FilePath
from med_image_seg.Concrete.Storage.Projects import C_ProjectRepository

from ...Abstract.Editor.I_TestImageUnloading import I_TestImageUnloading
from .C_GuiFixtures import C_GuiFixtures


# 在真实 Qt 场景中验证卸载事务，覆盖磁盘安全、状态清理及再次加载。
@final
class C_TestImageUnloading(I_TestImageUnloading):
    # 使用离屏平台和隔离的 profiling 目录，不影响用户正在使用的界面。
    @pytest.fixture(autouse=True)
    def _configure_environment(self) -> None:
        from ..Environment.C_TestEnvironment import C_TestEnvironment

        C_TestEnvironment().configure()

    # 把 pytest 原生临时路径转换为项目路径契约。
    @pytest.fixture(name="tmp_path")
    def _adapt_path(self, tmp_path: Path) -> I_FilePath:
        return C_FilePath(tmp_path)

    # 列表存在文件不代表已经打开影像，按钮不得据此提前启用。
    def test_unload_is_disabled_without_an_open_image(
        self, tmp_path: I_FilePath
    ) -> None:
        app = C_GuiFixtures().app()
        window = C_Qt_AnnotationMainWindow(sources=[])
        try:
            assert not window.getUnloadImageButton().isEnabled()
            assert not window.unload_imported_image()
            source = C_GuiFixtures().source(tmp_path)
            window.add_sources([source.getPath()])
            app.processEvents()
            assert window.getSourceList().count() == 1
            assert window.getVolume() is None
            assert not window.getUnloadImageButton().isEnabled()
            assert not window.unload_imported_image()
            assert len(window.getSources()) == 1
            assert source.getPath().exists()
        finally:
            window.close()

    # 选中另一行时仍移除打开项，并在卸载前闭合和保存有效草稿。
    @pytest.mark.parametrize("language", ["en", "zh"])
    @pytest.mark.parametrize("annotation_index", [0, 7])
    def test_unload_removes_current_image_not_selected_row(
        self, tmp_path: I_FilePath, language: str, annotation_index: int
    ) -> None:
        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        before, after = tmp_path / "before.nii", tmp_path / "after.nii"
        before.write_bytes(b"before image")
        after.write_bytes(b"after image")
        originals = tuple(
            path.read_bytes() for path in (before, source.getPath(), after)
        )
        window = C_Qt_AnnotationMainWindow(sources=[], language=language)
        try:
            window.add_sources([before, source.getPath(), after])
            window.setAnnotationIndex(annotation_index)
            window.setInternalLoadingSource(source)
            window.volume_loaded(C_GuiFixtures().volume(source))
            window._finish_loading_ui()
            window.show()
            app.processEvents()
            assert window.getUnloadImageButton().isEnabled()
            assert window.getUnloadImageButton().text() == (
                "Unload imported image" if language == "en" else "卸载已导入影像"
            )
            project_path = window.requireProjectPath()
            slice_index = window.getCurrentSlice()
            window.getCanvas().setDraftPoints(
                C_PointList([(2.0, 2.0), (8.0, 2.0), (5.0, 8.0)])
            )
            window.getCanvas()._update_draft()
            window.getSourceList().setCurrentRow(2)
            window.getUnloadImageButton().click()
            app.processEvents()
            assert window.getVolume() is None
            assert window.getProject() is None
            assert window.getCurrentSource() is None
            assert window.getProjectPath() is None
            assert window.getLoadThread() is None
            assert window.getInternalLoadingSource() is None
            assert not window.getInternalDirty()
            assert not window.getUnloadImageButton().isEnabled()
            assert window.getFileButton().isEnabled()
            assert window.getLoadButton().isEnabled()
            assert all(
                not control.isEnabled() for control in window.iterEditorWidgets()
            )
            assert all(
                not action.isEnabled()
                for action in window.getAnnotationToolbar().actions()
            )
            assert window.getCanvas().getHost().scene().items() == []
            assert window.getCanvas().getInternalImageRect().isEmpty()
            assert window.getCanvas().getDraftPointCount() == 0
            assert window.getCanvas().getHandleCount() == 0
            assert window.getCanvas().getInternalFirstImage()
            assert window.getMaskCoverageBar().getPresence() == ()
            assert window.getSliceSlider().maximum() == 0
            assert window.getSliceSpin().value() == 0
            assert window.getAnnotationIndex() == 0
            assert window.getSourceList().count() == 2
            assert window.getSourceList().currentItem() is None
            assert tuple(item.getPath() for item in window.getSources()) == (
                before,
                after,
            )
            for index in range(2):
                assert (
                    window.getSourceList().item(index).data(Qt.ItemDataRole.UserRole)
                    == index
                )
            assert (
                window.getSources().findByFingerprint(source.getFingerprint()) is None
            )
            saved = C_ProjectRepository().load(project_path)
            assert saved.annotation(slice_index).getPolygonCount() == 1
            assert (
                tuple(path.read_bytes() for path in (before, source.getPath(), after))
                == originals
            )
            assert window.isEnabled()
            assert QApplication.overrideCursor() is None
        finally:
            window.close()

    # 模拟磁盘保存错误，确认卸载事务不会提前移除影像或清空画布。
    def test_save_failure_keeps_image_and_list(self, tmp_path: I_FilePath) -> None:
        C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[])
        try:
            window.add_sources([source.getPath()])
            window.setInternalLoadingSource(source)
            window.volume_loaded(C_GuiFixtures().volume(source))
            window._finish_loading_ui()
            project, volume = window.getProject(), window.getVolume()
            project_path = window.requireProjectPath()
            saved_bytes = project_path.read_bytes()
            slice_index = window.getCurrentSlice()
            window.setInternalDirty(True)
            with (
                patch.object(
                    C_AnnotationProject, "save", side_effect=OSError("disk unavailable")
                ),
                patch.object(
                    QMessageBox, "critical", return_value=QMessageBox.StandardButton.Ok
                ) as notice,
            ):
                assert not window.unload_imported_image()
                notice.assert_called_once()
            assert window.getProject() is project
            assert window.getVolume() is volume
            assert window.getCurrentSource() is source
            assert window.getCurrentSlice() == slice_index
            assert window.getProjectPath() == project_path
            assert window.getInternalDirty()
            assert window.getSourceList().count() == 1
            assert len(window.getSources()) == 1
            assert window.getUnloadImageButton().isEnabled()
            assert window.getCanvas().getHost().scene().items()
            assert project_path.read_bytes() == saved_bytes
            assert window.isEnabled()
        finally:
            window.close()

    # 普通观察和外置预览都要释放三视图，外置预览仍遵守禁止写 JSON 的约束。
    @pytest.mark.parametrize("external", [False, True])
    def test_unload_clears_observation_and_external_preview(
        self, tmp_path: I_FilePath, external: bool
    ) -> None:
        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        volume = C_GuiFixtures().volume(source)
        window = C_Qt_AnnotationMainWindow(sources=[])
        try:
            window.add_sources([source.getPath()])
            window.setInternalLoadingSource(source)
            window.volume_loaded(volume)
            window._finish_loading_ui()
            window.add_polygon(C_PointList([(2.0, 2.0), (8.0, 2.0), (5.0, 8.0)]), "add")
            window.getShowInterpolation().setChecked(False)
            window.show()
            if external:
                assert window._begin_external_preview()
                window.setExternalMaskPath(tmp_path / "mask.nii")
                mask = np.ones(volume.getData().shape, dtype=np.uint8)
                window.external_mask_loaded(mask, np.ones(mask.shape[2], dtype=bool))
            else:
                window.getObserveRadio().setChecked(True)
            app.processEvents()
            assert window.getReadOnly()
            assert window.getUnloadImageButton().isEnabled()
            assert window.getObservationWindowCount() == 2
            assert all(
                view.getHost().isVisible() for view in window.iterObservationWindows()
            )
            project_path = window.requireProjectPath()
            saved = project_path.read_bytes()
            if external:
                with (
                    patch.object(
                        C_AnnotationProject,
                        "save",
                        side_effect=AssertionError("preview must not write JSON"),
                    ) as save,
                    patch.object(
                        QMessageBox,
                        "critical",
                        return_value=QMessageBox.StandardButton.Ok,
                    ),
                ):
                    assert window.unload_imported_image()
                    save.assert_not_called()
            else:
                assert window.unload_imported_image()
            app.processEvents()
            assert window.getVolume() is None
            assert not window.getReadOnly()
            assert not window.getExternalPreviewActive()
            assert window.getExternalMask() is None
            assert window.getExternalMaskPath() is None
            assert window.getInternalExternalViewState() is None
            assert window.getInternalObservationMask() is None
            assert window.getObservationPosition() == (0, 0, 0)
            assert window.getAddRadio().isChecked()
            assert not window.getCanvas().getReadOnly()
            assert not window.getShowInterpolation().isChecked()
            assert window.getCanvas().getInternalCrosshairPosition() is None
            assert not window.getUnloadExternalMaskButton().isEnabled()
            for view in window.iterObservationWindows():
                assert not view.getHost().isVisible()
                assert view.getCanvas().getHost().scene().items() == []
                assert view.getCanvas().getInternalCrosshairPosition() is None
                assert view.getSliceSpin().maximum() == 0
            if external:
                assert project_path.read_bytes() == saved
            else:
                assert C_ProjectRepository().load(project_path).getHasPolygons()
            window.add_sources([source.getPath()])
            assert window.getVolume() is None
            window.setInternalLoadingSource(source)
            window.volume_loaded(volume)
            window._finish_loading_ui()
            window.getObserveRadio().setChecked(True)
            app.processEvents()
            assert window.getReadOnly()
            assert window.getObservationWindowCount() == 2
            assert all(
                view.getHost().isVisible() for view in window.iterObservationWindows()
            )
            assert all(
                view.getCanvas().getHost().scene().items()
                for view in window.iterObservationWindows()
            )
        finally:
            window.close()

    # 用未启动的真实线程和状态标志验证并发保护，不依赖后台任务速度。
    @pytest.mark.parametrize("busy", ["volume", "external", "polygon", "annotation"])
    def test_busy_operations_reject_unloading(
        self, tmp_path: I_FilePath, busy: str
    ) -> None:
        C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        volume = C_GuiFixtures().volume(source)
        window = C_Qt_AnnotationMainWindow(sources=[])
        thread = None
        try:
            window.add_sources([source.getPath()])
            window.setInternalLoadingSource(source)
            window.volume_loaded(volume)
            window._finish_loading_ui()
            project = window.getProject()
            if busy == "volume":
                thread = C_Qt_VolumeLoadThread(source, 0.8)
                window.setLoadThread(thread)
            elif busy == "external":
                thread = C_Qt_ExternalMaskLoadThread(source.getPath(), volume, window)
                window.setExternalMaskThread(thread)
            elif busy == "polygon":
                window.setInternalClosingPolygon(True)
            else:
                window.setInternalSwitchingAnnotation(True)
            window._apply_mode_ui()
            assert not window.getUnloadImageButton().isEnabled()
            with patch.object(window, "save_project", return_value=True) as save:
                assert not window.unload_imported_image()
                save.assert_not_called()
            assert window.getCurrentSource() is source
            assert window.getVolume() is volume
            assert window.getProject() is project
            assert window.getSourceList().count() == 1
        finally:
            window.setLoadThread(None)
            window.setExternalMaskThread(None)
            window.setInternalClosingPolygon(False)
            window.setInternalSwitchingAnnotation(False)
            if thread is not None:
                thread.getHost().deleteLater()
            window.close()

    # 使用真实 NIfTI 后台加载验证卸载后不会自动打开其他项，手动操作仍正常。
    @pytest.mark.parametrize("target", ["remaining", "reimport"])
    def test_manual_loading_works_after_unload(
        self, tmp_path: I_FilePath, target: str
    ) -> None:
        app = C_GuiFixtures().app()
        paths = [tmp_path / "first.nii", tmp_path / "second.nii"]
        for path in paths:
            C_GuiFixtures().write_nifti(path)
        window = C_Qt_AnnotationMainWindow(sources=[])
        try:
            window.add_sources(paths)
            window.getSourceList().setCurrentRow(0)
            window.load_selected_source()
            assert not window.getUnloadImageButton().isEnabled()
            assert not window.unload_imported_image()
            deadline = monotonic() + 10.0
            while window.getLoadThread() is not None and monotonic() < deadline:
                QTest.qWait(10)
            assert window.getLoadThread() is None
            assert window.getInternalLoadError() is None
            assert window.requireCurrentSource().getPath() == paths[0]
            assert window.getUnloadImageButton().isEnabled()
            window.getUnloadImageButton().click()
            QTest.qWait(30)
            assert window.getVolume() is None
            assert window.getLoadThread() is None
            assert window.getSourceList().count() == 1
            if target == "reimport":
                window.add_sources([paths[0]])
                assert window.getVolume() is None
                window.getSourceList().setCurrentRow(1)
                expected = paths[0]
            else:
                window.getSourceList().setCurrentRow(0)
                expected = paths[1]
            window.getLoadButton().click()
            deadline = monotonic() + 10.0
            while window.getLoadThread() is not None and monotonic() < deadline:
                QTest.qWait(10)
            assert window.getLoadThread() is None
            assert window.getInternalLoadError() is None
            assert window.requireCurrentSource().getPath() == expected
            assert window.getVolume() is not None
            assert window.getUnloadImageButton().isEnabled()
            assert window.getCanvas().getHost().scene().items()
        finally:
            thread = window.getLoadThread()
            if thread is not None:
                thread.getHost().wait(10000)
                app.processEvents()
            window.close()
