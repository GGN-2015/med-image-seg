from __future__ import annotations

from collections.abc import Iterable
from contextlib import AbstractContextManager
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QGraphicsPathItem

from ....Abstract.Domain.Annotations.I_MutableAnnotationProject import (
    I_MutableAnnotationProject,
)
from ....Abstract.Domain.Collections.I_ImageCollection import I_ImageCollection
from ....Abstract.Domain.Collections.I_MutableImageCollection import (
    I_MutableImageCollection,
)
from ....Abstract.Domain.Geometry.I_PointList import I_PointList
from ....Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
from ....Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
from ....Abstract.Domain.ViewState.I_ExternalMaskViewState import (
    I_ExternalMaskViewState,
)
from ....Abstract.Presentation.Canvas.T_MutableSliceCanvas import T_MutableSliceCanvas
from ....Abstract.Presentation.Canvas.T_MutableVertexHandle import T_MutableVertexHandle
from ....Abstract.Presentation.Loading.T_MutableExternalMaskLoadThread import (
    T_MutableExternalMaskLoadThread,
)
from ....Abstract.Presentation.Loading.T_MutableVolumeLoadThread import (
    T_MutableVolumeLoadThread,
)
from ....Abstract.Presentation.Navigation import (
    T_MutableAnnotationIndexSpinBox,
)
from ....Abstract.Presentation.Navigation.T_MutableMaskCoverageBar import (
    T_MutableMaskCoverageBar,
)
from ....Abstract.Presentation.Observation import (
    T_MutableOrthogonalSliceWindow,
)
from ....Abstract.Presentation.Progress.I_ProgressDialogSettings import (
    I_ProgressDialogSettings,
)
from ....Abstract.Presentation.Window.T_MutableAnnotationMainWindow import (
    T_MutableAnnotationMainWindow,
)
from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
from ..Metaclasses.C_Qt_AbcMeta import C_Qt_AbcMeta

if TYPE_CHECKING:
    from ....Abstract.Domain.Annotations.I_MutableAnnotationProject import (
        I_MutableAnnotationProject,
    )
    from ....Abstract.Domain.Collections.I_MutableImageCollection import (
        I_MutableImageCollection,
    )
    from ....Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
    from ....Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from ....Abstract.Domain.ViewState.I_ExternalMaskViewState import (
        I_ExternalMaskViewState,
    )
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
import operator
from collections.abc import Iterator
from typing import final

import numpy as np
from numpy.typing import NDArray
from PySide6.QtCore import QPointF, QRectF, Qt, QThread, QTime, QTimer, SignalInstance
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
    QHideEvent,
    QShortcut,
    QShowEvent,
)
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QGraphicsEllipseItem,
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


# 协调影像、当前项目与三视图状态，将布局、加载和导出委托给服务对象。
@final
class C_Qt_AnnotationMainWindow(
    QMainWindow,
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
    metaclass=C_Qt_AbcMeta,
):
    # 返回当前中英界面语言代码。
    def getLanguage(self) -> str:
        return self._state_language

    # 记录当前中英界面语言代码。
    def setLanguage(self, value: str) -> None:
        self._state_language = value

    # 通过集合接口访问影像，支持按数量、索引和指纹查询。
    def getSources(self) -> I_MutableImageCollection:
        return self._state_sources

    # 设置应用使用的影像集合接口，不暴露集合内部的存储结构。
    def setSources(self, value: I_MutableImageCollection) -> None:
        self._state_sources = value

    # 返回当前已载入的影像源。
    def getCurrentSource(self) -> I_ImageSource | None:
        return self._state_current_source

    # 记录当前已载入的影像源。
    def setCurrentSource(self, value: I_ImageSource | None) -> None:
        self._state_current_source = value

    # 返回当前已加载的医学影像体积。
    def getVolume(self) -> I_MedicalVolume | None:
        return self._state_volume

    # 记录当前已加载的医学影像体积。
    def setVolume(self, value: I_MedicalVolume | None) -> None:
        self._state_volume = value

    # 返回当前编号的标注项目。
    def getProject(self) -> I_MutableAnnotationProject | None:
        return self._state_project

    # 记录当前编号的标注项目。
    def setProject(self, value: I_MutableAnnotationProject | None) -> None:
        self._state_project = value

    # 返回当前编号对应的 JSON 标注路径。
    def getProjectPath(self) -> I_FilePath | None:
        return self._state_project_path

    # 记录当前编号对应的 JSON 标注路径。
    def setProjectPath(self, value: I_FilePath | None) -> None:
        self._state_project_path = value

    # 返回当前标注文件编号。
    def getAnnotationIndex(self) -> int:
        return self._state_annotation_index

    # 记录当前标注文件编号。
    def setAnnotationIndex(self, value: int) -> None:
        self._state_annotation_index = value

    # 返回标注编号切换是否正在进行。
    def getInternalSwitchingAnnotation(self) -> bool:
        return self._state_switching_annotation

    # 记录标注编号切换是否正在进行。
    def setInternalSwitchingAnnotation(self, value: bool) -> None:
        self._state_switching_annotation = value

    # 返回当前 LP 切片编号。
    def getCurrentSlice(self) -> int:
        return self._state_current_slice

    # 记录当前 LP 切片编号。
    def setCurrentSlice(self, value: int) -> None:
        self._state_current_slice = value

    # 返回影像后台加载线程。
    def getLoadThread(
        self,
    ) -> T_MutableVolumeLoadThread[QThread, SignalInstance] | None:
        return self._state_load_thread

    # 记录影像后台加载线程。
    def setLoadThread(
        self, value: T_MutableVolumeLoadThread[QThread, SignalInstance] | None
    ) -> None:
        self._state_load_thread = value

    # 返回后台正在加载的影像源。
    def getInternalLoadingSource(self) -> I_ImageSource | None:
        return self._state_loading_source

    # 记录后台正在加载的影像源。
    def setInternalLoadingSource(self, value: I_ImageSource | None) -> None:
        self._state_loading_source = value

    # 返回影像加载进度框。
    def getLoadingDialog(self) -> QProgressDialog | None:
        return self._state_loading_dialog

    # 记录影像加载进度框。
    def setLoadingDialog(self, value: QProgressDialog | None) -> None:
        self._state_loading_dialog = value

    # 返回当前锁定操作的进度窗口，让闭合和导出期间的保存均可在后台执行。
    def getBusyProgressDialog(self) -> QProgressDialog | None:
        return self._state_busy_progress_dialog

    # 登记当前耗时操作的进度窗口，任务结束后解除后台执行标记。
    def setBusyProgressDialog(self, value: QProgressDialog | None) -> None:
        self._state_busy_progress_dialog = value

    # 返回最近一次影像加载错误。
    def getInternalLoadError(self) -> str | None:
        return self._state_load_error

    # 记录最近一次影像加载错误。
    def setInternalLoadError(self, value: str | None) -> None:
        self._state_load_error = value

    # 返回项目是否存在尚未落盘的修改。
    def getInternalDirty(self) -> bool:
        return self._state_dirty

    # 记录项目是否存在尚未落盘的修改。
    def setInternalDirty(self, value: bool) -> None:
        self._state_dirty = value

    # 返回多边形闭合流程是否正在执行。
    def getInternalClosingPolygon(self) -> bool:
        return self._state_closing_polygon

    # 记录多边形闭合流程是否正在执行。
    def setInternalClosingPolygon(self, value: bool) -> None:
        self._state_closing_polygon = value

    # 返回掩码区间缓存是否需要重算。
    def getInternalMaskCoverageDirty(self) -> bool:
        return self._state_mask_coverage_dirty

    # 记录掩码区间缓存是否需要重算。
    def setInternalMaskCoverageDirty(self, value: bool) -> None:
        self._state_mask_coverage_dirty = value

    # 返回是否处于禁止编辑的观察状态。
    def getReadOnly(self) -> bool:
        return self._state_read_only

    # 记录是否处于禁止编辑的观察状态。
    def setReadOnly(self, value: bool) -> None:
        self._state_read_only = value

    # 返回 LP、PS、SL 三个视图共享的体素交点。
    def getObservationPosition(self) -> tuple[int, int, int]:
        return self._state_observation_position

    # 记录三个截面共用的 LPS 体素交点。
    def setObservationPosition(self, value: tuple[int, int, int]) -> None:
        self._state_observation_position = value

    # 返回观察模式复用的三维掩码缓存。
    def getInternalObservationMask(self) -> NDArray[np.uint8] | None:
        return self._state_observation_mask

    # 记录观察模式复用的三维掩码缓存。
    def setInternalObservationMask(self, value: NDArray[np.uint8] | None) -> None:
        self._state_observation_mask = value

    # 返回进入观察模式前的插值显示设置。
    def getInternalEditingInterpolationVisible(self) -> bool:
        return self._state_editing_interpolation_visible

    # 记录进入观察模式前的插值显示设置。
    def setInternalEditingInterpolationVisible(self, value: bool) -> None:
        self._state_editing_interpolation_visible = value

    # 返回与参考影像对齐的外置掩码。
    def getExternalMask(self) -> NDArray[np.uint8] | None:
        return self._state_external_mask

    # 记录与参考影像对齐的外置掩码。
    def setExternalMask(self, value: NDArray[np.uint8] | None) -> None:
        self._state_external_mask = value

    # 返回当前外置掩码文件路径。
    def getExternalMaskPath(self) -> I_FilePath | None:
        return self._state_external_mask_path

    # 记录当前外置掩码文件路径。
    def setExternalMaskPath(self, value: I_FilePath | None) -> None:
        self._state_external_mask_path = value

    # 返回外置掩码后台加载线程。
    def getExternalMaskThread(
        self,
    ) -> T_MutableExternalMaskLoadThread[QThread, SignalInstance] | None:
        return self._state_external_mask_thread

    # 记录外置掩码后台加载线程。
    def setExternalMaskThread(
        self, value: T_MutableExternalMaskLoadThread[QThread, SignalInstance] | None
    ) -> None:
        self._state_external_mask_thread = value

    # 返回外置掩码加载进度框。
    def getExternalLoadingDialog(self) -> QProgressDialog | None:
        return self._state_external_loading_dialog

    # 记录外置掩码加载进度框。
    def setExternalLoadingDialog(self, value: QProgressDialog | None) -> None:
        self._state_external_loading_dialog = value

    # 返回进入外置掩码预览前保存的编辑状态。
    def getInternalExternalViewState(self) -> I_ExternalMaskViewState | None:
        return self._state_external_view_state

    # 记录进入外置掩码预览前保存的编辑状态。
    def setInternalExternalViewState(
        self, value: I_ExternalMaskViewState | None
    ) -> None:
        self._state_external_view_state = value

    # 返回最近一次外置掩码加载错误。
    def getInternalExternalMaskError(self) -> str | None:
        return self._state_external_mask_error

    # 记录最近一次外置掩码加载错误。
    def setInternalExternalMaskError(self, value: str | None) -> None:
        self._state_external_mask_error = value

    # 返回自动保存定时器。
    def getAutosaveTimer(self) -> QTimer:
        return self._state_autosave_timer

    # 记录自动保存定时器。
    def setAutosaveTimer(self, value: QTimer) -> None:
        self._state_autosave_timer = value

    # 返回掩码与标注导出工具栏。
    def getAnnotationToolbar(self) -> QToolBar:
        return self._state_annotation_toolbar

    # 记录掩码与标注导出工具栏。
    def setAnnotationToolbar(self, value: QToolBar) -> None:
        self._state_annotation_toolbar = value

    # 返回NIfTI 掩码导出动作。
    def getExportAction(self) -> QAction:
        return self._state_export_action

    # 记录NIfTI 掩码导出动作。
    def setExportAction(self, value: QAction) -> None:
        self._state_export_action = value

    # 返回UBD 掩码导出动作。
    def getExportUbdAction(self) -> QAction:
        return self._state_export_ubd_action

    # 记录UBD 掩码导出动作。
    def setExportUbdAction(self, value: QAction) -> None:
        self._state_export_ubd_action = value

    # 返回JSON 标注导出动作。
    def getExportJsonAction(self) -> QAction:
        return self._state_export_json_action

    # 记录JSON 标注导出动作。
    def setExportJsonAction(self, value: QAction) -> None:
        self._state_export_json_action = value

    # 返回影像集合标题。
    def getImageCollectionLabel(self) -> QLabel:
        return self._state_image_collection_label

    # 记录影像集合标题。
    def setImageCollectionLabel(self, value: QLabel) -> None:
        self._state_image_collection_label = value

    # 返回影像文件导入按钮。
    def getFileButton(self) -> QPushButton:
        return self._state_file_button

    # 记录影像文件导入按钮。
    def setFileButton(self, value: QPushButton) -> None:
        self._state_file_button = value

    # 返回DICOM 目录导入按钮。
    def getDicomButton(self) -> QPushButton:
        return self._state_dicom_button

    # 记录DICOM 目录导入按钮。
    def setDicomButton(self, value: QPushButton) -> None:
        self._state_dicom_button = value

    # 返回界面语言标签。
    def getLanguageLabel(self) -> QLabel:
        return self._state_language_label

    # 记录界面语言标签。
    def setLanguageLabel(self, value: QLabel) -> None:
        self._state_language_label = value

    # 返回界面语言选择框。
    def getLanguageCombo(self) -> QComboBox:
        return self._state_language_combo

    # 记录界面语言选择框。
    def setLanguageCombo(self, value: QComboBox) -> None:
        self._state_language_combo = value

    # 返回影像列表、画布及编辑面板的分隔器。
    def getSplitter(self) -> QSplitter:
        return self._state_splitter

    # 记录影像列表、画布及编辑面板的分隔器。
    def setSplitter(self, value: QSplitter) -> None:
        self._state_splitter = value

    # 返回已导入影像列表标题。
    def getImportedImagesLabel(self) -> QLabel:
        return self._state_imported_images_label

    # 记录已导入影像列表标题。
    def setImportedImagesLabel(self, value: QLabel) -> None:
        self._state_imported_images_label = value

    # 返回已导入影像列表控件。
    def getSourceList(self) -> QListWidget:
        return self._state_source_list

    # 记录已导入影像列表控件。
    def setSourceList(self, value: QListWidget) -> None:
        self._state_source_list = value

    # 返回标注网格间距标签。
    def getSpacingLabel(self) -> QLabel:
        return self._state_spacing_label

    # 记录标注网格间距标签。
    def setSpacingLabel(self, value: QLabel) -> None:
        self._state_spacing_label = value

    # 返回标注网格间距输入框。
    def getSpacingSpin(self) -> QDoubleSpinBox:
        return self._state_spacing_spin

    # 记录标注网格间距输入框。
    def setSpacingSpin(self, value: QDoubleSpinBox) -> None:
        self._state_spacing_spin = value

    # 返回载入选中影像按钮。
    def getLoadButton(self) -> QPushButton:
        return self._state_load_button

    # 记录载入选中影像按钮。
    def setLoadButton(self, value: QPushButton) -> None:
        self._state_load_button = value

    # 返回关闭当前影像并移除导入项的按钮。
    def getUnloadImageButton(self) -> QPushButton:
        return self._state_unload_image_button

    # 登记卸载影像按钮，供加载和模式切换统一管理状态。
    def setUnloadImageButton(self, value: QPushButton) -> None:
        self._state_unload_image_button = value

    # 返回切片画布。
    def getCanvas(
        self,
    ) -> T_MutableSliceCanvas[
        QGraphicsView,
        QPointF,
        QRectF,
        QGraphicsPixmapItem,
        QGraphicsPathItem,
        QGraphicsPolygonItem,
        T_MutableVertexHandle[QGraphicsEllipseItem],
        SignalInstance,
    ]:
        return self._state_canvas

    # 记录切片画布。
    def setCanvas(
        self,
        value: T_MutableSliceCanvas[
            QGraphicsView,
            QPointF,
            QRectF,
            QGraphicsPixmapItem,
            QGraphicsPathItem,
            QGraphicsPolygonItem,
            T_MutableVertexHandle[QGraphicsEllipseItem],
            SignalInstance,
        ],
    ) -> None:
        self._state_canvas = value

    # 返回上一层按钮。
    def getPreviousButton(self) -> QPushButton:
        return self._state_previous_button

    # 记录上一层按钮。
    def setPreviousButton(self, value: QPushButton) -> None:
        self._state_previous_button = value

    # 返回下一层按钮。
    def getNextButton(self) -> QPushButton:
        return self._state_next_button

    # 记录下一层按钮。
    def setNextButton(self, value: QPushButton) -> None:
        self._state_next_button = value

    # 返回上一个有轮廓层按钮。
    def getPreviousLabeledButton(self) -> QPushButton:
        return self._state_previous_labeled_button

    # 记录上一个有轮廓层按钮。
    def setPreviousLabeledButton(self, value: QPushButton) -> None:
        self._state_previous_labeled_button = value

    # 返回下一个有轮廓层按钮。
    def getNextLabeledButton(self) -> QPushButton:
        return self._state_next_labeled_button

    # 记录下一个有轮廓层按钮。
    def setNextLabeledButton(self, value: QPushButton) -> None:
        self._state_next_labeled_button = value

    # 返回当前切片位置滑块。
    def getSliceSlider(self) -> QSlider:
        return self._state_slice_slider

    # 记录当前切片位置滑块。
    def setSliceSlider(self, value: QSlider) -> None:
        self._state_slice_slider = value

    # 返回逐层掩码存在性区间条。
    def getMaskCoverageBar(self) -> T_MutableMaskCoverageBar[QWidget, QSlider]:
        return self._state_mask_coverage_bar

    # 记录逐层掩码存在性区间条。
    def setMaskCoverageBar(
        self, value: T_MutableMaskCoverageBar[QWidget, QSlider]
    ) -> None:
        self._state_mask_coverage_bar = value

    # 返回当前切片编号输入框。
    def getSliceSpin(self) -> QSpinBox:
        return self._state_slice_spin

    # 记录当前切片编号输入框。
    def setSliceSpin(self, value: QSpinBox) -> None:
        self._state_slice_spin = value

    # 返回标注编号标签。
    def getAnnotationIndexLabel(self) -> QLabel:
        return self._state_annotation_index_label

    # 记录标注编号标签。
    def setAnnotationIndexLabel(self, value: QLabel) -> None:
        self._state_annotation_index_label = value

    # 返回标注编号输入框。
    def getAnnotationIndexSpin(
        self,
    ) -> T_MutableAnnotationIndexSpinBox[QAbstractSpinBox, SignalInstance]:
        return self._state_annotation_index_spin

    # 记录标注编号输入框。
    def setAnnotationIndexSpin(
        self, value: T_MutableAnnotationIndexSpinBox[QAbstractSpinBox, SignalInstance]
    ) -> None:
        self._state_annotation_index_spin = value

    # 返回多边形模式选择框。
    def getModeGroup(self) -> QGroupBox:
        return self._state_mode_group

    # 记录多边形模式选择框。
    def setModeGroup(self, value: QGroupBox) -> None:
        self._state_mode_group = value

    # 返回添加区域单选按钮。
    def getAddRadio(self) -> QRadioButton:
        return self._state_add_radio

    # 记录添加区域单选按钮。
    def setAddRadio(self, value: QRadioButton) -> None:
        self._state_add_radio = value

    # 返回擦除区域单选按钮。
    def getEraseRadio(self) -> QRadioButton:
        return self._state_erase_radio

    # 记录擦除区域单选按钮。
    def setEraseRadio(self, value: QRadioButton) -> None:
        self._state_erase_radio = value

    # 返回只读观察模式单选按钮。
    def getObserveRadio(self) -> QRadioButton:
        return self._state_observe_radio

    # 记录只读观察模式单选按钮。
    def setObserveRadio(self, value: QRadioButton) -> None:
        self._state_observe_radio = value

    # 返回观察模式状态标签。
    def getObservationStatus(self) -> QLabel:
        return self._state_observation_status

    # 记录观察模式状态标签。
    def setObservationStatus(self, value: QLabel) -> None:
        self._state_observation_status = value

    # 返回闭合当前轮廓按钮。
    def getFinishButton(self) -> QPushButton:
        return self._state_finish_button

    # 记录闭合当前轮廓按钮。
    def setFinishButton(self, value: QPushButton) -> None:
        self._state_finish_button = value

    # 返回取消当前轮廓按钮。
    def getCancelButton(self) -> QPushButton:
        return self._state_cancel_button

    # 记录取消当前轮廓按钮。
    def setCancelButton(self, value: QPushButton) -> None:
        self._state_cancel_button = value

    # 返回删除最近编辑轮廓按钮。
    def getDeleteButton(self) -> QPushButton:
        return self._state_delete_button

    # 记录删除最近编辑轮廓按钮。
    def setDeleteButton(self, value: QPushButton) -> None:
        self._state_delete_button = value

    # 返回复制上一层标注按钮。
    def getCopyButton(self) -> QPushButton:
        return self._state_copy_button

    # 记录复制上一层标注按钮。
    def setCopyButton(self, value: QPushButton) -> None:
        self._state_copy_button = value

    # 返回清空当前层按钮。
    def getClearButton(self) -> QPushButton:
        return self._state_clear_button

    # 记录清空当前层按钮。
    def setClearButton(self, value: QPushButton) -> None:
        self._state_clear_button = value

    # 返回当前层复核复选框。
    def getCompletedCheck(self) -> QCheckBox:
        return self._state_completed_check

    # 记录当前层复核复选框。
    def setCompletedCheck(self, value: QCheckBox) -> None:
        self._state_completed_check = value

    # 返回当前层强制空掩码复选框。
    def getForceEmptyCheck(self) -> QCheckBox:
        return self._state_force_empty_check

    # 记录当前层强制空掩码复选框。
    def setForceEmptyCheck(self, value: QCheckBox) -> None:
        self._state_force_empty_check = value

    # 返回下一未完成层按钮。
    def getNextIncompleteButton(self) -> QPushButton:
        return self._state_next_incomplete_button

    # 记录下一未完成层按钮。
    def setNextIncompleteButton(self, value: QPushButton) -> None:
        self._state_next_incomplete_button = value

    # 返回切片复核进度标签。
    def getReviewProgress(self) -> QProgressBar:
        return self._state_review_progress

    # 记录切片复核进度标签。
    def setReviewProgress(self, value: QProgressBar) -> None:
        self._state_review_progress = value

    # 返回显示自动插值复选框。
    def getShowInterpolation(self) -> QCheckBox:
        return self._state_show_interpolation

    # 记录显示自动插值复选框。
    def setShowInterpolation(self, value: QCheckBox) -> None:
        self._state_show_interpolation = value

    # 返回当前层插值状态标签。
    def getInterpolationStatus(self) -> QLabel:
        return self._state_interpolation_status

    # 记录当前层插值状态标签。
    def setInterpolationStatus(self, value: QLabel) -> None:
        self._state_interpolation_status = value

    # 返回自动保存状态标签。
    def getAutosaveStatus(self) -> QLabel:
        return self._state_autosave_status

    # 记录自动保存状态标签。
    def setAutosaveStatus(self, value: QLabel) -> None:
        self._state_autosave_status = value

    # 返回窗宽窗位设置框。
    def getWindowGroup(self) -> QGroupBox:
        return self._state_window_group

    # 记录窗宽窗位设置框。
    def setWindowGroup(self, value: QGroupBox) -> None:
        self._state_window_group = value

    # 返回窗位标签。
    def getLevelLabel(self) -> QLabel:
        return self._state_level_label

    # 记录窗位标签。
    def setLevelLabel(self, value: QLabel) -> None:
        self._state_level_label = value

    # 返回窗位输入框。
    def getLevelSpin(self) -> QDoubleSpinBox:
        return self._state_level_spin

    # 记录窗位输入框。
    def setLevelSpin(self, value: QDoubleSpinBox) -> None:
        self._state_level_spin = value

    # 返回窗宽标签。
    def getWidthLabel(self) -> QLabel:
        return self._state_width_label

    # 记录窗宽标签。
    def setWidthLabel(self, value: QLabel) -> None:
        self._state_width_label = value

    # 返回窗宽输入框。
    def getWidthSpin(self) -> QDoubleSpinBox:
        return self._state_width_spin

    # 记录窗宽输入框。
    def setWidthSpin(self, value: QDoubleSpinBox) -> None:
        self._state_width_spin = value

    # 返回载入外置掩码按钮。
    def getLoadExternalMaskButton(self) -> QPushButton:
        return self._state_load_external_mask_button

    # 记录载入外置掩码按钮。
    def setLoadExternalMaskButton(self, value: QPushButton) -> None:
        self._state_load_external_mask_button = value

    # 返回卸载外置掩码按钮。
    def getUnloadExternalMaskButton(self) -> QPushButton:
        return self._state_unload_external_mask_button

    # 记录卸载外置掩码按钮。
    def setUnloadExternalMaskButton(self, value: QPushButton) -> None:
        self._state_unload_external_mask_button = value

    # 返回编辑操作提示标签。
    def getHintLabel(self) -> QLabel:
        return self._state_hint_label

    # 记录编辑操作提示标签。
    def setHintLabel(self, value: QLabel) -> None:
        self._state_hint_label = value

    # 逐项登记编辑控件，复制输入而不保留外部容器。
    def setEditingControls(self, value: Iterable[QWidget]) -> None:
        self._state_editing_controls = list(value)

    # 复制编辑面板控件集合，供加载期间保存及恢复启用状态。
    def setEditorWidgets(self, value: Iterable[QWidget]) -> None:
        self._state_editor_widgets = list(value)

    # 逐项登记编辑快捷键，供只读和忙碌状态统一管理。
    def setEditingShortcuts(self, value: Iterable[QShortcut]) -> None:
        self._state_editing_shortcuts = list(value)

    # 初始化项目及加载状态，装配主界面、服务和快捷键。
    def __init__(
        self,
        *,
        sources: list[I_ImageSource] | None = None,
        spacing_mm: float = 0.8,
        language: str = "en",
    ) -> None:
        from ...Domain.Collections.C_ImageCollection import C_ImageCollection
        from ...Localization.C_Localizer import C_Localizer
        from ..Appearance.C_Qt_FontSetup import C_Qt_FontSetup

        super().__init__()
        C_Qt_FontSetup().configure()
        self.setLanguage(C_Localizer().normalize_language(language))
        self.resize(1500, 920)
        self.setSources(C_ImageCollection(sources or []))
        self.setCurrentSource(None)
        self.setVolume(None)
        self.setProject(None)
        self.setProjectPath(None)
        self.setAnnotationIndex(0)
        self.setInternalSwitchingAnnotation(False)
        self.setCurrentSlice(0)
        self.setLoadThread(None)
        self.setInternalLoadingSource(None)
        self.setLoadingDialog(None)
        self.setBusyProgressDialog(None)
        self.setInternalLoadError(None)
        self.setInternalDirty(False)
        self.setInternalClosingPolygon(False)
        self.setInternalMaskCoverageDirty(True)
        self.setReadOnly(False)
        self.setObservationPosition((0, 0, 0))
        self.setInternalObservationMask(None)
        self.clearObservationWindows()
        self.setInternalEditingInterpolationVisible(True)
        self.setExternalMask(None)
        self.setExternalMaskPath(None)
        self.setExternalMaskThread(None)
        self.setExternalLoadingDialog(None)
        self.setInternalExternalViewState(None)
        self.setInternalExternalMaskError(None)
        self.clearExternalLoadingWidgetStates()
        self.clearExternalLoadingShortcutStates()
        self._build_ui(spacing_mm)
        self._bind_shortcuts()
        self._refresh_source_list()
        self.setAutosaveTimer(QTimer(self))
        self.getAutosaveTimer().setInterval(10000)
        self.getAutosaveTimer().timeout.connect(self.autosave_if_needed)
        self.getAutosaveTimer().start()
        if len(self.getSources()):
            QTimer.singleShot(0, self.load_first_source)

    # 构建影像列表、主画布和右侧编辑面板，登记供状态切换使用的控件。
    def _build_ui(self, spacing_mm: float) -> None:
        from ..Layout.C_Qt_LayoutService import C_Qt_LayoutService

        return C_Qt_LayoutService().build_ui(self, spacing_mm)

    # 按消息键翻译文案并填充格式参数。
    def _text(self, key: str, **values: str | int | float) -> str:
        from ...Localization.C_Localizer import C_Localizer

        return C_Localizer().translate(key, self.getLanguage(), **values)

    # 返回外置掩码预览是否启用。
    def getExternalPreviewActive(self) -> bool:
        return self.getInternalExternalViewState() is not None

    # 根据当前模式选择操作提示键，区分编辑与只读观察。
    def _hint_key(self) -> str:
        if self.getExternalPreviewActive():
            return "external_mask_hint"
        return "observation_hint" if self.getReadOnly() else "hint"

    # 保存编辑状态并进入只读模式，为外置掩码选择和加载做准备。
    def _begin_external_preview(self) -> bool:
        from ..Interaction.C_Qt_PreviewService import C_Qt_PreviewService

        return C_Qt_PreviewService().begin_external_preview(self)

    # 进入只读观察模式后选择 NIfTI 或 UBD 掩码文件。
    def choose_external_mask(self) -> None:
        from ...Storage.Paths.C_FilePath import C_FilePath

        if not self._begin_external_preview():
            return
        try:
            selected, _ = QFileDialog.getOpenFileName(
                self,
                self._text("external_mask_choose"),
                str(self.requireCurrentSource().getPath().getParent()),
                self._text("external_mask_filter"),
            )
        except Exception as exc:
            self.unload_external_mask()
            QMessageBox.critical(self, self._text("external_mask_failed"), str(exc))
            return
        if not selected:
            self.unload_external_mask()
            return
        self._start_external_mask_load(C_FilePath(selected))

    # 进入外置掩码加载流程；已有预览或忙碌时拒绝重复操作。
    def load_external_mask(self, path: str | I_FilePath) -> bool:
        from ...Storage.Paths.C_FilePath import C_FilePath

        if not self._begin_external_preview():
            return False
        self._start_external_mask_load(C_FilePath(path))
        return True

    # 在后台读取选中的外置掩码，并锁定相关操作直到结果返回。
    def _start_external_mask_load(self, path: I_FilePath) -> None:
        from ..Interaction.C_Qt_PreviewService import C_Qt_PreviewService

        return C_Qt_PreviewService().start_external_mask_load(self, path)

    # 接收已对齐的外置掩码，更新三个截面及绿色存在性区间。
    def external_mask_loaded(
        self, mask: NDArray[np.uint8], presence: NDArray[np.bool_]
    ) -> None:
        if (
            self.getVolume() is None
            or mask.shape != self.requireVolume().getData().shape
        ):
            self.setInternalExternalMaskError(self._text("external_mask_shape_error"))
            return
        self.setExternalMask(mask)
        self.getMaskCoverageBar().set_presence(presence)
        self.refresh_slice()

    # 记录后台加载错误，供线程结束后显示提示并恢复编辑状态。
    def external_mask_load_failed(self, message: str) -> None:
        self.setInternalExternalMaskError(message)

    # 清理后台线程和加载提示，按成功或失败结果恢复可操作状态。
    def external_mask_thread_finished(self) -> None:
        thread = self.getExternalMaskThread()
        self.setExternalMaskThread(None)
        if thread is not None:
            thread.getHost().deleteLater()
        if self.getExternalLoadingDialog() is not None:
            if self.getInternalExternalMaskError() is None:
                self.requireExternalLoadingDialog().accept()
            else:
                self.requireExternalLoadingDialog().reject()
            self.requireExternalLoadingDialog().deleteLater()
            self.setExternalLoadingDialog(None)
        for _state_index in range(self.getExternalLoadingWidgetCount()):
            widget = self.getExternalLoadingWidget(_state_index)
            enabled = self.getExternalLoadingWidgetEnabled(_state_index)
            widget.setEnabled(enabled)
        for _state_index in range(self.getExternalLoadingShortcutCount()):
            shortcut = self.getExternalLoadingShortcut(_state_index)
            enabled = self.getExternalLoadingShortcutEnabled(_state_index)
            shortcut.setEnabled(enabled)
        self.clearExternalLoadingWidgetStates()
        self.clearExternalLoadingShortcutStates()
        QApplication.restoreOverrideCursor()
        if self.getInternalExternalMaskError() is not None:
            error = self.requireInternalExternalMaskError()
            self.unload_external_mask()
            QMessageBox.critical(self, self._text("external_mask_failed"), error)
            return
        self._apply_mode_ui()
        self.statusBar().showMessage(
            self._text("external_mask_loaded", path=str(self.getExternalMaskPath()))
        )

    # 移除外置掩码，恢复原编号、切片、编辑模式和插值显示设置。
    def unload_external_mask(self) -> bool:
        state = self.getInternalExternalViewState()
        if state is None or self.getExternalMaskThread() is not None:
            return False
        with self._polygon_busy_ui("external_mask_unloading"):
            self.setExternalMask(None)
            self.setExternalMaskPath(None)
            self.setInternalExternalViewState(None)
            self.setAnnotationIndex(state.getAnnotationIndex())
            self._sync_annotation_index_spin()
            self.setObservationPosition(state.getPosition())
            self.setCurrentSlice(state.getPosition()[2])
            self.getMaskCoverageBar().set_presence(state.getCoverage())
            self.setInternalMaskCoverageDirty(False)
            radio = {
                "add": self.getAddRadio(),
                "erase": self.getEraseRadio(),
                "observe": self.getObserveRadio(),
            }[state.getMode()]
            radio.setChecked(True)
            self._apply_mode_ui()
            self.set_slice(state.getPosition()[2])
            self._show_annotation_path()
        if state.getAutosaveActive():
            self.getAutosaveTimer().start()
        self._apply_mode_ui()
        self.statusBar().showMessage(self._text("external_mask_unloaded"))
        return True

    # 读取语言选择项并更新界面文案，无需重新启动。
    def _language_changed(self, index: int) -> None:
        language = self.getLanguageCombo().itemData(index)
        if language is not None:
            self.set_language(str(language))

    # 规范语言代码并刷新所有中英界面文案。
    def set_language(self, language: str) -> None:
        from ...Localization.C_Localizer import C_Localizer

        self.setLanguage(C_Localizer().normalize_language(language))
        combo_index = self.getLanguageCombo().findData(self.getLanguage())
        if combo_index >= 0 and combo_index != self.getLanguageCombo().currentIndex():
            self.getLanguageCombo().blockSignals(True)
            self.getLanguageCombo().setCurrentIndex(combo_index)
            self.getLanguageCombo().blockSignals(False)
        self._retranslate_ui()

    # 根据当前语言更新标题、按钮、状态及操作提示文本。
    def _retranslate_ui(self) -> None:
        from ..Layout.C_Qt_LayoutService import C_Qt_LayoutService

        return C_Qt_LayoutService().retranslate_ui(self)

    # 把编辑和切片导航快捷键连接到对应动作，并登记可禁用项。
    def _bind_shortcuts(self) -> None:
        from ..Layout.C_Qt_LayoutService import C_Qt_LayoutService

        return C_Qt_LayoutService().bind_shortcuts(self)

    # 按影像集合顺序重建列表，并保留来源对象与列表项的关联。
    def _refresh_source_list(self) -> None:
        from ..Layout.C_Qt_LayoutService import C_Qt_LayoutService

        return C_Qt_LayoutService().refresh_source_list(self)

    # 批量导入影像，刷新列表并返回应用维护的影像集合接口。
    def add_sources(self, paths: Iterable[str | I_FilePath]) -> I_ImageCollection:
        from ...Domain.Collections.C_ImageCollection import C_ImageCollection

        added: list[I_ImageSource] = []
        errors: list[str] = []
        previous_count = len(self.getSources())
        for path in paths:
            try:
                source = self.getSources().add(path)
            except (OSError, ValueError) as exc:
                errors.append(f"{path}: {exc}")
            else:
                added.append(source)
        self._refresh_source_list()
        if len(self.getSources()) > previous_count:
            self.statusBar().showMessage(
                self._text("sources_added", count=len(self.getSources()))
            )
        if errors:
            QMessageBox.warning(
                self, self._text("partial_import_title"), "\n".join(errors)
            )
        return C_ImageCollection(added)

    # 选择一个或多个影像文件并加入可载入列表。
    def choose_image_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self, self._text("choose_images_title"), "", self._text("image_filter")
        )
        if files:
            self.add_sources(files)

    # 选择 DICOM 目录并将其加入影像集合。
    def choose_dicom_directory(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self, self._text("choose_dicom_title")
        )
        if directory:
            self.add_sources([directory])

    # 在存在初始影像时自动加载首项；空集合保持未载入状态。
    def load_first_source(self) -> None:
        if len(self.getSources()) and self.getLoadThread() is None:
            self.getSourceList().setCurrentRow(0)
            self.load_selected_source()

    # 读取影像列表当前选择的来源并启动后台加载。
    def load_selected_source(self) -> None:
        from ..Loading.C_Qt_VolumeLoadThread import C_Qt_VolumeLoadThread

        item = self.getSourceList().currentItem()
        if (
            item is None
            or self.getLoadThread() is not None
            or self.getExternalPreviewActive()
        ):
            return
        if not self.save_project(notify=True):
            return
        source = self.getSources()[int(item.data(Qt.ItemDataRole.UserRole))]
        self.setInternalLoadingSource(source)
        self.setInternalLoadError(None)
        self._show_loading(source)
        self.setLoadThread(
            C_Qt_VolumeLoadThread(
                source, self.getSpacingSpin().value(), self.getAnnotationIndex()
            )
        )
        self.requireLoadThread().getLoaded().connect(self.volume_loaded)
        self.requireLoadThread().getFailed().connect(self.volume_load_failed)
        self.requireLoadThread().getHost().finished.connect(self.load_thread_finished)
        self.requireLoadThread().getHost().start()

    # 把保存、状态清理和列表移除交给加载服务，不删除原始影像。
    def unload_imported_image(self) -> bool:
        from ..Persistence.C_Qt_LoadingService import C_Qt_LoadingService

        return C_Qt_LoadingService().unload_imported_image(self)

    # 禁用三个视图和编辑入口，并显示不可取消的加载进度提示。
    def _show_loading(self, source: I_ImageSource) -> None:
        from ..Persistence.C_Qt_LoadingService import C_Qt_LoadingService

        return C_Qt_LoadingService().show_loading(self, source)

    # 关闭加载提示并恢复先前控件状态，结束影像加载阶段。
    def _finish_loading_ui(self) -> None:
        from ..Persistence.C_Qt_LoadingService import C_Qt_LoadingService

        return C_Qt_LoadingService().finish_loading_ui(self)

    # 回收影像加载线程，关闭进度提示并恢复主窗口和附属视图。
    def load_thread_finished(self) -> None:
        self.setLoadThread(None)
        self._finish_loading_ui()
        if self.getInternalLoadError() is not None:
            QMessageBox.warning(
                self, self._text("load_failed_title"), self.requireInternalLoadError()
            )
            self.statusBar().showMessage(self._text("load_failed_status"))
        self.setInternalLoadingSource(None)

    # 保存后台影像读取错误，供任务结束时提示并恢复原状态。
    def volume_load_failed(self, message: str) -> None:
        self.setInternalLoadError(message)

    # 打开当前编号的 JSON 或备份；文件不存在时创建对应的新项目。
    def _open_annotation_project(
        self, source: I_ImageSource, volume: I_MedicalVolume, index: int
    ) -> tuple[I_MutableAnnotationProject, I_FilePath]:
        from ..Persistence.C_Qt_LoadingService import C_Qt_LoadingService

        return C_Qt_LoadingService().open_annotation_project(source, volume, index)

    # 以当前项目编号刷新输入框，避免信号递归触发项目切换。
    def _sync_annotation_index_spin(self) -> None:
        was_blocked = self.getAnnotationIndexSpin().getHost().blockSignals(True)
        self.getAnnotationIndexSpin().setValue(self.getAnnotationIndex())
        self.getAnnotationIndexSpin().getHost().blockSignals(was_blocked)

    # 显示当前编号及落盘路径，外置预览时明确标注保存已暂停。
    def _show_annotation_path(self) -> None:
        from ..Persistence.C_Qt_LoadingService import C_Qt_LoadingService

        return C_Qt_LoadingService().show_annotation_path(self)

    # 先保存原编号项目再切换标注文件；只读、忙碌或保存失败时拒绝切换。
    def set_annotation_index(self, index: int) -> bool:
        index = operator.index(index)
        if index < 0:
            raise ValueError("annotation index must be nonnegative")
        if (
            self.getInternalClosingPolygon()
            or self.getInternalSwitchingAnnotation()
            or self.getLoadThread() is not None
            or self.getReadOnly()
            or self.getExternalPreviewActive()
        ):
            self._sync_annotation_index_spin()
            return False
        if index == self.getAnnotationIndex():
            self._sync_annotation_index_spin()
            return True
        if (
            self.getProject() is None
            or self.getVolume() is None
            or self.getCurrentSource() is None
        ):
            self.setAnnotationIndex(index)
            self._sync_annotation_index_spin()
            return True
        self.setInternalSwitchingAnnotation(True)
        try:
            self.getCanvas().finish_polygon()
            if not self.save_project(notify=True, force=True):
                return False
            error = None
            with self._polygon_busy_ui("switching_annotation_status"):
                try:
                    project, path = self._open_annotation_project(
                        self.requireCurrentSource(), self.requireVolume(), index
                    )
                    observation_mask = (
                        project.to_mask(interpolate=True)
                        if self.getReadOnly()
                        else None
                    )
                except Exception as exc:
                    error = exc
                else:
                    self.getCanvas().cancel_polygon()
                    self.setProject(project)
                    self.setProjectPath(path)
                    self.setAnnotationIndex(index)
                    self.setInternalDirty(False)
                    self.setInternalMaskCoverageDirty(True)
                    self.setInternalObservationMask(observation_mask)
                    self._sync_annotation_index_spin()
                    self._show_annotation_path()
                    self.refresh_slice()
            if error is not None:
                QMessageBox.critical(
                    self, self._text("annotation_switch_failed"), str(error)
                )
                return False
            self.statusBar().showMessage(
                self._text(
                    "annotation_selected", index=index, path=str(self.getProjectPath())
                )
            )
            return True
        finally:
            self.setInternalSwitchingAnnotation(False)
            self._sync_annotation_index_spin()

    # 接收新影像并打开所选编号项目，成功准备掩码后更新视图。
    def volume_loaded(self, volume: I_MedicalVolume) -> None:
        if self.getExternalPreviewActive():
            return
        assert self.getInternalLoadingSource() is not None
        source = self.getInternalLoadingSource() or self.requireCurrentSource()
        try:
            project, project_path = self._open_annotation_project(
                source, volume, self.getAnnotationIndex()
            )
            observation_mask = (
                project.to_mask(interpolate=True) if self.getReadOnly() else None
            )
        except Exception as exc:
            self.setInternalLoadError(f"{type(exc).__name__}: {exc}")
            return
        self.setCurrentSource(source)
        self.setVolume(volume)
        self.setProjectPath(project_path)
        self.setProject(project)
        self.setInternalDirty(False)
        self.setInternalMaskCoverageDirty(True)
        self.setInternalObservationMask(observation_mask)
        self.setObservationPosition(tuple(size // 2 for size in volume.getData().shape))
        if np.allclose(volume.getSpacingMm(), (volume.getSpacingMm()[0],) * 3):
            self.getSpacingSpin().setValue(volume.getSpacingMm()[0])
        self.setCurrentSlice(self.getObservationPosition()[2])
        self._sync_annotation_index_spin()
        self._show_annotation_path()
        depth = volume.getData().shape[2]
        self.getSliceSlider().setRange(0, depth - 1)
        self.getSliceSpin().setRange(0, depth - 1)
        self.getReviewProgress().setRange(0, depth)
        finite = volume.getData()[np.isfinite(volume.getData())]
        stride = max(1, finite.size // 500000)
        low, high = np.percentile(finite[::stride], (1.0, 99.0))
        data_min, data_max = (float(finite.min()), float(finite.max()))
        self.getLevelSpin().setRange(data_min, data_max)
        self.getWidthSpin().setRange(1.0, max(1.0, 2 * (data_max - data_min)))
        self.getLevelSpin().setValue(float((low + high) / 2))
        self.getWidthSpin().setValue(float(max(1.0, high - low)))
        self.setCurrentSlice(depth // 2)
        self.getSliceSlider().setValue(self.getCurrentSlice())
        self.getSliceSpin().setValue(self.getCurrentSlice())
        self.refresh_slice()
        modality = str(volume.getMetadata().getText("modality", "UNKNOWN"))
        self.statusBar().showMessage(
            self._text(
                "loaded_status",
                name=self.requireCurrentSource().getDisplayName(),
                shape=str(volume.getData().shape),
                spacing=str(volume.getSpacingMm()),
                modality=modality,
            )
        )

    # 切换添加、擦除或观察模式；进入只读前先处理尚未闭合的草稿。
    def update_operation(self) -> None:
        observe = self.getObserveRadio().isChecked()
        if self.getExternalPreviewActive() and (not observe):
            self.getObserveRadio().setChecked(True)
            return
        if observe == self.getReadOnly():
            if not observe:
                self.getCanvas().set_operation(
                    "add" if self.getAddRadio().isChecked() else "erase"
                )
            return
        if observe:
            if self.getProject() is None:
                self.getAddRadio().setChecked(True)
                return
            self.getCanvas().finish_polygon()
            if not self.getExternalPreviewActive():
                try:
                    with self._polygon_busy_ui("preparing_observation"):
                        self.setInternalObservationMask(
                            self.requireProject().to_mask(interpolate=True)
                        )
                except Exception as exc:
                    radio = (
                        self.getAddRadio()
                        if self.getCanvas().getInternalOperation() == "add"
                        else self.getEraseRadio()
                    )
                    radio.setChecked(True)
                    QMessageBox.critical(
                        self, self._text("observation_failed"), str(exc)
                    )
                    return
            self.setInternalEditingInterpolationVisible(
                self.getShowInterpolation().isChecked()
            )
        self.setReadOnly(observe)
        self.getCanvas().set_read_only(observe)
        self.getShowInterpolation().blockSignals(True)
        self.getShowInterpolation().setChecked(
            True if observe else self.getInternalEditingInterpolationVisible()
        )
        self.getShowInterpolation().blockSignals(False)
        if observe:
            self._ensure_observation_windows()
        else:
            for view in self.iterObservationWindows():
                view.getHost().hide()
            self.getCanvas().set_crosshair(None, self.getObservationPosition())
            self.getCanvas().set_operation(
                "add" if self.getAddRadio().isChecked() else "erase"
            )
            self.setInternalObservationMask(None)
        self._apply_mode_ui()
        self.refresh_slice()

    # 根据编辑、观察或外置预览状态启用相应控件和快捷键。
    def _apply_mode_ui(self) -> None:
        from ..Layout.C_Qt_LayoutService import C_Qt_LayoutService

        return C_Qt_LayoutService().apply_mode_ui(self)

    # 按需创建 PS、SL 非模态窗口，避免重复打开同一截面。
    def _ensure_observation_windows(self) -> None:
        from ..Layout.C_Qt_LayoutService import C_Qt_LayoutService

        return C_Qt_LayoutService().ensure_observation_windows(self)

    # 把截面点击转换为共享体素交点，并同步其余截面的层号。
    def _observation_clicked(self, name: str, point: QPointF) -> None:
        from ..Interaction.C_Qt_InteractionService import C_Qt_InteractionService

        return C_Qt_InteractionService().observation_clicked(self, name, point)

    # 将某截面的固定轴设为指定层号，并同步其余视图的交点和参考线。
    def _set_observation_axis(self, name: str, index: int) -> None:
        from ..Interaction.C_Qt_InteractionService import C_Qt_InteractionService

        return C_Qt_InteractionService().set_observation_axis(self, name, index)

    # 按共享交点刷新 LP、PS、SL 切片、掩码和参考线。
    def _refresh_observation_views(self) -> None:
        from ..Interaction.C_Qt_PreviewService import C_Qt_PreviewService

        return C_Qt_PreviewService().refresh_observation_views(self)

    # 将当前 LP 层按窗宽窗位转换为显示灰度。
    def _windowed_slice(self) -> NDArray[np.uint8]:
        from ..Interaction.C_Qt_InteractionService import C_Qt_InteractionService

        return C_Qt_InteractionService().windowed_slice(self)

    # 将指定截面按当前窗宽窗位转换为显示灰度。
    def _windowed_plane(self, plane: NDArray[np.float32]) -> NDArray[np.uint8]:
        from ..Interaction.C_Qt_InteractionService import C_Qt_InteractionService

        return C_Qt_InteractionService().windowed_plane(self, plane)

    # 重绘当前层轮廓或掩码，并同步导航、复核及插值状态。
    def refresh_slice(self) -> None:
        from ...Algorithms.Observation.C_OverlayPalette import C_OverlayPalette

        if self.getVolume() is None or self.getProject() is None:
            return
        if self.getExternalPreviewActive():
            self.getCanvas().set_slice(
                self._windowed_slice(),
                [],
                None
                if self.getExternalMask() is None
                else self.requireExternalMask()[:, :, self.getCurrentSlice()].T,
                overlay_color=C_OverlayPalette().getExternalMaskColor(),
            )
            self.getInterpolationStatus().setText(
                self._text(
                    "external_mask_current",
                    index=self.getCurrentSlice(),
                    path=str(self.getExternalMaskPath() or "…"),
                )
            )
            self._show_annotation_path()
            self._refresh_observation_views()
            return
        if self.getInternalMaskCoverageDirty():
            if self.getBusyProgressDialog() is not None:
                from ...Application.Tasks.C_MaskPresenceTask import C_MaskPresenceTask
                from ..Tasks.C_Qt_BackgroundTaskRunner import C_Qt_BackgroundTaskRunner

                presence = C_Qt_BackgroundTaskRunner[NDArray[np.bool_]]().run(
                    C_MaskPresenceTask(self.requireProject())
                )
            else:
                presence = self.requireProject().mask_presence()
            self.getMaskCoverageBar().set_presence(presence)
            self.setInternalMaskCoverageDirty(False)
        annotation = self.requireProject().annotation(self.getCurrentSlice())
        if self.getReadOnly():
            assert self.getInternalObservationMask() is not None
            interpolated = (
                self.requireInternalObservationMask()[:, :, self.getCurrentSlice()].T
                if self.requireProject().interpolation_bounds(self.getCurrentSlice())
                is not None
                else None
            )
        else:
            interpolated = (
                self.requireProject().interpolated_plane(self.getCurrentSlice())
                if self.getShowInterpolation().isChecked()
                else None
            )
        self.getCanvas().set_slice(
            self._windowed_slice(),
            [] if annotation.getForceEmpty() else annotation.iterPolygons(),
            interpolated_mask=interpolated,
        )
        self.getCompletedCheck().blockSignals(True)
        self.getCompletedCheck().setChecked(annotation.getCompleted())
        self.getCompletedCheck().blockSignals(False)
        self.getForceEmptyCheck().blockSignals(True)
        self.getForceEmptyCheck().setChecked(annotation.getForceEmpty())
        self.getForceEmptyCheck().blockSignals(False)
        self.getReviewProgress().setValue(self.requireProject().getCompletedCount())
        if annotation.getForceEmpty():
            state = self._text("state_force_empty")
        elif annotation.getPolygonCount():
            sources = {polygon.getSource() for polygon in annotation.iterPolygons()}
            if sources == {"prototype"}:
                prefix = self._text("state_machine")
            elif sources == {"manual"}:
                prefix = self._text("state_manual")
            else:
                prefix = self._text("state_union")
            review = self._text(
                "state_reviewed" if annotation.getCompleted() else "state_unreviewed"
            )
            state = f"{prefix} ({review})"
        elif annotation.getCompleted():
            state = self._text("state_empty_boundary")
        elif annotation.getKeyframe():
            state = self._text("state_empty_keyframe")
        elif interpolated is not None:
            bounds = self.requireProject().interpolation_bounds(self.getCurrentSlice())
            state = self._text(
                "state_interpolated",
                lower=bounds[0] if bounds else 0,
                upper=bounds[1] if bounds else 0,
            )
        else:
            state = self._text("state_unannotated")
        self.getInterpolationStatus().setText(self._text("current_slice", state=state))
        if self.getReadOnly():
            self._refresh_observation_views()

    # 将 LP 层号限制到有效范围，清除草稿并刷新三个联动截面。
    def set_slice(self, index: int) -> None:
        if self.getVolume() is None:
            return
        index = int(np.clip(index, 0, self.requireVolume().getData().shape[2] - 1))
        self.getCanvas().cancel_polygon()
        self.setCurrentSlice(index)
        self.setObservationPosition((*self.getObservationPosition()[:2], index))
        self.getSliceSlider().blockSignals(True)
        self.getSliceSpin().blockSignals(True)
        self.getSliceSlider().setValue(index)
        self.getSliceSpin().setValue(index)
        self.getSliceSlider().blockSignals(False)
        self.getSliceSpin().blockSignals(False)
        self.refresh_slice()

    # 按相对步长切换 LP 层，并通过统一刷新逻辑更新视图。
    def move_slice(self, offset: int) -> None:
        self.set_slice(self.getCurrentSlice() + offset)

    # 跳到严格早于或晚于当前层的最近轮廓层；找不到时模态提示且不回绕。
    def go_to_labeled_slice(self, direction: int) -> None:
        if (
            self.getProject() is None
            or self.getVolume() is None
            or self.getInternalClosingPolygon()
            or self.getInternalSwitchingAnnotation()
            or (self.getLoadThread() is not None)
            or self.getExternalPreviewActive()
        ):
            return
        candidates = (
            index
            for index, annotation in (
                (_entry_index, self.requireProject().getSlice(_entry_index))
                for _entry_index in self.requireProject().iterSliceIndices()
            )
            if annotation.getPolygonCount()
            and (index - self.getCurrentSlice()) * direction > 0
        )
        target = (max if direction < 0 else min)(candidates, default=None)
        if target is None:
            QMessageBox.information(
                self,
                self._text("labeled_slice_title"),
                self._text(
                    "previous_labeled_not_found"
                    if direction < 0
                    else "next_labeled_not_found"
                ),
            )
            return
        self.set_slice(target)

    # 将耗时流程的界面锁定和进度配置转交交互服务。
    def _polygon_busy_ui(
        self,
        status_key: str = "closing_polygon_status",
        *,
        progress_settings: I_ProgressDialogSettings | None = None,
    ) -> AbstractContextManager[None]:
        from ..Interaction.C_Qt_InteractionService import C_Qt_InteractionService

        return C_Qt_InteractionService().polygon_busy_ui(
            self, status_key, progress_settings=progress_settings
        )

    # 向指定层加入轮廓，清除强制空层标志并分配新的编辑序号。
    def add_polygon(self, points: I_PointList, operation: str) -> None:
        from ...Application.Tasks.C_AddPolygonTask import C_AddPolygonTask
        from ...Domain.Annotations.C_PolygonAnnotation import C_PolygonAnnotation
        from ..Tasks.C_Qt_BackgroundTaskRunner import C_Qt_BackgroundTaskRunner

        if (
            self.getProject() is None
            or self.getInternalClosingPolygon()
            or self.getReadOnly()
        ):
            return
        with self._polygon_busy_ui():
            C_Qt_BackgroundTaskRunner[None]().run(
                C_AddPolygonTask(
                    self.requireProject(),
                    self.getCurrentSlice(),
                    C_PolygonAnnotation(points=points, operation=operation),
                )
            )
            self.commit_change()
            self.refresh_slice()

    # 接收顶点拖动结果，更新对应轮廓并立即保存项目。
    def update_polygon(self, polygon_index: int, points: I_PointList) -> None:
        if self.getProject() is None or self.getReadOnly():
            return
        self.requireProject().replace_polygon(
            self.getCurrentSlice(), polygon_index, points
        )
        self.commit_change()
        self.refresh_slice()

    # 按编辑序号删除本层最近修改的轮廓，而非简单删除列表末项。
    def delete_last_edited_polygon(self) -> None:
        if self.getProject() is None or self.getReadOnly():
            return
        self.getCanvas().cancel_polygon()
        if self.requireProject().annotation(self.getCurrentSlice()).getForceEmpty():
            self.statusBar().showMessage(self._text("force_empty_delete"))
            return
        deleted = self.requireProject().delete_last_edited_polygon(
            self.getCurrentSlice()
        )
        if deleted is None:
            self.statusBar().showMessage(self._text("no_polygon_delete"))
            return
        self.commit_change()
        self.refresh_slice()
        self.statusBar().showMessage(self._text("polygon_deleted"))

    # 清除本层轮廓及显式状态，使其重新参与关键层插值并保存。
    def clear_current_slice(self) -> None:
        if self.getProject() is None or self.getReadOnly():
            return
        annotation = self.requireProject().annotation(self.getCurrentSlice())
        if not (
            annotation.getPolygonCount()
            or annotation.getCompleted()
            or annotation.getKeyframe()
            or annotation.getForceEmpty()
        ):
            return
        answer = QMessageBox.question(
            self, self._text("clear_title"), self._text("clear_message")
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.requireProject().clear_slice(self.getCurrentSlice())
        self.commit_change()
        self.refresh_slice()

    # 将上一层标注复制到当前层，并立即保存新轮廓。
    def copy_previous_slice(self) -> None:
        if (
            self.getProject() is None
            or self.getCurrentSlice() == 0
            or self.getReadOnly()
        ):
            return
        target = self.requireProject().annotation(self.getCurrentSlice())
        if target.getPolygonCount():
            answer = QMessageBox.question(
                self, self._text("overwrite_title"), self._text("overwrite_message")
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        self.requireProject().copy_slice(
            self.getCurrentSlice() - 1, self.getCurrentSlice()
        )
        self.commit_change()
        self.refresh_slice()

    # 在可编辑状态下更新本层复核标志，并立即保存刷新。
    def set_slice_completed(self, completed: bool) -> None:
        if self.getProject() is None or self.getReadOnly():
            return
        self.requireProject().set_completed(self.getCurrentSlice(), completed)
        self.commit_change()
        self.refresh_slice()

    # 更新当前层强制空掩码状态，使它优先于轮廓和自动插值。
    def set_force_empty(self, force_empty: bool) -> None:
        if self.getProject() is None or self.getReadOnly():
            return
        self.requireProject().set_force_empty(self.getCurrentSlice(), force_empty)
        self.commit_change()
        self.refresh_slice()

    # 切换当前层复核状态，并将空复核层作为插值边界保存。
    def toggle_completed(self) -> None:
        if self.getProject() is not None and (not self.getReadOnly()):
            self.getCompletedCheck().setChecked(
                not self.getCompletedCheck().isChecked()
            )

    # 查找下一未复核层并跳转，保持当前标注状态不变。
    def go_to_next_incomplete(self) -> None:
        if self.getProject() is None or self.getExternalPreviewActive():
            return
        depth = self.requireProject().getShapeLps()[2]
        for offset in range(1, depth + 1):
            index = (self.getCurrentSlice() + offset) % depth
            if not self.requireProject().annotation(index).getCompleted():
                self.set_slice(index)
                return

    # 标记项目已修改，立即保存并刷新切片及复核状态。
    def commit_change(self) -> None:
        if self.getExternalPreviewActive():
            return
        self.setInternalDirty(True)
        self.setInternalMaskCoverageDirty(True)
        self.setInternalObservationMask(None)
        self.save_project()

    # 仅在项目有修改且允许写盘时保存，外置掩码预览期间不写 JSON。
    def autosave_if_needed(self) -> None:
        if (
            self.getInternalDirty()
            and (not self.getInternalClosingPolygon())
            and (not self.getExternalPreviewActive())
        ):
            self.save_project()

    # 按当前编号策略保存 JSON；仅非零编号的空轮廓项目会删除文件。
    def save_project(self, *, notify: bool = False, force: bool = False) -> bool:
        if self.getExternalPreviewActive():
            return True
        empty_numbered = (
            self.getAnnotationIndex() > 0
            and self.getProject() is not None
            and (not self.requireProject().getHasPolygons())
        )
        if (
            self.getProject() is None
            or self.getProjectPath() is None
            or (not self.getInternalDirty() and (not force) and (not empty_numbered))
        ):
            return True
        try:
            if self.getBusyProgressDialog() is not None:
                from ...Application.Tasks.C_SaveProjectTask import C_SaveProjectTask
                from ..Tasks.C_Qt_BackgroundTaskRunner import C_Qt_BackgroundTaskRunner

                C_Qt_BackgroundTaskRunner[I_FilePath]().run(
                    C_SaveProjectTask(
                        self.requireProject(),
                        self.requireProjectPath(),
                        delete_if_empty=self.getAnnotationIndex() > 0,
                    )
                )
            elif self.getAnnotationIndex() > 0:
                self.requireProject().save(
                    self.requireProjectPath(), delete_if_empty=True
                )
            else:
                self.requireProject().save(self.requireProjectPath())
        except Exception as exc:
            self.getAutosaveStatus().setText(
                self._text("autosave_failed", error=str(exc))
            )
            if notify:
                QMessageBox.critical(
                    self, self._text("autosave_failed_title"), str(exc)
                )
            return False
        self.setInternalDirty(False)
        if empty_numbered:
            self._show_annotation_path()
            return True
        saved_at = QTime.currentTime().toString("HH:mm:ss")
        self.getAutosaveStatus().setText(
            self._text(
                "autosave_success", time=saved_at, path=str(self.getProjectPath())
            )
        )
        return True

    # 选择 NIfTI 文件名和位置后执行掩码写入。
    def export_mask(self) -> None:
        from ..Persistence.C_Qt_ExportService import C_Qt_ExportService

        if (
            self.getCurrentSource() is None
            or self.getExternalPreviewActive()
            or self.getInternalClosingPolygon()
        ):
            return
        service = C_Qt_ExportService()
        output = service.select_output(
            self,
            self.requireCurrentSource().getMaskPath(),
            self._text("export_mask_dialog_title"),
            self._text("export_mask_filter"),
            ".nii.gz",
        )
        if output is not None:
            self._export_mask(output)

    # 选择 UBD 文件名和位置后导出包含插值的掩码。
    def export_ubd_mask(self) -> None:
        from ..Persistence.C_Qt_ExportService import C_Qt_ExportService

        if (
            self.getCurrentSource() is None
            or self.getExternalPreviewActive()
            or self.getInternalClosingPolygon()
        ):
            return
        service = C_Qt_ExportService()
        output = service.select_output(
            self,
            self.requireCurrentSource().getUbdMaskPath(),
            self._text("export_ubd_dialog_title"),
            self._text("export_ubd_filter"),
            ".ubd.npz",
        )
        if output is not None:
            self._export_mask(output)

    # 选择 JSON 文件名和位置后导出当前编号标注。
    def export_annotations(self) -> None:
        from ..Persistence.C_Qt_ExportService import C_Qt_ExportService

        if (
            self.getProject() is None
            or self.getProjectPath() is None
            or self.getExternalPreviewActive()
            or self.getInternalClosingPolygon()
        ):
            return
        service = C_Qt_ExportService()
        output = service.select_output(
            self,
            self.requireProjectPath(),
            self._text("export_annotations_dialog_title"),
            self._text("export_annotations_filter"),
            ".med-image-seg.json",
        )
        if output is not None:
            service.export_annotations(self, output)

    # 检查导出条件并执行掩码写入，只在成功后显示完成提示。
    def _export_mask(self, output: I_FilePath) -> None:
        from ..Persistence.C_Qt_ExportService import C_Qt_ExportService

        return C_Qt_ExportService().export_mask(self, output)

    # 加载或闭合期间拒绝退出；保存成功后隐藏附属视图并继续关闭窗口。
    def closeEvent(self, event: QCloseEvent) -> None:
        if self.getExternalMaskThread() is not None:
            event.ignore()
            return
        if self.getInternalClosingPolygon():
            event.ignore()
            return
        if self.getLoadThread() is not None:
            QMessageBox.information(
                self,
                self._text("loading_close_title"),
                self._text("loading_close_message"),
            )
            event.ignore()
            return
        if not self.save_project(notify=True):
            event.ignore()
            return
        for view in self.iterObservationWindows():
            view.getHost().hide()
        super().closeEvent(event)

    # 随主窗口显示附属截面，并继续交由 Qt 处理窗口显示事件。
    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if self.getReadOnly() and self.getVolume() is not None:
            for view in self.iterObservationWindows():
                view.getHost().show()

    # 让附属截面窗口随主窗口隐藏，避免观察视图脱离父窗口状态。
    def hideEvent(self, event: QHideEvent) -> None:
        for view in self.iterObservationWindows():
            view.getHost().hide()
        super().hideEvent(event)

    # 返回底层界面宿主。
    def getHost(self) -> QMainWindow:
        return self

    # 返回需随编辑模式启停的控件数量。
    def getEditingControlCount(self) -> int:
        return len(self._state_editing_controls)

    # 按索引取得编辑控件，不暴露控件列表。
    def getEditingControl(self, index: int) -> QWidget:
        return self._state_editing_controls[index]

    # 返回参与编辑面板状态管理的控件数量。
    def getEditorWidgetCount(self) -> int:
        return len(self._state_editor_widgets)

    # 按索引取得参与编辑面板状态管理的控件。
    def getEditorWidget(self, index: int) -> QWidget:
        return self._state_editor_widgets[index]

    # 返回随只读状态禁用的编辑快捷键数量。
    def getEditingShortcutCount(self) -> int:
        return len(self._state_editing_shortcuts)

    # 按索引取得编辑快捷键。
    def getEditingShortcut(self, index: int) -> QShortcut:
        return self._state_editing_shortcuts[index]

    # 返回当前已登记的附属截面窗口数量。
    def getObservationWindowCount(self) -> int:
        return len(self._state_observation_windows)

    # 按截面名称查询附属窗口，尚未创建时返回空值。
    def findObservationWindow(
        self, index: str
    ) -> (
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
        ]
        | None
    ):
        return self._state_observation_windows.get(index)

    # 遍历已创建的附属截面名称，不暴露内部窗口映射。
    def iterObservationWindowNames(self) -> Iterator[str]:
        yield from self._state_observation_windows

    # 登记指定截面的附属窗口，避免暴露整个窗口字典。
    def setObservationWindow(
        self,
        name: str,
        window: T_MutableOrthogonalSliceWindow[
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
    ) -> None:
        self._state_observation_windows[name] = window

    # 移除附属截面窗口的登记，不向调用方暴露窗口映射。
    def clearObservationWindows(self) -> None:
        self._state_observation_windows = {}

    # 返回外置加载前已记录状态的控件数量。
    def getExternalLoadingWidgetCount(self) -> int:
        return len(self._state_external_loading_widget_states)

    # 按索引取得外置加载前记录的控件。
    def getExternalLoadingWidget(self, index: int) -> QWidget:
        return self._state_external_loading_widget_states[index][0]

    # 按索引查询控件在外置加载前是否启用。
    def getExternalLoadingWidgetEnabled(self, index: int) -> bool:
        return self._state_external_loading_widget_states[index][1]

    # 记录一个控件及其启用状态，避免加载结束后误启用只读控件。
    def rememberExternalLoadingWidget(self, widget: QWidget, enabled: bool) -> None:
        self._state_external_loading_widget_states.append((widget, enabled))

    # 清除外置加载前记录的控件启用状态。
    def clearExternalLoadingWidgetStates(self) -> None:
        self._state_external_loading_widget_states = []

    # 返回外置加载前已记录状态的快捷键数量。
    def getExternalLoadingShortcutCount(self) -> int:
        return len(self._state_external_loading_shortcut_states)

    # 按索引取得加载前记录的快捷键。
    def getExternalLoadingShortcut(self, index: int) -> QShortcut:
        return self._state_external_loading_shortcut_states[index][0]

    # 按索引查询快捷键在外置加载前是否启用。
    def getExternalLoadingShortcutEnabled(self, index: int) -> bool:
        return self._state_external_loading_shortcut_states[index][1]

    # 记录一个快捷键及其启用状态，供外置加载结束时恢复。
    def rememberExternalLoadingShortcut(self, widget: QShortcut, enabled: bool) -> None:
        self._state_external_loading_shortcut_states.append((widget, enabled))

    # 清除外置加载前记录的快捷键启用状态。
    def clearExternalLoadingShortcutStates(self) -> None:
        self._state_external_loading_shortcut_states = []

    # 取得主窗口中心控件；尚未就绪时抛出明确错误。
    def requireCentralWidget(self) -> QWidget:
        widget = self.centralWidget()
        if widget is None:
            raise RuntimeError("界面尚未就绪 / UI is not available")
        return widget
