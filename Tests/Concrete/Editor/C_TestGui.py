from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QRectF, QThread, QTimer, SignalInstance
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsPathItem,
    QGraphicsPixmapItem,
    QGraphicsPolygonItem,
    QGraphicsView,
    QGroupBox,
    QLabel,
    QListWidget,
    QMainWindow,
    QProgressDialog,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QSplitter,
    QToolBar,
    QWidget,
)
from pytest import MonkeyPatch

from med_image_seg.Abstract.Domain.Annotations import (
    I_MutableAnnotationProject,
)
from med_image_seg.Abstract.Domain.Geometry.I_PointList import I_PointList
from med_image_seg.Abstract.Presentation.Canvas import (
    T_MutableSliceCanvas,
    T_MutableVertexHandle,
)
from med_image_seg.Abstract.Presentation.Loading import (
    T_MutableExternalMaskLoadThread,
    T_MutableVolumeLoadThread,
)
from med_image_seg.Abstract.Presentation.Navigation import (
    T_MutableAnnotationIndexSpinBox,
    T_MutableMaskCoverageBar,
)
from med_image_seg.Abstract.Presentation.Observation import (
    T_MutableOrthogonalSliceWindow,
)

from ...Abstract.Editor.T_TestGui import T_TestGui

if TYPE_CHECKING:
    from med_image_seg.Abstract.Application.Projects import (
        I_MutableAnnotationExporter,
    )
    from med_image_seg.Abstract.Domain.Annotations.I_PolygonAnnotation import (
        I_PolygonAnnotation,
    )
    from med_image_seg.Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
    from med_image_seg.Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from med_image_seg.Abstract.Presentation.Window import (
        T_MutableAnnotationMainWindow,
    )
    from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath
import json
import time
from typing import final

import numpy as np
import pytest
import SimpleITK as sitk
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QKeyEvent, QShortcut
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox, QProgressBar


# 验证编辑、实时保存、导出及加载过程中的界面状态转换。
@final
class C_TestGui(T_TestGui[MonkeyPatch]):
    # 为当前测试类配置离屏 Qt 环境。
    @pytest.fixture(autouse=True, name="configure_environment")
    def _configure_environment_fixture(self) -> None:
        from ..Environment.C_TestEnvironment import C_TestEnvironment

        C_TestEnvironment().configure()

    # 复用或创建 QApplication，供测试驱动界面事件。
    def _app(self) -> QApplication:
        from .C_GuiFixtures import C_GuiFixtures

        return C_GuiFixtures().app()

    # 创建临时影像源，统一测试项目的配套文件路径和指纹。
    def _source(self, tmp_path: I_FilePath) -> I_ImageSource:
        from .C_GuiFixtures import C_GuiFixtures

        return C_GuiFixtures().source(tmp_path)

    # 构造与测试影像源对应的体素和几何信息。
    def _volume(self, source: I_ImageSource) -> I_MedicalVolume:
        from .C_GuiFixtures import C_GuiFixtures

        return C_GuiFixtures().volume(source)

    # 写入具有已知几何的 NIfTI 测试影像。
    def _write_nifti(self, path: I_FilePath) -> None:
        from .C_GuiFixtures import C_GuiFixtures

        return C_GuiFixtures().write_nifti(path)

    # 断言闭合计算期间编辑控件和快捷键均被禁用。
    def _assert_polygon_busy(
        self,
        window: T_MutableAnnotationMainWindow[
            QMainWindow,
            QTimer,
            QToolBar,
            QAction,
            QLabel,
            QPushButton,
            QComboBox,
            QSplitter,
            QListWidget,
            QDoubleSpinBox,
            QSlider,
            QSpinBox,
            QGroupBox,
            QRadioButton,
            QCheckBox,
            QProgressBar,
            QProgressDialog,
            QShortcut,
            QWidget,
            QButtonGroup,
            T_MutableSliceCanvas[
                QGraphicsView,
                QPointF,
                QRectF,
                QGraphicsPixmapItem,
                QGraphicsPathItem,
                QGraphicsPolygonItem,
                T_MutableVertexHandle[QGraphicsEllipseItem],
                SignalInstance,
            ],
            T_MutableOrthogonalSliceWindow[
                QWidget,
                QLabel,
                T_MutableSliceCanvas[
                    QGraphicsView,
                    QPointF,
                    QRectF,
                    QGraphicsPixmapItem,
                    QGraphicsPathItem,
                    QGraphicsPolygonItem,
                    T_MutableVertexHandle[QGraphicsEllipseItem],
                    SignalInstance,
                ],
                QSpinBox,
                SignalInstance,
            ],
            T_MutableAnnotationIndexSpinBox[QAbstractSpinBox, SignalInstance],
            T_MutableMaskCoverageBar[QWidget, QSlider],
            T_MutableVolumeLoadThread[QThread, SignalInstance],
            T_MutableExternalMaskLoadThread[QThread, SignalInstance],
            QPointF,
        ],
    ) -> None:
        from .C_GuiFixtures import C_GuiFixtures

        return C_GuiFixtures().assert_polygon_busy(window)

    # 验证无参数启动显示空影像列表，而不要求预先选择文件。
    def test_no_argument_window_starts_without_images(self) -> None:
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        window = C_Qt_AnnotationMainWindow(sources=[])
        app.processEvents()
        assert window.getSourceList().count() == 0
        assert window.getVolume() is None
        assert window.getLanguage() == "en"
        assert window.getFileButton().text() == "Import image files"
        assert all(not widget.isEnabled() for widget in window.iterEditorWidgets())
        assert not window.getExportAction().isEnabled()
        assert not window.getExportUbdAction().isEnabled()
        assert not window.getExportJsonAction().isEnabled()
        assert window.getAnnotationToolbar().actions() == [
            window.getExportAction(),
            window.getExportUbdAction(),
            window.getExportJsonAction(),
        ]
        window.close()

    # 切换中英语言，验证按钮和提示无需重启即可更新。
    def test_interface_language_can_switch_without_restart(self) -> None:
        from med_image_seg.Concrete.Localization.C_Localizer import C_Localizer
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        window = C_Qt_AnnotationMainWindow(sources=[])
        assert (
            window.getExportAction().text() == "Export interpolated 3D mask (.nii.gz)"
        )
        assert (
            window.getExportUbdAction().text()
            == "Export interpolated 3D mask (.ubd.npz)"
        )
        assert (
            window.getExportJsonAction().text()
            == "Export annotations (.med-image-seg.json)"
        )
        window.set_language("zh")
        app.processEvents()
        assert window.getLanguage() == "zh"
        assert window.getFileButton().text() == "导入影像文件"
        assert window.windowTitle() == "med-image-seg - 医疗影像多边形标注"
        assert window.getLanguageCombo().currentData() == "zh"
        assert window.getExportAction().text() == C_Localizer().translate(
            "export_mask", "zh"
        )
        assert window.getExportUbdAction().text() == C_Localizer().translate(
            "export_ubd_mask", "zh"
        )
        assert window.getExportJsonAction().text() == C_Localizer().translate(
            "export_annotations", "zh"
        )
        window.close()

    # 延迟影像加载，验证进度框可见且主界面被禁用。
    def test_loading_dialog_is_visible_and_main_ui_is_disabled(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[])
        window.setInternalLoadingSource(source)
        window.volume_loaded(C_GuiFixtures().volume(source))
        window._finish_loading_ui()
        assert window.getExportAction().isEnabled()
        assert window.getExportUbdAction().isEnabled()
        assert window.getExportJsonAction().isEnabled()
        window._show_loading(source)
        app.processEvents()
        assert window.getLoadingDialog() is not None
        assert window.requireLoadingDialog().isVisible()
        progress = window.requireLoadingDialog().findChild(QProgressBar)
        assert progress is not None and progress.isVisible()
        assert (progress.minimum(), progress.maximum()) == (0, 0)
        assert not window.requireCentralWidget().isEnabled()
        assert not window.getExportAction().isEnabled()
        assert not window.getExportUbdAction().isEnabled()
        assert not window.getExportJsonAction().isEnabled()
        window._finish_loading_ui()
        app.processEvents()
        assert window.requireCentralWidget().isEnabled()
        assert window.getExportAction().isEnabled()
        assert window.getExportUbdAction().isEnabled()
        assert window.getExportJsonAction().isEnabled()
        window.close()

    # 添加或修改轮廓，验证标注立即保存到影像旁的 JSON。
    def test_polygon_edits_save_immediately_next_to_image(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[])
        window.setInternalLoadingSource(source)
        window.volume_loaded(C_GuiFixtures().volume(source))
        window._finish_loading_ui()
        window.add_polygon(C_PointList([(2, 2), (8, 2), (5, 8)]), "add")
        window.update_polygon(0, C_PointList([(3, 3), (8, 2), (5, 8)]))
        app.processEvents()
        assert source.getAnnotationPath().is_file()
        assert C_FilePath(f"{source.getAnnotationPath()}.bak").is_file()
        payload = json.loads(source.getAnnotationPath().read_text(encoding="utf-8"))
        current = str(window.getCurrentSlice())
        assert payload["slices"][current]["polygons"][0]["points"][0] == [3.0, 3.0]
        window.delete_last_edited_polygon()
        payload = json.loads(source.getAnnotationPath().read_text(encoding="utf-8"))
        assert current not in payload["slices"]
        window.close()

    # 延迟保存和刷新，验证闭合流程结束前界面一直不可操作。
    @pytest.mark.parametrize("trigger", ["space", "button", "right", "double"])
    def test_polygon_closure_disables_ui_until_save_and_refresh_finish(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch, trigger: str
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_AnnotationProject import (
            C_AnnotationProject,
        )
        from med_image_seg.Concrete.Domain.Geometry.C_Point2D import C_Point2D
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )
        from med_image_seg.Concrete.Storage.Projects.C_ProjectRepository import (
            C_ProjectRepository,
        )

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[])
        window.setInternalLoadingSource(source)
        window.volume_loaded(C_GuiFixtures().volume(source))
        window._finish_loading_ui()
        window.show()
        window.activateWindow()
        window.getCanvas().getHost().setFocus()
        app.processEvents()
        points = [(2.0, 2.0), (8.0, 2.0), (5.0, 8.0)]
        window.getCanvas().setDraftPoints(
            C_PointList([C_Point2D(*point) for point in points])
        )
        window.getCanvas()._update_draft()
        slice_index = window.getCurrentSlice()
        previous_message = window.statusBar().currentMessage()
        stages: list[str] = []
        add_polygon = C_AnnotationProject.add_polygon
        save = C_AnnotationProject.save
        refresh_slice = window.refresh_slice

        # 检查闭合期间界面锁定，再执行原轮廓添加并记录阶段。
        def record_add(
            self: I_MutableAnnotationProject, index: int, polygon: I_PolygonAnnotation
        ) -> None:
            assert isinstance(self, C_AnnotationProject)
            C_GuiFixtures().assert_polygon_busy(window)
            stages.append("annotation")
            add_polygon(self, index, polygon)

        # 记录保存调用和路径，必要时检查闭合期间界面仍处于锁定状态。
        def record_save(
            self: I_MutableAnnotationProject, path: I_FilePath
        ) -> I_FilePath:
            assert isinstance(self, C_AnnotationProject)
            C_GuiFixtures().assert_polygon_busy(window)
            stages.append("save")
            window.add_polygon(C_PointList(points), "add")
            window.getCanvas().finish_polygon()
            window.autosave_if_needed()
            assert not window.close()
            for event_type in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease):
                QApplication.postEvent(
                    window,
                    QKeyEvent(
                        event_type, Qt.Key.Key_Right, Qt.KeyboardModifier.NoModifier
                    ),
                )
            return save(self, path)

        # 检查刷新阶段界面仍被锁定，并记录刷新执行顺序。
        def record_refresh() -> None:
            C_GuiFixtures().assert_polygon_busy(window)
            stages.append("refresh")
            refresh_slice()

        try:
            with monkeypatch.context() as patch:
                patch.setattr(C_AnnotationProject, "add_polygon", record_add)
                patch.setattr(C_AnnotationProject, "save", record_save)
                patch.setattr(window, "refresh_slice", record_refresh)
                if trigger == "space":
                    QTest.keyClick(
                        window.getCanvas().getHost().viewport(), Qt.Key.Key_Space
                    )
                elif trigger == "button":
                    window.getFinishButton().click()
                elif trigger == "right":
                    QTest.mouseClick(
                        window.getCanvas().getHost().viewport(),
                        Qt.MouseButton.RightButton,
                    )
                else:
                    QTest.mouseDClick(
                        window.getCanvas().getHost().viewport(),
                        Qt.MouseButton.LeftButton,
                    )
                app.processEvents()
            assert stages == ["annotation", "save", "refresh"]
            assert window.isEnabled()
            assert window.requireCentralWidget().isEnabled()
            assert window.getCanvas().getHost().isEnabled()
            assert window.getAnnotationToolbar().isEnabled()
            assert all(
                action.isEnabled() for action in window.getAnnotationToolbar().actions()
            )
            assert all(
                shortcut.isEnabled() for shortcut in window.findChildren(QShortcut)
            )
            assert window.getAutosaveTimer().isActive()
            assert not window.getInternalClosingPolygon()
            assert not window.getInternalDirty()
            assert window.statusBar().currentMessage() == previous_message
            assert QApplication.overrideCursor() is None
            assert window.getCurrentSlice() == slice_index
            assert not window.getCanvas().getDraftPointCount()
            assert window.getCanvas().getPolygonItemCount() == 1
            loaded = C_ProjectRepository().load(source.getAnnotationPath())
            assert loaded.annotation(slice_index).getPolygonCount() == 1
        finally:
            window.close()

    # 模拟闭合期间失败，核验控件和快捷键恢复原启用状态。
    @pytest.mark.parametrize("failed_step", ["annotation", "save", "refresh"])
    @pytest.mark.parametrize("initially_enabled", [False, True])
    def test_polygon_closure_restores_previous_ui_state_after_failure(
        self,
        tmp_path: I_FilePath,
        monkeypatch: MonkeyPatch,
        failed_step: str,
        initially_enabled: bool,
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_AnnotationProject import (
            C_AnnotationProject,
        )
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[])
        window.setInternalLoadingSource(source)
        window.volume_loaded(C_GuiFixtures().volume(source))
        window._finish_loading_ui()
        window.getFileButton().setEnabled(False)
        window.getExportJsonAction().setEnabled(False)
        shortcuts = window.findChildren(QShortcut)
        shortcuts[0].setEnabled(False)
        window.getAutosaveTimer().stop()
        window.setEnabled(initially_enabled)
        window.statusBar().showMessage("previous status")
        QApplication.setOverrideCursor(Qt.CursorShape.CrossCursor)

        # 在确认界面已锁定后模拟轮廓添加失败。
        def fail_annotation(
            self: I_MutableAnnotationProject, index: int, polygon: I_PolygonAnnotation
        ) -> None:
            C_GuiFixtures().assert_polygon_busy(window)
            raise RuntimeError("simulated polygon failure")

        # 模拟 JSON 保存失败，检查错误路径和界面状态恢复。
        def fail_save(self: I_MutableAnnotationProject, path: I_FilePath) -> I_FilePath:
            C_GuiFixtures().assert_polygon_busy(window)
            raise OSError("simulated JSON save failure")

        # 在确认界面已锁定后模拟刷新失败。
        def fail_refresh() -> None:
            C_GuiFixtures().assert_polygon_busy(window)
            raise RuntimeError("simulated polygon failure")

        try:
            with monkeypatch.context() as patch:
                if failed_step == "annotation":
                    patch.setattr(C_AnnotationProject, "add_polygon", fail_annotation)
                elif failed_step == "save":
                    patch.setattr(C_AnnotationProject, "save", fail_save)
                else:
                    patch.setattr(window, "refresh_slice", fail_refresh)
                if failed_step == "save":
                    window.add_polygon(C_PointList([(2, 2), (8, 2), (5, 8)]), "add")
                    assert window.getInternalDirty()
                    assert (
                        "simulated JSON save failure"
                        in window.getAutosaveStatus().text()
                    )
                else:
                    with pytest.raises(RuntimeError, match="simulated polygon failure"):
                        window.add_polygon(C_PointList([(2, 2), (8, 2), (5, 8)]), "add")
                app.processEvents()
            assert window.isEnabled() is initially_enabled
            assert not window.getFileButton().isEnabled()
            assert not window.getExportJsonAction().isEnabled()
            assert not shortcuts[0].isEnabled()
            assert all(shortcut.isEnabled() for shortcut in shortcuts[1:])
            assert not window.getAutosaveTimer().isActive()
            assert not window.getInternalClosingPolygon()
            assert window.statusBar().currentMessage() == "previous status"
            cursor = QApplication.overrideCursor()
            assert cursor is not None
            assert cursor.shape() == Qt.CursorShape.CrossCursor
        finally:
            QApplication.restoreOverrideCursor()
            window.close()

    # 验证不足三个顶点的草稿不会触发闭合计算和忙碌锁定。
    @pytest.mark.parametrize("point_count", [0, 1, 2])
    def test_incomplete_polygon_does_not_enter_busy_state(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch, point_count: int
    ) -> None:
        from med_image_seg.Concrete.Domain.Geometry.C_Point2D import C_Point2D
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[])
        window.setInternalLoadingSource(source)
        window.volume_loaded(C_GuiFixtures().volume(source))
        window._finish_loading_ui()
        window.getCanvas().setDraftPoints(
            C_PointList([C_Point2D(index, index) for index in range(point_count)])
        )
        previous_json = source.getAnnotationPath().read_bytes()

        # 拦截不完整草稿触发的忙碌状态，调用即判定测试失败。
        def unexpected_busy_state() -> None:
            pytest.fail("an incomplete polygon must not enter the busy state")

        monkeypatch.setattr(window, "_polygon_busy_ui", unexpected_busy_state)
        try:
            window.getCanvas().finish_polygon()
            app.processEvents()
            assert window.isEnabled()
            assert not window.getInternalClosingPolygon()
            assert window.getCanvas().getDraftPointCount() == point_count
            assert source.getAnnotationPath().read_bytes() == previous_json
            assert QApplication.overrideCursor() is None
        finally:
            window.close()

    # 选择自定义路径导出掩码，核验格式、插值内容和中英保存对话框。
    @pytest.mark.parametrize("suffix", [".nii.gz", ".ubd.npz"])
    @pytest.mark.parametrize("with_suffix", [False, True])
    @pytest.mark.parametrize("language", ["en", "zh"])
    def test_export_toolbar_actions_write_interpolated_masks(
        self,
        tmp_path: I_FilePath,
        monkeypatch: MonkeyPatch,
        suffix: str,
        with_suffix: bool,
        language: str,
    ) -> None:
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Localization.C_Localizer import C_Localizer
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        volume = C_GuiFixtures().volume(source)
        window = C_Qt_AnnotationMainWindow(sources=[], language=language)
        window.setInternalLoadingSource(source)
        window.volume_loaded(volume)
        window._finish_loading_ui()
        messages: list[str] = []
        output = tmp_path / "另存目录" / f"自定义掩码{suffix}"
        selected = output if with_suffix else output.with_name("自定义掩码")
        dialog_calls: list[tuple[str, str, str]] = []

        # 替代原生保存对话框，记录默认路径与译文并返回用户选择的名称。
        def select_export(
            _parent: QWidget, title: str, directory: str, file_filter: str
        ) -> tuple[str, str]:
            dialog_calls.append((title, directory, file_filter))
            return str(selected), ""

        monkeypatch.setattr(QFileDialog, "getSaveFileName", select_export)
        monkeypatch.setattr(
            QMessageBox,
            "information",
            lambda _parent, _title, message: messages.append(message),
        )
        monkeypatch.setattr(
            QMessageBox,
            "critical",
            lambda _parent, _title, message: pytest.fail(message),
        )
        try:
            for slice_index in (1, 3):
                window.set_slice(slice_index)
                window.add_polygon(C_PointList([(2, 2), (8, 2), (5, 8)]), "add")
            assert window.getProject() is not None
            expected = window.requireProject().to_mask(interpolate=True)
            assert expected[:, :, 2].any()
            if suffix == ".ubd.npz":
                window.getExportUbdAction().trigger()
                expected_default = source.getUbdMaskPath()
                title_key = "export_ubd_dialog_title"
                filter_key = "export_ubd_filter"
                with np.load(output, allow_pickle=False) as archive:
                    assert archive["image_type"].item() == "mask"
                    assert archive["mmpd"].item() == volume.getSpacingMm()[0]
                    written = archive["body_data"]
            else:
                window.getExportAction().trigger()
                expected_default = source.getMaskPath()
                title_key = "export_mask_dialog_title"
                filter_key = "export_mask_filter"
                verification = tmp_path / "verification.nii.gz"
                verification.write_bytes(output.read_bytes())
                image = sitk.ReadImage(str(verification))
                written = np.transpose(sitk.GetArrayFromImage(image), (2, 1, 0))
            app.processEvents()
            assert dialog_calls == [
                (
                    C_Localizer().translate(title_key, language),
                    str(expected_default),
                    C_Localizer().translate(filter_key, language),
                )
            ]
            np.testing.assert_array_equal(written, expected)
            assert not source.getMaskPath().exists()
            assert not source.getUbdMaskPath().exists()
            assert source.getAnnotationPath().is_file()
            assert len(messages) == 1
            assert str(output) in messages[0]
            assert QApplication.overrideCursor() is None
        finally:
            window.close()

    # 模拟 UBD 导出失败，验证没有错误的成功提示。
    @pytest.mark.parametrize("failed_step", ["save", "export"])
    def test_ubd_export_handles_failures_without_success_message(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch, failed_step: str
    ) -> None:
        from med_image_seg.Concrete.Application.Projects import (
            C_AnnotationExporter,
        )
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[])
        window.setInternalLoadingSource(source)
        window.volume_loaded(C_GuiFixtures().volume(source))
        window._finish_loading_ui()
        errors: list[Exception] = []

        # 模拟掩码导出失败，并防止原项目保存失败后继续导出。
        def fail_export(
            self: I_MutableAnnotationExporter,
            project: I_MutableAnnotationProject,
            volume: I_MedicalVolume,
            output_path: I_FilePath,
            *,
            interpolate: bool,
        ) -> I_FilePath:
            if failed_step == "save":
                pytest.fail("export must not run when saving fails")
            raise OSError("simulated UBD export failure")

        try:
            with monkeypatch.context() as patch:
                patch.setattr(
                    QFileDialog,
                    "getSaveFileName",
                    lambda *_args: (str(tmp_path / "export.ubd.npz"), ""),
                )
                patch.setattr(C_AnnotationExporter, "export", fail_export)
                if failed_step == "save":
                    patch.setattr(window, "save_project", lambda *, notify: False)
                patch.setattr(
                    QMessageBox,
                    "critical",
                    lambda _parent, _title, message: errors.append(message),
                )
                patch.setattr(
                    QMessageBox,
                    "information",
                    lambda *_args: pytest.fail("failed export must not report success"),
                )
                window.getExportUbdAction().trigger()
                app.processEvents()
                assert not source.getUbdMaskPath().exists()
                assert errors == (
                    ["simulated UBD export failure"] if failed_step == "export" else []
                )
                assert QApplication.overrideCursor() is None
        finally:
            window.close()

    # 另存 JSON 到选定目录，保留原自动保存路径及全部标注信息。
    @pytest.mark.parametrize("suffix", [".dcm", ".nii", ".nii.gz", ".ubd.npz"])
    @pytest.mark.parametrize("file_state", ["saved", "missing", "pending"])
    @pytest.mark.parametrize("with_annotation_suffix", [False, True])
    def test_json_export_saves_annotation_project_to_selected_path(
        self,
        tmp_path: I_FilePath,
        monkeypatch: MonkeyPatch,
        suffix: str,
        file_state: str,
        with_annotation_suffix: bool,
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_AnnotationProject import (
            C_AnnotationProject,
        )
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Localization.C_Localizer import C_Localizer
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath
        from med_image_seg.Concrete.Storage.Projects.C_ProjectRepository import (
            C_ProjectRepository,
        )
        from med_image_seg.Concrete.Storage.Volumes.C_ImageSourceFactory import (
            C_ImageSourceFactory,
        )

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        directory = tmp_path / "中文目录"
        directory.mkdir()
        image = directory / f"病例{suffix}"
        image.write_bytes(b"synthetic-image")
        source = C_ImageSourceFactory().from_path(image)
        volume = C_GuiFixtures().volume(source)
        window = C_Qt_AnnotationMainWindow(sources=[])
        window.setInternalLoadingSource(source)
        window.volume_loaded(volume)
        window._finish_loading_ui()
        messages: list[str] = []
        saved_paths: list[I_FilePath] = []
        save = C_AnnotationProject.save
        output = tmp_path / "另存目录" / "自定义标注.med-image-seg.json"
        selected = output if with_annotation_suffix else output.with_name("自定义标注")
        monkeypatch.setattr(
            QFileDialog, "getSaveFileName", lambda *_args: (str(selected), "")
        )

        # 记录自动保存与另存副本的目标，确认导出没有重定向项目。
        def record_save(
            self: I_MutableAnnotationProject,
            path: I_FilePath,
            *,
            delete_if_empty: bool = False,
        ) -> I_FilePath:
            assert isinstance(self, C_AnnotationProject)
            saved_paths.append(C_FilePath(path))
            return save(self, path, delete_if_empty=delete_if_empty)

        try:
            for slice_index in (1, 3):
                window.set_slice(slice_index)
                window.add_polygon(C_PointList([(2, 2), (8, 2), (5, 8)]), "add")
            window.set_slice_completed(True)
            window.set_slice(4)
            window.set_force_empty(True)
            assert window.getProject() is not None
            assert not window.getInternalDirty()
            previous_json = source.getAnnotationPath().read_bytes()
            if file_state == "missing":
                source.getAnnotationPath().unlink()
            elif file_state == "pending":
                window.requireProject().add_polygon(
                    0,
                    C_PolygonAnnotation(
                        points=((3, 3), (9, 3), (6, 9)), source="prototype"
                    ),
                )
                window.setInternalDirty(True)
            monkeypatch.setattr(C_AnnotationProject, "save", record_save)
            monkeypatch.setattr(
                QMessageBox,
                "information",
                lambda _parent, _title, message: messages.append(message),
            )
            monkeypatch.setattr(
                QMessageBox,
                "critical",
                lambda _parent, _title, message: pytest.fail(message),
            )
            window.getExportJsonAction().trigger()
            app.processEvents()
            loaded = C_ProjectRepository().load(output)
            loaded.validate_volume(volume)
            assert loaded.getImageId() == window.requireProject().getImageId()
            assert (
                loaded.getSourceFingerprint()
                == window.requireProject().getSourceFingerprint()
            )
            assert loaded.getEditCounter() == window.requireProject().getEditCounter()
            assert loaded.getMetadata() == window.requireProject().getMetadata()
            for slice_index in range(volume.getData().shape[2]):
                assert loaded.annotation(
                    slice_index
                ) == window.requireProject().annotation(slice_index)
            np.testing.assert_array_equal(
                loaded.to_mask(), window.requireProject().to_mask()
            )
            assert saved_paths == [source.getAnnotationPath(), output]
            assert window.getProjectPath() == source.getAnnotationPath()
            assert not window.getInternalDirty()
            assert not source.getMaskPath().exists()
            assert not source.getUbdMaskPath().exists()
            if file_state != "missing":
                assert (
                    C_FilePath(f"{source.getAnnotationPath()}.bak").read_bytes()
                    == previous_json
                )
            assert len(messages) == 1
            assert messages[0] == C_Localizer().translate(
                "export_annotations_complete_message",
                path=str(output),
            )
            assert QApplication.overrideCursor() is None
        finally:
            window.close()

    # 模拟 JSON 写盘失败，核验只报告错误而不提示导出成功。
    @pytest.mark.parametrize("dirty", [False, True])
    def test_json_export_reports_save_failure_without_success(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch, dirty: bool
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_AnnotationProject import (
            C_AnnotationProject,
        )
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[])
        window.setInternalLoadingSource(source)
        window.volume_loaded(C_GuiFixtures().volume(source))
        window._finish_loading_ui()
        errors: list[Exception] = []
        previous_json = source.getAnnotationPath().read_bytes()
        window.setInternalDirty(dirty)

        # 模拟 JSON 保存失败，检查错误路径和界面状态恢复。
        def fail_save(self: I_MutableAnnotationProject, path: I_FilePath) -> I_FilePath:
            raise OSError("simulated JSON export failure")

        try:
            with monkeypatch.context() as patch:
                patch.setattr(
                    QFileDialog,
                    "getSaveFileName",
                    lambda *_args: (str(tmp_path / "export.med-image-seg.json"), ""),
                )
                patch.setattr(C_AnnotationProject, "save", fail_save)
                patch.setattr(
                    QMessageBox,
                    "critical",
                    lambda _parent, _title, message: errors.append(message),
                )
                patch.setattr(
                    QMessageBox,
                    "information",
                    lambda *_args: pytest.fail("failed export must not report success"),
                )
                window.getExportJsonAction().trigger()
                app.processEvents()
                assert errors == ["simulated JSON export failure"]
                assert window.getInternalDirty() is dirty
                assert source.getAnnotationPath().read_bytes() == previous_json
                assert QApplication.overrideCursor() is None
        finally:
            window.close()

    # 验证没有当前项目时不产生误导性的导出成功提示。
    def test_json_export_without_project_does_not_report_success(
        self, monkeypatch: MonkeyPatch
    ) -> None:
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        window = C_Qt_AnnotationMainWindow(sources=[])
        monkeypatch.setattr(
            QMessageBox,
            "information",
            lambda *_args: pytest.fail("no project must not report export success"),
        )
        monkeypatch.setattr(
            QFileDialog,
            "getSaveFileName",
            lambda *_args: pytest.fail("no project must not open a save dialog"),
        )
        try:
            window.export_annotations()
            app.processEvents()
            assert not window.getExportJsonAction().isEnabled()
        finally:
            window.close()

    # 取消另存为时禁止三个导出动作保存项目、创建文件或提示成功。
    @pytest.mark.parametrize("suffix", [".nii.gz", ".ubd.npz", ".med-image-seg.json"])
    def test_cancel_export_dialog_does_not_write_files(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch, suffix: str
    ) -> None:
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[])
        window.setInternalLoadingSource(source)
        window.volume_loaded(C_GuiFixtures().volume(source))
        window._finish_loading_ui()
        window.setInternalDirty(True)
        previous_json = source.getAnnotationPath().read_bytes()
        previous_status = window.getAutosaveStatus().text()
        try:
            with monkeypatch.context() as patch:
                patch.setattr(QFileDialog, "getSaveFileName", lambda *_args: ("", ""))
                patch.setattr(
                    window,
                    "save_project",
                    lambda **_kwargs: pytest.fail("cancel must not save the project"),
                )
                patch.setattr(
                    QMessageBox,
                    "information",
                    lambda *_args: pytest.fail("cancel must not report success"),
                )
                patch.setattr(
                    QMessageBox,
                    "critical",
                    lambda *_args: pytest.fail("cancel must not report failure"),
                )
                if suffix == ".nii.gz":
                    window.getExportAction().trigger()
                elif suffix == ".ubd.npz":
                    window.getExportUbdAction().trigger()
                else:
                    window.getExportJsonAction().trigger()
                app.processEvents()
                assert source.getAnnotationPath().read_bytes() == previous_json
                assert window.getAutosaveStatus().text() == previous_status
                assert window.getInternalDirty()
                assert window.getProjectPath() == source.getAnnotationPath()
                assert not source.getMaskPath().exists()
                assert not source.getUbdMaskPath().exists()
                assert QApplication.overrideCursor() is None
        finally:
            window.close()

    # 补齐扩展名后目标已存在时，必须再次确认覆盖而不是静默替换。
    @pytest.mark.parametrize("suffix", [".nii.gz", ".ubd.npz", ".med-image-seg.json"])
    @pytest.mark.parametrize("overwrite", [False, True])
    def test_export_confirms_overwrite_after_completing_suffix(
        self,
        tmp_path: I_FilePath,
        monkeypatch: MonkeyPatch,
        suffix: str,
        overwrite: bool,
    ) -> None:
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[])
        window.setInternalLoadingSource(source)
        window.volume_loaded(C_GuiFixtures().volume(source))
        window._finish_loading_ui()
        output = tmp_path / f"自定义导出{suffix}"
        output.write_bytes(b"existing-export")
        previous_json = source.getAnnotationPath().read_bytes()
        confirmations: list[str] = []
        messages: list[str] = []

        # 拦截补后缀的覆盖确认，保留按钮默认值并模拟用户决定。
        def confirm_overwrite(
            _parent: QWidget,
            _title: str,
            message: str,
            _buttons: QMessageBox.StandardButton,
            default_button: QMessageBox.StandardButton,
        ) -> QMessageBox.StandardButton:
            assert default_button == QMessageBox.StandardButton.No
            confirmations.append(message)
            return (
                QMessageBox.StandardButton.Yes
                if overwrite
                else QMessageBox.StandardButton.No
            )

        monkeypatch.setattr(
            QFileDialog,
            "getSaveFileName",
            lambda *_args: (str(tmp_path / "自定义导出"), ""),
        )
        monkeypatch.setattr(QMessageBox, "question", confirm_overwrite)
        monkeypatch.setattr(
            QMessageBox,
            "information",
            lambda _parent, _title, message: messages.append(message),
        )
        monkeypatch.setattr(
            QMessageBox,
            "critical",
            lambda _parent, _title, message: pytest.fail(message),
        )
        try:
            if suffix == ".nii.gz":
                window.getExportAction().trigger()
            elif suffix == ".ubd.npz":
                window.getExportUbdAction().trigger()
            else:
                window.getExportJsonAction().trigger()
            app.processEvents()
            assert len(confirmations) == 1
            assert str(output) in confirmations[0]
            assert len(messages) == int(overwrite)
            if overwrite:
                assert output.read_bytes() != b"existing-export"
                assert str(output) in messages[0]
            else:
                assert output.read_bytes() == b"existing-export"
                assert source.getAnnotationPath().read_bytes() == previous_json
            assert window.getProjectPath() == source.getAnnotationPath()
            assert not source.getMaskPath().exists()
            assert not source.getUbdMaskPath().exists()
            assert QApplication.overrideCursor() is None
        finally:
            window.close()

    # 区分自动保存和另存文件失败，核验导出失败不会切换当前项目路径。
    def test_json_export_reports_selected_path_write_failure(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_AnnotationProject import (
            C_AnnotationProject,
        )
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[])
        window.setInternalLoadingSource(source)
        window.volume_loaded(C_GuiFixtures().volume(source))
        window._finish_loading_ui()
        window.setInternalDirty(True)
        output = tmp_path / "export.med-image-seg.json"
        errors: list[str] = []
        save = C_AnnotationProject.save

        # 允许原项目自动保存，仅让用户选择的导出副本写入失败。
        def fail_selected_save(
            self: I_MutableAnnotationProject,
            path: I_FilePath,
            *,
            delete_if_empty: bool = False,
        ) -> I_FilePath:
            assert isinstance(self, C_AnnotationProject)
            if path == output:
                raise OSError("selected export path is not writable")
            return save(self, path, delete_if_empty=delete_if_empty)

        try:
            with monkeypatch.context() as patch:
                patch.setattr(C_AnnotationProject, "save", fail_selected_save)
                patch.setattr(
                    QFileDialog, "getSaveFileName", lambda *_args: (str(output), "")
                )
                patch.setattr(
                    QMessageBox,
                    "critical",
                    lambda _parent, _title, message: errors.append(message),
                )
                patch.setattr(
                    QMessageBox,
                    "information",
                    lambda *_args: pytest.fail("failed export must not report success"),
                )
                window.getExportJsonAction().trigger()
                app.processEvents()
                assert errors == ["selected export path is not writable"]
                assert window.getProjectPath() == source.getAnnotationPath()
                assert source.getAnnotationPath().is_file()
                assert not output.exists()
                assert not window.getInternalDirty()
                assert QApplication.overrideCursor() is None
        finally:
            window.close()

    # 保留已有 JSON 的任意合法文件名，导出后继续在原文件自动保存编辑。
    def test_json_export_preserves_name_and_original_autosave(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch
    ) -> None:
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )
        from med_image_seg.Concrete.Storage.Projects.C_ProjectRepository import (
            C_ProjectRepository,
        )

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[])
        window.setInternalLoadingSource(source)
        window.volume_loaded(C_GuiFixtures().volume(source))
        window._finish_loading_ui()
        output = tmp_path / "自定义名称.json"
        monkeypatch.setattr(
            QFileDialog, "getSaveFileName", lambda *_args: (str(output), "")
        )
        monkeypatch.setattr(QMessageBox, "information", lambda *_args: None)
        monkeypatch.setattr(
            QMessageBox,
            "critical",
            lambda _parent, _title, message: pytest.fail(message),
        )
        try:
            window.getExportJsonAction().trigger()
            app.processEvents()
            assert output.is_file()
            assert not output.with_name("自定义名称.json.med-image-seg.json").exists()
            exported = output.read_bytes()
            window.set_slice(1)
            window.add_polygon(C_PointList([(2, 2), (8, 2), (5, 8)]), "add")
            assert window.getProjectPath() == source.getAnnotationPath()
            saved = C_ProjectRepository().load(source.getAnnotationPath())
            assert saved.annotation(1).getPolygonCount() == 1
            assert output.read_bytes() == exported
            assert not window.getInternalDirty()
        finally:
            window.close()

    # 验证画布按项查询不暴露列表，返回点的修改不会影响内部坐标。
    def test_canvas_collection_queries_protect_internal_state(self) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Presentation.Canvas.C_Qt_SliceCanvas import (
            C_Qt_SliceCanvas,
        )

        app = self._app()
        canvas = C_Qt_SliceCanvas()
        try:
            canvas.set_slice(
                np.zeros((100, 100), dtype=np.uint8),
                (C_PolygonAnnotation(((20, 20), (80, 20), (50, 80))),),
            )
            canvas.setDraftPoints(C_PointList(((10.0, 15.0), (25.0, 30.0))))
            assert canvas.getDraftPointCount() == 2
            assert canvas.getPolygonItemCount() == 1
            assert canvas.getPolygonPointCount(0) == 3
            assert canvas.getHandleCount() == 3
            assert canvas.getPolygonItem(0).scene() is canvas.scene()
            assert canvas.getHandle(0).getPolygonIndex() == 0

            draft_point = canvas.getDraftPoint(0)
            draft_point.setX(99.0)
            assert canvas.getDraftPoint(0) == QPointF(10.0, 15.0)
            polygon_point = canvas.getPolygonPoint(0, 0)
            polygon_point.setY(99.0)
            assert canvas.getPolygonPoint(0, 0) == QPointF(20.0, 20.0)
            for old_name in (
                "getInternalDraftPoints",
                "getInternalPolygonItems",
                "getInternalPolygonPoints",
                "getInternalHandles",
            ):
                assert not hasattr(canvas, old_name)
            with pytest.raises(IndexError):
                canvas.getDraftPoint(2)
            with pytest.raises(IndexError):
                canvas.getPolygonItem(1)
            with pytest.raises(IndexError):
                canvas.getPolygonPoint(0, 3)
            with pytest.raises(IndexError):
                canvas.getHandle(3)
            canvas.cancel_polygon()
            assert canvas.getDraftPointCount() == 0
            assert canvas.getPolygonPointCount(0) == 3
            app.processEvents()
        finally:
            canvas.close()

    # 验证首个草稿点以不可编辑的黄色圆点显示，避免零长度路径不可见。
    def test_first_draft_point_displays_yellow_position_marker(self) -> None:
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Presentation.Canvas.C_Qt_SliceCanvas import (
            C_Qt_SliceCanvas,
        )

        app = self._app()
        canvas = C_Qt_SliceCanvas()
        try:
            canvas.setDraftPoints(C_PointList(((23.0, 31.0),)))
            canvas._update_draft()

            draft_item = canvas.requireInternalDraftItem()
            child_items = draft_item.childItems()
            assert len(child_items) == 1
            marker = child_items[0]
            assert isinstance(marker, QGraphicsEllipseItem)
            assert marker.pos() == QPointF(23.0, 31.0)
            assert marker.rect() == QRectF(-3.5, -3.5, 7.0, 7.0)
            assert marker.brush().color().name() == "#ffd166"
            assert marker.flags() & (
                QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations
            )
            assert not marker.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            assert not marker.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            app.processEvents()
        finally:
            canvas.close()

    # 模拟顶点拖动，验证坐标更新并提交多边形变更信号。
    def test_canvas_vertex_handle_can_be_dragged(self) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )
        from med_image_seg.Concrete.Presentation.Canvas.C_Qt_SliceCanvas import (
            C_Qt_SliceCanvas,
        )

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        canvas = C_Qt_SliceCanvas()
        canvas.resize(420, 420)
        canvas.show()
        canvas.set_slice(
            np.zeros((100, 100), dtype=np.uint8),
            [C_PolygonAnnotation(points=((20, 20), (80, 20), (50, 80)))],
        )
        app.processEvents()
        changes: list[tuple[int, I_PointList]] = []
        canvas.polygon_changed.connect(
            lambda index, points: changes.append((index, points))
        )
        start = canvas.mapFromScene(QPointF(20, 20))
        destination = canvas.mapFromScene(QPointF(30, 35))
        QTest.mousePress(canvas.viewport(), Qt.MouseButton.LeftButton, pos=start)
        QTest.mouseMove(canvas.viewport(), destination, delay=10)
        QTest.mouseRelease(
            canvas.viewport(), Qt.MouseButton.LeftButton, pos=destination, delay=10
        )
        app.processEvents()
        assert changes
        assert changes[0][0] == 0
        assert np.allclose(
            (changes[0][1].getPoint(0).getX(), changes[0][1].getPoint(0).getY()),
            (30.0, 35.0),
            atol=1.0,
        )
        canvas.close()

    # 验证初始 NIfTI 在后台加载，并按默认策略建立标注文件。
    def test_initial_nifti_loads_in_background_and_creates_json(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )
        from med_image_seg.Concrete.Storage.Volumes.C_ImageSourceFactory import (
            C_ImageSourceFactory,
        )

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        image_path = tmp_path / "real.nii.gz"
        C_GuiFixtures().write_nifti(image_path)
        source = C_ImageSourceFactory().from_path(image_path)
        window = C_Qt_AnnotationMainWindow(sources=[source], spacing_mm=1.0)
        window.show()
        deadline = time.monotonic() + 20.0
        while time.monotonic() < deadline:
            app.processEvents()
            if window.getCurrentSource() == source and window.getLoadThread() is None:
                break
            time.sleep(0.01)
        assert window.getCurrentSource() == source
        assert window.getVolume() is not None
        assert source.getAnnotationPath().is_file()
        assert window.getLoadingDialog() is None
        assert window.requireCentralWidget().isEnabled()
        window.close()

    # 启动时载入已有影像，验证程序采用标注保存的网格而不是当前界面间距。
    def test_initial_image_automatically_loads_existing_json(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Application.Projects.C_ProjectFactory import (
            C_ProjectFactory,
        )
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )
        from med_image_seg.Concrete.Storage.Volumes.C_ImageSourceFactory import (
            C_ImageSourceFactory,
        )
        from med_image_seg.Concrete.Storage.Volumes.C_MedicalVolumeReader import (
            C_MedicalVolumeReader,
        )

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        image_path = tmp_path / "annotated.nii.gz"
        C_GuiFixtures().write_nifti(image_path)
        source = C_ImageSourceFactory().from_path(image_path)
        volume = C_MedicalVolumeReader(1.0).read(source.getPath())
        project = C_ProjectFactory().create(
            image_id=source.getSourceId(),
            source_fingerprint=source.getFingerprint(),
            volume=volume,
        )
        project.add_polygon(
            3,
            C_PolygonAnnotation(
                points=((2, 2), (10, 2), (10, 8), (2, 8)), source="prototype"
            ),
        )
        project.save(source.getAnnotationPath())
        requested_volume = C_MedicalVolumeReader(0.8).read(source.getPath())
        assert requested_volume.getData().shape != volume.getData().shape
        window = C_Qt_AnnotationMainWindow(sources=[source], spacing_mm=0.8)
        window.show()
        deadline = time.monotonic() + 20.0
        while time.monotonic() < deadline:
            app.processEvents()
            if window.getCurrentSource() == source and window.getLoadThread() is None:
                break
            time.sleep(0.01)
        assert window.getProject() is not None
        assert window.requireVolume().getData().shape == volume.getData().shape
        assert window.requireVolume().getSpacingMm() == pytest.approx((1.0, 1.0, 1.0))
        assert window.getSpacingSpin().value() == pytest.approx(1.0)
        assert window.getInternalLoadError() is None
        assert (
            window.requireProject().annotation(3).getPolygon(0).getSource()
            == "prototype"
        )
        window.set_slice(3)
        assert window.getCanvas().getPolygonItemCount() == 1
        window.close()

    # 切换强制空层复选框，验证修改立即写入标注文件。
    def test_force_empty_checkbox_saves_immediately(self, tmp_path: I_FilePath) -> None:
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_GuiFixtures import C_GuiFixtures

        app = C_GuiFixtures().app()
        source = C_GuiFixtures().source(tmp_path)
        window = C_Qt_AnnotationMainWindow(sources=[])
        window.setInternalLoadingSource(source)
        window.volume_loaded(C_GuiFixtures().volume(source))
        window._finish_loading_ui()
        window.add_polygon(C_PointList([(2, 2), (8, 2), (5, 8)]), "add")
        window.getForceEmptyCheck().setChecked(True)
        app.processEvents()
        payload = json.loads(source.getAnnotationPath().read_text(encoding="utf-8"))
        current = str(window.getCurrentSlice())
        assert payload["slices"][current]["force_empty"] is True
        assert len(payload["slices"][current]["polygons"]) == 1
        assert not window.getCanvas().getPolygonItemCount()
        assert window.getProject() is not None
        assert (
            not window.requireProject().to_mask()[:, :, window.getCurrentSlice()].any()
        )
        window.close()

    # 把 pytest 临时目录转换为路径接口，供业务测试复用。
    @pytest.fixture(name="tmp_path")
    def _adapt_path(self, tmp_path: Path) -> I_FilePath:
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        return C_FilePath(tmp_path)
