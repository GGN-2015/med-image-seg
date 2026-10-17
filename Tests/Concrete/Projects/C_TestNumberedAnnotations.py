from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import final

import numpy as np
import pytest
from PySide6.QtCore import QPointF, QRectF, Qt, QThread, QTimer, SignalInstance
from PySide6.QtGui import QAction, QShortcut, QValidator
from PySide6.QtTest import QTest
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

from med_image_seg.Abstract.Domain.Annotations import (
    I_MutableAnnotationProject,
)
from med_image_seg.Abstract.Domain.Geometry.I_PointList import I_PointList
from med_image_seg.Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
from med_image_seg.Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
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

from ...Abstract.Projects.T_TestNumberedAnnotations import T_TestNumberedAnnotations


# 验证编号切换、独立项目和空编号文件的删除策略。
@final
class C_TestNumberedAnnotations(
    T_TestNumberedAnnotations[
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
        MonkeyPatch,
    ]
):
    # 为当前测试类配置离屏 Qt 环境。
    @pytest.fixture(autouse=True, name="configure_environment")
    def _configure_environment_fixture(self) -> None:
        from ..Environment.C_TestEnvironment import C_TestEnvironment

        C_TestEnvironment().configure()

    # 启动影像读取前保存当前项目，避免切换来源时丢失标注。
    def _load_source(
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
        path: I_FilePath,
        shape: tuple[int, int, int] = (20, 16, 9),
    ) -> I_ImageSource:
        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        return C_NumberedAnnotationsFixtures().load_source(window, path, shape)

    # 创建测试窗口，退出测试时关闭窗口并释放相关资源。
    @pytest.fixture(name="window")
    def _window_fixture(
        self, tmp_path: I_FilePath
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
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        app = QApplication.instance() or QApplication([])
        instance = C_Qt_AnnotationMainWindow(sources=[], language="zh")
        C_NumberedAnnotationsFixtures().load_source(instance, tmp_path / "扫描.nii.gz")
        instance.show()
        app.processEvents()
        yield instance
        instance.close()
        app.processEvents()
        instance.deleteLater()
        app.processEvents()

    # 构造指定位置的轮廓样本，供标注行为测试使用。
    def _polygon(self, offset: float = 0) -> I_PointList:
        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        return C_NumberedAnnotationsFixtures().polygon(offset)

    # 使用当前影像和网格创建空项目。
    def _new_project(
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
    ) -> I_MutableAnnotationProject:
        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        return C_NumberedAnnotationsFixtures().new_project(window)

    # 确认外置掩码操作没有生成或修改标注配套文件。
    def _assert_no_sidecars(self, path: I_FilePath) -> None:
        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        return C_NumberedAnnotationsFixtures().assert_no_sidecars(path)

    # 验证编号默认是 0，且标签随界面语言更新。
    def test_number_selector_defaults_to_zero_and_translates(
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
        assert window.getAnnotationIndex() == 0
        assert window.getAnnotationIndexSpin().value() == 0
        assert window.getAnnotationIndexLabel().text() == "标注编号"
        assert (
            window.getProjectPath() == window.requireCurrentSource().getAnnotationPath()
        )
        assert window.requireProjectPath().is_file()
        window.set_language("en")
        assert window.getAnnotationIndexLabel().text() == "Annotation number"
        assert (
            "Numbered files with no polygons"
            in window.getAnnotationIndexSpin().getHost().toolTip()
        )

    # 反复切换编号，验证项目独立且影像不会重复加载。
    def test_switching_numbers_keeps_projects_independent_without_reloading_image(
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
        monkeypatch: MonkeyPatch,
    ) -> None:
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Storage.Projects.C_ProjectRepository import (
            C_ProjectRepository,
        )
        from med_image_seg.Concrete.Storage.Volumes.C_MedicalVolumeReader import (
            C_MedicalVolumeReader,
        )

        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        window.set_slice(3)
        window.add_polygon(
            C_PointList(C_NumberedAnnotationsFixtures().polygon()), "add"
        )
        zero_project = window.requireProject()
        zero_path = window.requireProjectPath()
        volume = window.requireVolume()
        level, width = (window.getLevelSpin().value(), window.getWidthSpin().value())

        # 拦截编号切换时重新读取影像的调用。
        def no_image_read(*args, **kwargs):
            pytest.fail("Changing annotation number must not reload the image")

        monkeypatch.setattr(C_MedicalVolumeReader, "read", no_image_read)
        window.getAnnotationIndexSpin().setValue(1)
        first_path = window.requireCurrentSource().annotation_path_for_index(1)
        assert window.getAnnotationIndex() == 1
        assert window.getProject() is not zero_project
        assert window.getProjectPath() == first_path
        assert window.getVolume() is volume
        assert window.getCurrentSlice() == 3
        assert (window.getLevelSpin().value(), window.getWidthSpin().value()) == (
            level,
            width,
        )
        assert not window.requireProject().getHasPolygons()
        assert not any(window.getMaskCoverageBar().getPresence())
        C_NumberedAnnotationsFixtures().assert_no_sidecars(first_path)
        zero_bytes = zero_path.read_bytes()
        window.add_polygon(
            C_PointList(C_NumberedAnnotationsFixtures().polygon(5)), "add"
        )
        window.set_slice_completed(True)
        first_saved = C_ProjectRepository().load(first_path)
        assert first_saved.annotation(3).getCompleted()
        assert first_saved.annotation(3).getPolygon(0).getPoints() == C_PointList(
            tuple(C_NumberedAnnotationsFixtures().polygon(5))
        )
        assert zero_path.read_bytes() == zero_bytes
        window.getAnnotationIndexSpin().setValue(0)
        assert window.getProjectPath() == zero_path
        assert window.requireProject().annotation(3).getPolygon(
            0
        ).getPoints() == C_PointList(tuple(C_NumberedAnnotationsFixtures().polygon()))
        assert not window.requireProject().annotation(3).getCompleted()
        assert window.getCanvas().getHandleCount()
        window.getAnnotationIndexSpin().setValue(1)
        assert window.requireProject().annotation(3).getCompleted()
        assert window.requireProject().annotation(3).getPolygon(
            0
        ).getPoints() == C_PointList(tuple(C_NumberedAnnotationsFixtures().polygon(5)))

    # 验证回车只提交一次编号，且上下箭头可逐步调整。
    def test_number_input_commits_once_on_enter_and_supports_arrow_steps(
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
        monkeypatch: MonkeyPatch,
    ) -> None:
        opened = []
        original = window._open_annotation_project

        # 记录项目打开次数并调用原实现，用于检查编号只提交一次。
        def tracked(source: I_ImageSource, volume: I_MedicalVolume, index: int):
            opened.append(index)
            return original(source, volume, index)

        monkeypatch.setattr(window, "_open_annotation_project", tracked)
        editor = window.getAnnotationIndexSpin().getHost().lineEdit()
        editor.setFocus()
        editor.selectAll()
        QTest.keyClicks(editor, "12")
        assert window.getAnnotationIndex() == 0
        assert opened == []
        QTest.keyClick(editor, Qt.Key.Key_Return)
        assert opened == [12]
        assert window.getAnnotationIndex() == 12
        QTest.keyClick(window.getAnnotationIndexSpin().getHost(), Qt.Key.Key_Up)
        assert window.getAnnotationIndex() == 13
        QTest.keyClick(window.getAnnotationIndexSpin().getHost(), Qt.Key.Key_Down)
        assert window.getAnnotationIndex() == 12
        window.getAnnotationIndexSpin().getHost().stepBy(-100)
        assert window.getAnnotationIndex() == 0
        assert (
            not window.getAnnotationIndexSpin().getHost().stepEnabled()
            & QAbstractSpinBox.StepEnabledFlag.StepDownEnabled
        )

    # 验证标注编号支持任意精度的非负整数并拒绝负值。
    def test_number_input_supports_arbitrary_precision_and_rejects_negative_values(
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
        index = 10**35 + 7
        window.getAnnotationIndexSpin().setValue(index)
        assert window.getAnnotationIndex() == index
        assert window.getAnnotationIndexSpin().value() == index
        assert (
            window.requireProjectPath().getName() == f"扫描.med-image-seg-{index}.json"
        )
        window.getAnnotationIndexSpin().getHost().stepBy(1)
        assert window.getAnnotationIndex() == index + 1
        with pytest.raises(ValueError, match="nonnegative"):
            window.getAnnotationIndexSpin().setValue(-1)
        with pytest.raises(ValueError, match="nonnegative"):
            window.set_annotation_index(-1)
        assert window.getAnnotationIndex() == index + 1
        state, _, _ = window.getAnnotationIndexSpin().getHost().validate("-1", 2)
        assert state == QValidator.State.Invalid
        state, _, _ = window.getAnnotationIndexSpin().getHost().validate("1.5", 3)
        assert state == QValidator.State.Invalid

    # 重复选择当前编号，验证不重复读取或保存项目。
    def test_reselecting_active_number_does_not_reload_or_save(
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
        monkeypatch: MonkeyPatch,
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_AnnotationProject import (
            C_AnnotationProject,
        )

        active = window.requireProject()

        # 拦截重复选择当前编号导致的多余读取或保存。
        def unexpected(*args, **kwargs):
            pytest.fail("The active annotation should not be reloaded or saved")

        monkeypatch.setattr(window, "_open_annotation_project", unexpected)
        with monkeypatch.context() as patch:
            patch.setattr(C_AnnotationProject, "save", unexpected)
            assert window.set_annotation_index(0)
        assert window.getProject() is active

    # 编辑非零编号项目，验证轮廓和插值状态实时写盘。
    @pytest.mark.parametrize(
        "action",
        [
            "add",
            "drag",
            "copy",
            "review",
            "force_empty",
            "unreview",
            "restore_interpolation",
        ],
    )
    def test_numbered_annotation_edits_save_immediately(
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
        monkeypatch: MonkeyPatch,
        action: str,
    ) -> None:
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath
        from med_image_seg.Concrete.Storage.Projects.C_ProjectRepository import (
            C_ProjectRepository,
        )

        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        window.set_annotation_index(5)
        window.set_slice(1)
        window.add_polygon(
            C_PointList(C_NumberedAnnotationsFixtures().polygon()), "add"
        )
        window.set_slice(7)
        window.add_polygon(
            C_PointList(C_NumberedAnnotationsFixtures().polygon(4)), "add"
        )
        window.set_slice(4)
        path = window.requireProjectPath()
        previous = path.read_bytes()
        if action == "add":
            window.add_polygon(
                C_PointList(C_NumberedAnnotationsFixtures().polygon(2)), "add"
            )
        elif action == "drag":
            window.set_slice(1)
            window.update_polygon(
                0, C_PointList(C_NumberedAnnotationsFixtures().polygon(1))
            )
        elif action == "copy":
            window.set_slice(2)
            window.copy_previous_slice()
        elif action == "review":
            window.set_slice_completed(True)
        elif action == "force_empty":
            window.set_force_empty(True)
        elif action == "unreview":
            window.set_slice_completed(True)
            window.set_slice_completed(False)
        elif action == "restore_interpolation":
            window.set_slice_completed(True)
            monkeypatch.setattr(
                QMessageBox, "question", lambda *args: QMessageBox.StandardButton.Yes
            )
            window.clear_current_slice()
        assert path.is_file()
        assert path.read_bytes() != previous
        restored = C_ProjectRepository().load(path)
        np.testing.assert_array_equal(
            restored.to_mask(), window.requireProject().to_mask()
        )
        assert (
            restored.getCompletedCount() == window.requireProject().getCompletedCount()
        )
        assert (
            restored.getKeyframeIndices()
            == window.requireProject().getKeyframeIndices()
        )
        assert not window.getInternalDirty()
        assert C_FilePath(f"{path}.bak").is_file()

    # 删除最后一个轮廓，验证非零编号主文件和备份均清理且不会恢复。
    @pytest.mark.parametrize("action", ["undo", "clear", "copy_empty"])
    def test_removing_last_polygon_removes_all_files_and_prevents_backup_resurrection(
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
        monkeypatch: MonkeyPatch,
        action: str,
    ) -> None:
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        window.set_annotation_index(2)
        window.add_polygon(
            C_PointList(C_NumberedAnnotationsFixtures().polygon()), "add"
        )
        window.set_slice_completed(True)
        path = window.requireProjectPath()
        previous = path.read_bytes()
        assert C_FilePath(f"{path}.bak").is_file()
        for suffix in (".tmp", ".bak.tmp"):
            C_FilePath(f"{path}{suffix}").write_bytes(previous)
        monkeypatch.setattr(
            QMessageBox, "question", lambda *args: QMessageBox.StandardButton.Yes
        )
        if action == "undo":
            window.delete_last_edited_polygon()
        elif action == "clear":
            window.clear_current_slice()
        else:
            window.copy_previous_slice()
        assert not window.requireProject().getHasPolygons()
        C_NumberedAnnotationsFixtures().assert_no_sidecars(path)
        assert not window.getInternalDirty()
        assert "不保留 JSON" in window.getAutosaveStatus().text()
        window.set_annotation_index(0)
        window.set_annotation_index(2)
        assert not window.requireProject().getHasPolygons()
        assert window.requireProject().getCompletedCount() == 0
        assert window.requireProject().getKeyframeIndices() == ()
        C_NumberedAnnotationsFixtures().assert_no_sidecars(path)

    # 清空一层但保留另一层轮廓，验证非零编号文件不被删除。
    def test_removing_one_slice_keeps_file_if_another_slice_has_polygons(
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
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Storage.Projects.C_ProjectRepository import (
            C_ProjectRepository,
        )

        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        window.set_annotation_index(1)
        window.set_slice(1)
        window.add_polygon(
            C_PointList(C_NumberedAnnotationsFixtures().polygon()), "add"
        )
        window.set_slice(7)
        window.add_polygon(
            C_PointList(C_NumberedAnnotationsFixtures().polygon(3)), "add"
        )
        window.delete_last_edited_polygon()
        assert window.requireProjectPath().is_file()
        assert window.requireProject().getHasPolygons()
        assert (
            C_ProjectRepository()
            .load(window.requireProjectPath())
            .annotation(1)
            .iterPolygons()
        )

    # 验证仅含复核或强制空层状态的项目只在 0 号保留文件。
    @pytest.mark.parametrize("number", [0, 1])
    def test_review_or_force_empty_without_polygons_only_persists_for_number_zero(
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
        number: int,
    ) -> None:
        from med_image_seg.Concrete.Storage.Projects.C_ProjectRepository import (
            C_ProjectRepository,
        )

        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        window.set_annotation_index(number)
        window.set_slice_completed(True)
        window.set_force_empty(True)
        path = window.requireProjectPath()
        if number == 0:
            saved = C_ProjectRepository().load(path)
            assert saved.annotation(window.getCurrentSlice()).getCompleted()
            assert saved.annotation(window.getCurrentSlice()).getForceEmpty()
        else:
            C_NumberedAnnotationsFixtures().assert_no_sidecars(path)
        window.set_annotation_index(3)
        window.set_annotation_index(number)
        assert window.requireProject().annotation(
            window.getCurrentSlice()
        ).getCompleted() == (number == 0)
        assert window.requireProject().annotation(
            window.getCurrentSlice()
        ).getForceEmpty() == (number == 0)

    # 验证强制空层仍有已存轮廓时不会删除非零编号文件。
    def test_forced_empty_with_saved_polygons_keeps_numbered_file(
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
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Storage.Projects.C_ProjectRepository import (
            C_ProjectRepository,
        )

        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        window.set_annotation_index(1)
        window.add_polygon(
            C_PointList(C_NumberedAnnotationsFixtures().polygon()), "add"
        )
        window.set_force_empty(True)
        assert not window.requireProject().to_mask().any()
        assert window.requireProject().getHasPolygons()
        restored = C_ProjectRepository().load(window.requireProjectPath())
        assert restored.annotation(window.getCurrentSlice()).iterPolygons()
        assert restored.annotation(window.getCurrentSlice()).getForceEmpty()

    # 切换编号前闭合草稿，验证它保存到原编号而非新编号。
    def test_switching_closes_and_saves_draft_to_the_outgoing_number(
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
        from med_image_seg.Concrete.Domain.Geometry.C_Point2D import C_Point2D
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Storage.Projects.C_ProjectRepository import (
            C_ProjectRepository,
        )

        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        old_path = window.requireProjectPath()
        old_slice = window.getCurrentSlice()
        window.getCanvas().setDraftPoints(
            C_PointList(
                [
                    C_Point2D(point.getX(), point.getY())
                    for point in C_NumberedAnnotationsFixtures().polygon()
                ]
            )
        )
        assert window.set_annotation_index(6)
        saved = C_ProjectRepository().load(old_path)
        assert saved.annotation(old_slice).getPolygon(0).getPoints() == C_PointList(
            tuple(C_NumberedAnnotationsFixtures().polygon())
        )
        assert not window.requireProject().getHasPolygons()
        assert not window.getCanvas().getDraftPointCount()

    # 模拟原项目保存失败，核验切换被阻止且编号输入恢复。
    def test_old_save_failure_blocks_switch_and_restores_number_input(
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
        monkeypatch: MonkeyPatch,
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_AnnotationProject import (
            C_AnnotationProject,
        )

        old_project, old_path = (window.requireProject(), window.requireProjectPath())
        old_bytes = old_path.read_bytes()
        window.setInternalDirty(True)
        errors = []

        # 模拟原标注文件被锁定，使保存失败并阻止编号切换。
        def fail(*args, **kwargs):
            raise PermissionError("annotation is locked")

        with monkeypatch.context() as patch:
            patch.setattr(C_AnnotationProject, "save", fail)
            patch.setattr(QMessageBox, "critical", lambda *args: errors.append(args[2]))
            window.getAnnotationIndexSpin().setValue(1)
            assert window.getAnnotationIndex() == 0
            assert window.getAnnotationIndexSpin().value() == 0
            assert window.getProject() is old_project
            assert window.getProjectPath() == old_path
            assert window.getInternalDirty()
            assert old_path.read_bytes() == old_bytes
            assert (
                not window.requireCurrentSource().annotation_path_for_index(1).exists()
            )
        assert errors == ["annotation is locked"]

    # 切到不可读或几何不匹配的标注，验证原活动项目不被替换。
    @pytest.mark.parametrize("failure", ["corrupt", "fingerprint", "geometry"])
    def test_unreadable_or_mismatched_target_does_not_replace_active_project(
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
        monkeypatch: MonkeyPatch,
        failure: str,
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList

        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        window.add_polygon(
            C_PointList(C_NumberedAnnotationsFixtures().polygon()), "add"
        )
        old_project, old_path = (window.requireProject(), window.requireProjectPath())
        target = window.requireCurrentSource().annotation_path_for_index(1)
        if failure == "corrupt":
            target.write_text("broken JSON", encoding="utf-8")
        else:
            project = C_NumberedAnnotationsFixtures().new_project(window)
            project.add_polygon(
                2,
                C_PolygonAnnotation(
                    points=tuple(C_NumberedAnnotationsFixtures().polygon(3))
                ),
            )
            if failure == "fingerprint":
                project.setSourceFingerprint("wrong-image")
            else:
                project.setShapeLps((30, 30, 30))
            project.save(target)
        target_bytes = target.read_bytes()
        errors = []
        monkeypatch.setattr(
            QMessageBox, "critical", lambda *args: errors.append(args[2])
        )
        window.getAnnotationIndexSpin().setValue(1)
        assert errors
        assert window.getAnnotationIndex() == 0
        assert window.getAnnotationIndexSpin().value() == 0
        assert window.getProject() is old_project
        assert window.getProjectPath() == old_path
        assert target.read_bytes() == target_bytes
        assert window.getHost().isEnabled()
        assert window.getAutosaveTimer().isActive()
        assert not window.getInternalSwitchingAnnotation()

    # 损坏非零编号主文件，验证只恢复该编号自己的备份。
    def test_numbered_project_can_recover_its_own_backup(
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
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )

        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        target = window.requireCurrentSource().annotation_path_for_index(4)
        project = C_NumberedAnnotationsFixtures().new_project(window)
        project.add_polygon(
            2,
            C_PolygonAnnotation(
                points=tuple(C_NumberedAnnotationsFixtures().polygon(2))
            ),
        )
        project.save(target)
        project.save(target)
        target.write_text("broken", encoding="utf-8")
        assert window.set_annotation_index(4)
        assert window.requireProject().annotation(2).iterPolygons()
        assert window.getProjectPath() == target
        window.set_slice(2)
        window.set_slice_completed(True)
        assert json.loads(target.read_text(encoding="utf-8"))["slices"]["2"][
            "completed"
        ]

    # 验证文件删除失败时保留未保存状态并阻止编号切换。
    def test_deletion_failure_keeps_dirty_project_and_blocks_switch(
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
        monkeypatch: MonkeyPatch,
    ) -> None:
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        window.set_annotation_index(1)
        window.add_polygon(
            C_PointList(C_NumberedAnnotationsFixtures().polygon()), "add"
        )
        window.set_slice_completed(True)
        path = window.requireProjectPath()
        original = C_FilePath.unlink
        errors = []

        # 模拟空标注主文件删除失败，核验原项目保持未保存状态。
        def fail_primary(candidate: I_FilePath, *args, **kwargs):
            assert isinstance(candidate, C_FilePath)
            if candidate == path:
                raise PermissionError("cannot remove empty annotation")
            return original(candidate, *args, **kwargs)

        with monkeypatch.context() as patch:
            patch.setattr(C_FilePath, "unlink", fail_primary)
            patch.setattr(QMessageBox, "critical", lambda *args: errors.append(args[2]))
            window.delete_last_edited_polygon()
            assert not window.requireProject().getHasPolygons()
            assert window.getInternalDirty()
            assert not window.set_annotation_index(2)
            assert window.getAnnotationIndex() == 1
            assert window.getAnnotationIndexSpin().value() == 1
            assert path.is_file()
        assert errors == ["cannot remove empty annotation"]
        window.autosave_if_needed()
        C_NumberedAnnotationsFixtures().assert_no_sidecars(path)
        assert not window.getInternalDirty()

    # 验证观察模式锁定标注编号，返回编辑模式后才重新启用。
    def test_observation_locks_number_until_return_to_editing(
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
        from med_image_seg.Concrete.Algorithms.Observation import (
            C_ObservationPlanes,
        )
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList

        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        for index in (1, 7):
            window.set_slice(index)
            window.add_polygon(
                C_PointList(C_NumberedAnnotationsFixtures().polygon()), "add"
            )
        project = C_NumberedAnnotationsFixtures().new_project(window)
        for index in (2, 8):
            project.add_polygon(
                index,
                C_PolygonAnnotation(
                    points=tuple(C_NumberedAnnotationsFixtures().polygon(6))
                ),
            )
        project.set_force_empty(5, True)
        project.save(window.requireCurrentSource().annotation_path_for_index(1))
        expected = project.to_mask()
        window.set_slice(3)
        window.getObserveRadio().setChecked(True)
        window._observation_clicked("LP", QPointF(11.5, 6.5))
        position = window.getObservationPosition()
        views = tuple(window.iterObservationWindows())
        old_mask = window.requireInternalObservationMask().copy()
        assert not window.getAnnotationIndexSpin().getHost().isEnabled()
        window.getAnnotationIndexSpin().setValue(1)
        assert (
            window.getAnnotationIndex() == window.getAnnotationIndexSpin().value() == 0
        )
        np.testing.assert_array_equal(window.requireInternalObservationMask(), old_mask)
        window.getAddRadio().setChecked(True)
        assert window.getAnnotationIndexSpin().getHost().isEnabled()
        window.getAnnotationIndexSpin().setValue(1)
        window.getObserveRadio().setChecked(True)
        assert window.getReadOnly()
        assert window.getObservationPosition() == position
        assert tuple(window.iterObservationWindows()) == views
        assert all(view.getHost().isVisible() for view in views)
        assert all(not control.isEnabled() for control in window.iterEditingControls())
        np.testing.assert_array_equal(window.requireInternalObservationMask(), expected)
        assert not np.array_equal(old_mask, window.requireInternalObservationMask())
        np.testing.assert_array_equal(
            window.getMaskCoverageBar().getPresence(), expected.any(axis=(0, 1))
        )
        for view in views:
            plane = (
                C_ObservationPlanes().getPlanes().getByName(view.getPlane().getName())
            )
            assert view.getCanvas().getInternalCrosshairPosition() == QPointF(
                position[plane.getHorizontalAxis()] + 0.5,
                position[plane.getVerticalAxis()] + 0.5,
            )
            assert view.getCanvas().getInternalInterpolationItem() is not None

    # 切换影像，验证当前选择的标注编号保持不变。
    def test_selected_number_is_retained_when_loading_another_image(
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
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList

        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        window.set_annotation_index(3)
        window.add_polygon(
            C_PointList(C_NumberedAnnotationsFixtures().polygon()), "add"
        )
        old_path = window.requireProjectPath()
        old_bytes = old_path.read_bytes()
        source = C_NumberedAnnotationsFixtures().load_source(
            window, tmp_path / "second.nii", (15, 12, 7)
        )
        assert window.getAnnotationIndex() == 3
        assert window.getAnnotationIndexSpin().value() == 3
        assert window.getProjectPath() == source.annotation_path_for_index(3)
        assert not source.getAnnotationPath().exists()
        assert not window.requireProject().getHasPolygons()
        C_NumberedAnnotationsFixtures().assert_no_sidecars(window.requireProjectPath())
        window.add_polygon(
            C_PointList(C_NumberedAnnotationsFixtures().polygon()), "add"
        )
        assert window.requireProjectPath().is_file()
        assert old_path.read_bytes() == old_bytes

    # 验证 JSON 导出使用当前编号，并遵守非零空文件删除策略。
    @pytest.mark.parametrize("empty", [True, False])
    def test_json_export_uses_active_number_and_respects_empty_file_policy(
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
        monkeypatch: MonkeyPatch,
        empty: bool,
    ) -> None:
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList
        from med_image_seg.Concrete.Localization.C_Localizer import C_Localizer

        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        window.set_annotation_index(7)
        if not empty:
            window.add_polygon(
                C_PointList(C_NumberedAnnotationsFixtures().polygon()), "add"
            )
        messages = []
        monkeypatch.setattr(
            QFileDialog,
            "getSaveFileName",
            lambda _parent, _title, directory, _filter: (directory, ""),
        )
        monkeypatch.setattr(
            QMessageBox, "information", lambda *args: messages.append(args[2])
        )
        window.export_annotations()
        assert messages
        assert str(window.requireProjectPath()) in messages[0]
        assert window.requireProjectPath().getName() == "扫描.med-image-seg-7.json"
        if empty:
            C_NumberedAnnotationsFixtures().assert_no_sidecars(
                window.requireProjectPath()
            )
            assert "不导出空文件" in messages[0]
        else:
            assert window.requireProjectPath().is_file()
            assert messages[0] == C_Localizer().translate(
                "export_annotations_complete_message",
                "zh",
                path=str(window.requireProjectPath()),
            )

    # 验证尚未载入影像时也可预先选择标注编号。
    def test_index_can_be_set_before_loading_first_image(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Presentation.Window import (
            C_Qt_AnnotationMainWindow,
        )

        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        app = QApplication.instance() or QApplication([])
        window = C_Qt_AnnotationMainWindow(sources=[])
        assert not window.getAnnotationIndexSpin().getHost().isEnabled()
        assert window.set_annotation_index(10)
        C_NumberedAnnotationsFixtures().load_source(window, tmp_path / "scan.nii")
        assert window.requireProjectPath().getName() == "scan.med-image-seg-10.json"
        assert window.getAnnotationIndexSpin().value() == 10
        C_NumberedAnnotationsFixtures().assert_no_sidecars(window.requireProjectPath())
        window.close()
        app.processEvents()

    # 验证空编号输入回退到当前编号，不意外切换项目。
    def test_blank_number_input_restores_active_value(
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
        window.set_annotation_index(3)
        editor = window.getAnnotationIndexSpin().getHost().lineEdit()
        editor.selectAll()
        QTest.keyClick(editor, Qt.Key.Key_Backspace)
        QTest.keyClick(editor, Qt.Key.Key_Return)
        assert window.getAnnotationIndex() == 3
        assert window.getAnnotationIndexSpin().value() == 3
        assert editor.text() == "3"

    # 验证编号输入只读时上下箭头也不可用。
    def test_spin_box_read_only_state_disables_arrows(self) -> None:
        from med_image_seg.Concrete.Presentation.Navigation import (
            C_Qt_AnnotationIndexSpinBox,
        )

        app = QApplication.instance() or QApplication([])
        spin = C_Qt_AnnotationIndexSpinBox()
        spin.setReadOnly(True)
        assert spin.stepEnabled() == QAbstractSpinBox.StepEnabledFlag.StepNone
        spin.close()
        app.processEvents()

    # 验证载入影像使用所选编号，默认仍为 0 号。
    def test_loading_image_opens_selected_existing_number_and_defaults_to_zero(
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
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList

        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        source, volume = (window.requireCurrentSource(), window.requireVolume())
        for number, offset in ((0, 0), (2, 5)):
            project = C_NumberedAnnotationsFixtures().new_project(window)
            project.add_polygon(
                3,
                C_PolygonAnnotation(
                    points=tuple(C_NumberedAnnotationsFixtures().polygon(offset))
                ),
            )
            project.save(source.annotation_path_for_index(number))
        window.setInternalLoadingSource(source)
        window.volume_loaded(volume)
        assert window.getAnnotationIndex() == 0
        assert window.requireProject().annotation(3).getPolygon(
            0
        ).getPoints() == C_PointList(tuple(C_NumberedAnnotationsFixtures().polygon()))
        window.set_annotation_index(2)
        window.setInternalLoadingSource(source)
        window.volume_loaded(volume)
        assert window.getAnnotationIndexSpin().value() == 2
        assert window.getProjectPath() == source.annotation_path_for_index(2)
        assert window.requireProject().annotation(3).getPolygon(
            0
        ).getPoints() == C_PointList(tuple(C_NumberedAnnotationsFixtures().polygon(5)))

    # 验证非零编号只有空备份时会清理它，不恢复空文件。
    def test_empty_numbered_backup_is_removed_when_opened_without_primary(
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
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        path = window.requireCurrentSource().annotation_path_for_index(2)
        project = C_NumberedAnnotationsFixtures().new_project(window)
        project.set_completed(3, True)
        project.save(path)
        project.save(path)
        path.unlink()
        assert C_FilePath(f"{path}.bak").is_file()
        assert window.set_annotation_index(2)
        assert window.requireProject().annotation(3).getCompleted()
        C_NumberedAnnotationsFixtures().assert_no_sidecars(path)

    # 验证观察模式不仅禁用输入框，也拒绝程序直接切换编号。
    def test_programmatic_number_change_is_blocked_in_observation(
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
        monkeypatch: MonkeyPatch,
    ) -> None:
        from med_image_seg.Concrete.Domain.Annotations.C_PolygonAnnotation import (
            C_PolygonAnnotation,
        )
        from med_image_seg.Concrete.Domain.Geometry.C_PointList import C_PointList

        from .C_NumberedAnnotationsFixtures import C_NumberedAnnotationsFixtures

        window.add_polygon(
            C_PointList(C_NumberedAnnotationsFixtures().polygon()), "add"
        )
        target = window.requireCurrentSource().annotation_path_for_index(2)
        project = C_NumberedAnnotationsFixtures().new_project(window)
        project.add_polygon(
            3,
            C_PolygonAnnotation(
                points=tuple(C_NumberedAnnotationsFixtures().polygon(5))
            ),
        )
        project.save(target)
        window.getObserveRadio().setChecked(True)
        original_project, original_mask = (
            window.requireProject(),
            window.requireInternalObservationMask(),
        )
        original_position = window.getObservationPosition()
        original_path = window.requireProjectPath()
        errors = []

        # 拦截观察模式打开其他编号项目的调用。
        def fail(*args, **kwargs):
            pytest.fail("Read-only mode must not open another annotation")

        monkeypatch.setattr(window, "_open_annotation_project", fail)
        monkeypatch.setattr(
            QMessageBox, "critical", lambda *args: errors.append(args[2])
        )
        assert not window.set_annotation_index(2)
        assert errors == []
        assert window.getProject() is original_project
        assert window.getInternalObservationMask() is original_mask
        assert window.getProjectPath() == original_path
        assert window.getObservationPosition() == original_position
        assert (
            window.getAnnotationIndex() == window.getAnnotationIndexSpin().value() == 0
        )
        assert window.getReadOnly()
        assert all(
            view.getHost().isEnabled() for view in window.iterObservationWindows()
        )
        assert all(not control.isEnabled() for control in window.iterEditingControls())

    # 把 pytest 临时目录转换为路径接口，供业务测试复用。
    @pytest.fixture(name="tmp_path")
    def _adapt_path(self, tmp_path: Path) -> I_FilePath:
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        return C_FilePath(tmp_path)
