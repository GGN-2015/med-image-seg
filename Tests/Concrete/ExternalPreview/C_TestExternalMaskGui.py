from __future__ import annotations

import json
import threading
import time
from collections.abc import Iterator
from copy import deepcopy
from pathlib import Path
from typing import final

import numpy as np
import pytest
from numpy.typing import NDArray
from PySide6.QtCore import QPointF, QRectF, QThread, QTimer, SignalInstance
from PySide6.QtGui import QAction, QShortcut
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QGraphicsEllipseItem,
    QGraphicsPathItem,
    QGraphicsPixmapItem,
    QGraphicsPolygonItem,
    QGraphicsView,
    QGroupBox,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
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
from med_image_seg.Abstract.Presentation.Window import (
    T_MutableAnnotationMainWindow,
)
from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

from ...Abstract.Diagnostics.I_MutableMessageLog import I_MutableMessageLog
from ...Abstract.ExternalPreview.T_TestExternalMaskGui import T_TestExternalMaskGui


# 验证外置掩码的加载、只读显示、界面锁定和卸载恢复。
@final
class C_TestExternalMaskGui(
    T_TestExternalMaskGui[
        MonkeyPatch,
        T_MutableAnnotationMainWindow[
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
    ]
):
    # 为当前测试类配置离屏 Qt 环境。
    @pytest.fixture(autouse=True, name="configure_environment")
    def _configure_environment_fixture(self) -> None:
        from ..Environment.C_TestEnvironment import C_TestEnvironment

        C_TestEnvironment().configure()

    # 驱动 Qt 事件循环直到后台读取完成，并在超时或失败时终止测试。
    def _wait_loaded(
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
        from .C_ExternalMaskGuiFixtures import C_ExternalMaskGuiFixtures

        return C_ExternalMaskGuiFixtures().wait_loaded(window)

    # 创建测试窗口，退出测试时关闭窗口并释放相关资源。
    @pytest.fixture(name="window")
    def _window_fixture(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch
    ) -> Iterator[
        T_MutableAnnotationMainWindow[
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
        ]
    ]:
        from med_image_seg.Concrete.Domain.Imaging.C_MedicalVolume import (
            C_MedicalVolume,
        )
        from med_image_seg.Concrete.Domain.Imaging.C_Metadata import C_Metadata
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )
        from med_image_seg.Concrete.Storage.Volumes.C_ImageSourceFactory import (
            C_ImageSourceFactory,
        )

        from ..Diagnostics.C_MessageLog import C_MessageLog
        from .C_ExternalMaskGuiFixtures import C_ExternalMaskGuiFixtures

        app = QApplication.instance() or QApplication([])
        path = tmp_path / "scan.nii"
        path.write_bytes(b"synthetic-image")
        source = C_ImageSourceFactory().from_path(path)
        instance = C_Qt_AnnotationMainWindow(sources=[], language="zh")
        instance.setInternalLoadingSource(source)
        instance.volume_loaded(
            C_MedicalVolume(
                data=np.arange(20 * 16 * 9, dtype=np.float32).reshape(20, 16, 9),
                spacing_mm=(0.8, 0.8, 0.8),
                origin_lps_mm=(10.0, 20.0, 30.0),
                metadata=C_Metadata(json.dumps({})),
                source=path,
            )
        )
        instance._finish_loading_ui()
        instance.show()
        app.processEvents()
        self._mask_errors: I_MutableMessageLog = C_MessageLog()
        monkeypatch.setattr(
            QMessageBox,
            "critical",
            lambda *args: self._mask_errors.record(str(args[2])),
        )
        yield instance
        C_ExternalMaskGuiFixtures().wait_loaded(instance)
        instance.close()
        app.processEvents()
        instance.deleteLater()
        app.processEvents()

    # 生成可复现的标注样本，供多个测试场景使用。
    def _seed(
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
        from .C_ExternalMaskGuiFixtures import C_ExternalMaskGuiFixtures

        return C_ExternalMaskGuiFixtures().seed(window)

    # 在测试目录写入掩码，供外置预览加载流程使用。
    def _write_mask(
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
        tmp_path: I_FilePath,
        suffix: str = ".nii.gz",
        empty: bool = False,
    ) -> tuple[I_FilePath, NDArray[np.uint8]]:
        from .C_ExternalMaskGuiFixtures import C_ExternalMaskGuiFixtures

        return C_ExternalMaskGuiFixtures().write_mask(window, tmp_path, suffix, empty)

    # 查询画布的掩码图层，供测试检查颜色和像素。
    def _overlay(
        self,
        canvas: T_MutableSliceCanvas[
            QGraphicsView,
            QPointF,
            QRectF,
            QGraphicsPixmapItem,
            QGraphicsPathItem,
            QGraphicsPolygonItem,
            T_MutableVertexHandle[QGraphicsEllipseItem],
            SignalInstance,
        ],
    ) -> NDArray[np.uint8]:
        from .C_ExternalMaskGuiFixtures import C_ExternalMaskGuiFixtures

        return C_ExternalMaskGuiFixtures().overlay(canvas)

    # 验证启动后仅载入外置掩码按钮可用，包括尚未载入影像时。
    def test_buttons_start_with_only_load_enabled_even_without_image(
        self, monkeypatch: MonkeyPatch
    ) -> None:
        from med_image_seg.Concrete.Localization.C_Localizer import C_Localizer
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        app = QApplication.instance() or QApplication([])
        window = C_Qt_AnnotationMainWindow(sources=[], language="zh")
        assert window.getLoadExternalMaskButton().isEnabled()
        assert not window.getUnloadExternalMaskButton().isEnabled()
        assert window.getLoadExternalMaskButton().text() == "载入外置掩码"
        assert window.getUnloadExternalMaskButton().text() == "卸载外置掩码"
        messages = []
        monkeypatch.setattr(
            QMessageBox, "information", lambda *args: messages.append(args[2])
        )
        window.choose_external_mask()
        assert messages == [C_Localizer().translate("external_mask_no_image", "zh")]
        assert not window.getExternalPreviewActive()
        window.close()
        app.processEvents()

    # 验证外置掩码替代三个视图中的轮廓及插值，并更新区间条。
    @pytest.mark.parametrize("suffix", [".nii", ".nii.gz", ".ubd.npz"])
    def test_external_mask_replaces_all_polygon_views_and_coverage(
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
        tmp_path: I_FilePath,
        suffix: str,
    ) -> None:
        from med_image_seg.Concrete.Algorithms.Observation import (
            C_ObservationPlanes,
            C_OverlayPalette,
        )
        from med_image_seg.Concrete.Domain.Snapshots.C_RecordOperations import (
            C_RecordOperations,
        )

        from .C_ExternalMaskGuiFixtures import C_ExternalMaskGuiFixtures

        C_ExternalMaskGuiFixtures().seed(window)
        project = window.requireProject()
        original = deepcopy(C_RecordOperations().asdict(project))
        original_json = window.requireProjectPath().read_bytes()
        path, expected = C_ExternalMaskGuiFixtures().write_mask(
            window, tmp_path, suffix
        )
        assert window.load_external_mask(path)
        C_ExternalMaskGuiFixtures().wait_loaded(window)
        assert not self._mask_errors.getCount()
        assert window.getExternalPreviewActive()
        assert window.getReadOnly()
        assert window.getObserveRadio().isChecked()
        assert not window.getAnnotationIndexSpin().getHost().isEnabled()
        assert not window.getLoadExternalMaskButton().isEnabled()
        assert window.getUnloadExternalMaskButton().isEnabled()
        assert not window.getModeGroup().isEnabled()
        assert all(
            not action.isEnabled() for action in window.getAnnotationToolbar().actions()
        )
        assert not window.getAutosaveTimer().isActive()
        np.testing.assert_array_equal(window.requireExternalMask(), expected)
        np.testing.assert_array_equal(
            window.getMaskCoverageBar().getPresence(), expected.any(axis=(0, 1))
        )
        window._observation_clicked("LP", QPointF(8.5, 8.5))
        window.set_slice(7)
        for name, plane in C_ObservationPlanes().getPlanes().getItems():
            canvas = (
                window.getCanvas()
                if name == "LP"
                else window.getObservationWindow(name).getCanvas()
            )
            assert not canvas.getHandleCount()
            assert not canvas.getPolygonItemCount()
            overlay = C_ExternalMaskGuiFixtures().overlay(canvas)
            mask_section = plane.section(
                expected, window.getObservationPosition()
            ).astype(bool)
            np.testing.assert_array_equal(overlay[:, :, 3] > 0, mask_section)
            assert np.all(
                overlay[mask_section] == C_OverlayPalette().getExternalMaskColor()
            )
        assert window.getProject() is project
        assert C_RecordOperations().asdict(window.requireProject()) == original
        assert window.requireProjectPath().read_bytes() == original_json

    # 监测调用，验证外置预览不保存 JSON 或重新栅格化原多边形。
    def test_external_preview_never_calls_json_save_or_full_polygon_rasterization(
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
        tmp_path: I_FilePath,
        monkeypatch: MonkeyPatch,
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_AnnotationProject import (
            C_AnnotationProject,
        )
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Domain.Snapshots.C_RecordOperations import (
            C_RecordOperations,
        )

        from .C_ExternalMaskGuiFixtures import C_ExternalMaskGuiFixtures

        C_ExternalMaskGuiFixtures().seed(window)
        path, _ = C_ExternalMaskGuiFixtures().write_mask(window, tmp_path)
        original = deepcopy(C_RecordOperations().asdict(window.requireProject()))

        # 拦截外置预览期间不允许发生的 JSON 保存或原轮廓栅格化。
        def forbidden(*args, **kwargs):
            pytest.fail("External preview must not rasterize or save the JSON project")

        with monkeypatch.context() as patch:
            patch.setattr(C_AnnotationProject, "save", forbidden)
            patch.setattr(C_AnnotationProject, "to_mask", forbidden)
            assert window.load_external_mask(path)
            C_ExternalMaskGuiFixtures().wait_loaded(window)
            window.set_slice(1)
            window._observation_clicked("PS", QPointF(5.5, 7.5))
            window.getLevelSpin().setValue(window.getLevelSpin().value() + 5)
            window.set_language("en")
            window.add_polygon(C_PointList([(1, 1), (5, 1), (2, 5)]), "add")
            window.update_polygon(0, C_PointList([(1, 1), (5, 1), (2, 5)]))
            window.delete_last_edited_polygon()
            window.clear_current_slice()
            window.copy_previous_slice()
            window.set_slice_completed(True)
            window.set_force_empty(True)
            window.toggle_completed()
            window.commit_change()
            window.autosave_if_needed()
            assert window.save_project(notify=True, force=True)
            window.export_annotations()
            window.export_mask()
            window.export_ubd_mask()
            assert not window.set_annotation_index(1)
            window.getAddRadio().setChecked(True)
            assert window.getObserveRadio().isChecked()
            assert window.getReadOnly()
            assert C_RecordOperations().asdict(window.requireProject()) == original
            assert "JSON saving paused" in window.getAutosaveStatus().text()
            assert window.getHost().close()

    # 卸载外置掩码，核验原编号、切片、模式、区间及快捷键恢复。
    @pytest.mark.parametrize("mode", ["add", "erase", "observe"])
    @pytest.mark.parametrize("autosave_active", [True, False])
    def test_unload_restores_original_number_slice_mode_coverage_and_shortcuts(
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
        tmp_path: I_FilePath,
        monkeypatch: MonkeyPatch,
        mode: str,
        autosave_active: bool,
    ) -> None:
        from med_image_seg.Concrete.Storage.Projects.C_ProjectRepository import (
            C_ProjectRepository,
        )

        from .C_ExternalMaskGuiFixtures import C_ExternalMaskGuiFixtures

        window.set_annotation_index(3)
        C_ExternalMaskGuiFixtures().seed(window)
        window.getShowInterpolation().setChecked(False)
        radio = {
            "add": window.getAddRadio(),
            "erase": window.getEraseRadio(),
            "observe": window.getObserveRadio(),
        }[mode]
        radio.setChecked(True)
        if not autosave_active:
            window.getAutosaveTimer().stop()
        position = window.getObservationPosition()
        coverage = window.getMaskCoverageBar().getPresence()
        project, project_path = (window.requireProject(), window.requireProjectPath())
        saved = project_path.read_bytes()
        cached_mask = window.getInternalObservationMask()
        path, _ = C_ExternalMaskGuiFixtures().write_mask(window, tmp_path)
        assert window.load_external_mask(path)
        C_ExternalMaskGuiFixtures().wait_loaded(window)
        window._observation_clicked("PS", QPointF(8.5, 7.5))
        window._observation_clicked("SL", QPointF(8.5, 13.5))

        # 拦截卸载外置掩码时的 JSON 重载，保证恢复的是内存中的原项目。
        def no_reload(*args, **kwargs):
            pytest.fail(
                "Unloading must restore the in-memory project without reloading JSON"
            )

        monkeypatch.setattr(C_ProjectRepository, "load", no_reload)
        assert window.unload_external_mask()
        assert not window.getExternalPreviewActive()
        assert window.getExternalMask() is None
        assert window.getProject() is project
        assert window.getProjectPath() == project_path
        assert (
            window.getAnnotationIndex() == window.getAnnotationIndexSpin().value() == 3
        )
        assert (
            window.getCurrentSlice()
            == window.getSliceSlider().value()
            == window.getSliceSpin().value()
            == position[2]
        )
        assert window.getObservationPosition() == position
        assert window.getMaskCoverageBar().getPresence() == coverage
        assert window.getInternalObservationMask() is cached_mask
        assert radio.isChecked()
        assert window.getReadOnly() == (mode == "observe")
        assert window.getAnnotationIndexSpin().getHost().isEnabled() == (
            mode != "observe"
        )
        assert all(
            shortcut.isEnabled() == (mode != "observe")
            for shortcut in window.iterEditingShortcuts()
        )
        assert all(
            action.isEnabled() for action in window.getAnnotationToolbar().actions()
        )
        assert window.getLoadExternalMaskButton().isEnabled()
        assert not window.getUnloadExternalMaskButton().isEnabled()
        assert window.getAutosaveTimer().isActive() == autosave_active
        assert project_path.read_bytes() == saved
        assert window.getShowInterpolation().isChecked() == (mode == "observe")

    # 验证外置掩码选择框打开前，软件已经进入只读观察模式。
    @pytest.mark.parametrize("cancel", [True, False])
    def test_file_chooser_opens_after_switching_to_read_only(
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
        tmp_path: I_FilePath,
        monkeypatch: MonkeyPatch,
        cancel: bool,
    ) -> None:
        from .C_ExternalMaskGuiFixtures import C_ExternalMaskGuiFixtures

        C_ExternalMaskGuiFixtures().seed(window)
        path, _ = C_ExternalMaskGuiFixtures().write_mask(window, tmp_path)

        # 在文件选择回调中核对软件已进入只读预览状态。
        def choose(*args):
            assert window.getExternalPreviewActive()
            assert window.getReadOnly()
            assert not window.getAnnotationIndexSpin().getHost().isEnabled()
            assert window.getObserveRadio().isChecked()
            assert all(
                view.getHost().isVisible() for view in window.iterObservationWindows()
            )
            assert "*.nii *.nii.gz *.ubd.npz" in args[3]
            return ("" if cancel else str(path), "")

        monkeypatch.setattr(QFileDialog, "getOpenFileName", choose)
        window.choose_external_mask()
        C_ExternalMaskGuiFixtures().wait_loaded(window)
        if cancel:
            assert not window.getExternalPreviewActive()
            assert not window.getReadOnly()
            assert window.getAnnotationIndexSpin().getHost().isEnabled()
            assert window.getLoadExternalMaskButton().isEnabled()
            assert not window.getUnloadExternalMaskButton().isEnabled()
        else:
            assert window.getExternalMask() is not None

    # 模拟外置掩码加载失败，核验原模式及控件状态恢复。
    @pytest.mark.parametrize("failure", ["missing", "corrupt", "unsupported"])
    def test_failed_external_load_restores_original_editing_state(
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
        tmp_path: I_FilePath,
        failure: str,
    ) -> None:
        from .C_ExternalMaskGuiFixtures import C_ExternalMaskGuiFixtures

        window.set_annotation_index(2)
        C_ExternalMaskGuiFixtures().seed(window)
        position = window.getObservationPosition()
        project = window.requireProject()
        saved = window.requireProjectPath().read_bytes()
        path = tmp_path / ("invalid.npz" if failure == "unsupported" else "invalid.nii")
        if failure != "missing":
            path.write_bytes(b"not a medical image")
        assert window.load_external_mask(path)
        C_ExternalMaskGuiFixtures().wait_loaded(window)
        assert self._mask_errors.getCount()
        assert not window.getExternalPreviewActive()
        assert not window.getReadOnly()
        assert window.getProject() is project
        assert window.getAnnotationIndex() == 2
        assert window.getObservationPosition() == position
        assert window.getExternalLoadingDialog() is None
        assert window.requireCentralWidget().isEnabled()
        assert window.getAnnotationToolbar().isEnabled()
        assert window.getLoadExternalMaskButton().isEnabled()
        assert not window.getUnloadExternalMaskButton().isEnabled()
        assert window.getAutosaveTimer().isActive()
        assert QApplication.overrideCursor() is None
        assert window.requireProjectPath().read_bytes() == saved

    # 延迟后台读取，验证事件循环保持响应且三个视图均不可操作。
    def test_external_loading_is_nonblocking_and_locks_all_views_until_completion(
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
        tmp_path: I_FilePath,
        monkeypatch: MonkeyPatch,
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskReader import (
            C_MedicalMaskReader,
        )

        from .C_ExternalMaskGuiFixtures import C_ExternalMaskGuiFixtures

        path, mask = C_ExternalMaskGuiFixtures().write_mask(window, tmp_path)
        started, release = (threading.Event(), threading.Event())
        worker_threads = []

        # 延迟后台掩码读取，供主线程检查界面响应和操作锁定。
        def delayed(*args):
            worker_threads.append(threading.get_ident())
            started.set()
            assert release.wait(5)
            return mask

        monkeypatch.setattr(C_MedicalMaskReader, "read", delayed)
        ticks = []
        timer = QTimer(window.getHost())
        timer.setInterval(5)
        timer.timeout.connect(lambda: ticks.append(True))
        timer.start()
        try:
            assert window.load_external_mask(path)
            deadline = time.monotonic() + 2
            while (
                not started.is_set() or len(ticks) < 3
            ) and time.monotonic() < deadline:
                QApplication.processEvents()
                time.sleep(0.005)
            assert started.is_set()
            assert len(ticks) >= 3
            assert len(worker_threads) == 1
            assert worker_threads[0] != threading.get_ident()
            assert not window.requireCentralWidget().isEnabled()
            assert not window.getAnnotationToolbar().isEnabled()
            assert all(
                not view.getHost().isEnabled()
                for view in window.iterObservationWindows()
            )
            assert all(
                not shortcut.isEnabled()
                for shortcut in window.getHost().findChildren(QShortcut)
            )
            assert window.requireExternalLoadingDialog().isVisible()
            progress = window.requireExternalLoadingDialog().findChild(QProgressBar)
            assert progress is not None
            assert (progress.minimum(), progress.maximum()) == (0, 0)
            assert not window.unload_external_mask()
            assert not window.load_external_mask(path)
            assert not window.getHost().close()
        finally:
            release.set()
            timer.stop()
            C_ExternalMaskGuiFixtures().wait_loaded(window)
        assert window.requireCentralWidget().isEnabled()
        assert window.getUnloadExternalMaskButton().isEnabled()
        assert window.getExternalLoadingDialog() is None

    # 验证空外置掩码显示全灰区间，不回退到原 JSON 轮廓。
    def test_empty_external_mask_displays_all_gray_coverage_without_json_fallback(
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
        tmp_path: I_FilePath,
    ) -> None:
        from .C_ExternalMaskGuiFixtures import C_ExternalMaskGuiFixtures

        C_ExternalMaskGuiFixtures().seed(window)
        path, _ = C_ExternalMaskGuiFixtures().write_mask(window, tmp_path, empty=True)
        assert window.load_external_mask(path)
        C_ExternalMaskGuiFixtures().wait_loaded(window)
        assert window.getExternalMask() is not None
        assert not window.requireExternalMask().any()
        assert window.getMaskCoverageBar().getPresence() == (False,) * 9
        assert not window.getCanvas().getPolygonItemCount()
        assert not (
            C_ExternalMaskGuiFixtures().overlay(window.getCanvas())[:, :, 3] > 0
        ).any()

    # 开始外置预览前闭合未保存草稿，卸载后恢复其原编辑环境。
    def test_unsaved_draft_is_closed_before_external_preview_then_restored(
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
        tmp_path: I_FilePath,
    ) -> None:
        from med_image_seg.Concrete.Domain.Geometry.C_Point2D import C_Point2D
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList

        from .C_ExternalMaskGuiFixtures import C_ExternalMaskGuiFixtures

        points = [(2, 2), (9, 2), (5, 10)]
        window.getCanvas().setDraftPoints(
            C_PointList([C_Point2D(*point) for point in points])
        )
        old_slice = window.getCurrentSlice()
        path, _ = C_ExternalMaskGuiFixtures().write_mask(window, tmp_path)
        window.load_external_mask(path)
        C_ExternalMaskGuiFixtures().wait_loaded(window)
        assert not window.getCanvas().getHandleCount()
        assert window.requireProject().annotation(old_slice).getPolygon(
            0
        ).getPoints() == C_PointList(tuple(points))
        window.unload_external_mask()
        assert window.getCanvas().getHandleCount()
        assert window.getCurrentSlice() == old_slice

    # 把 pytest 临时目录转换为路径接口，供业务测试复用。
    @pytest.fixture(name="tmp_path")
    def _adapt_path(self, tmp_path: Path) -> I_FilePath:
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        return C_FilePath(tmp_path)
