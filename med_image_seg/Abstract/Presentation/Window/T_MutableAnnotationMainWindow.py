from __future__ import annotations

from collections.abc import Iterable
from contextlib import AbstractContextManager
from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

from ...Domain.Annotations.I_MutableAnnotationProject import I_MutableAnnotationProject
from ...Domain.Collections.I_ImageCollection import I_ImageCollection
from ...Domain.Collections.I_MutableImageCollection import I_MutableImageCollection
from ...Domain.Geometry.I_PointList import I_PointList
from ...Domain.Imaging.I_ImageSource import I_ImageSource
from ...Domain.Imaging.I_MedicalVolume import I_MedicalVolume
from ...Domain.ViewState.I_ExternalMaskViewState import I_ExternalMaskViewState
from ...Storage.Paths.I_FilePath import I_FilePath
from ..Progress.I_ProgressDialogSettings import I_ProgressDialogSettings
from .T_AnnotationMainWindow import T_AnnotationMainWindow

if TYPE_CHECKING:
    from ...Domain.Annotations.I_MutableAnnotationProject import (
        I_MutableAnnotationProject,
    )
    from ...Domain.Collections.I_MutableImageCollection import I_MutableImageCollection
    from ...Domain.Imaging.I_ImageSource import I_ImageSource
    from ...Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from ...Domain.ViewState.I_ExternalMaskViewState import I_ExternalMaskViewState
    from ...Storage.Paths.I_FilePath import I_FilePath
from abc import abstractmethod
from typing import TypeVar

T_Action = TypeVar("T_Action")
T_AnnotationSpin = TypeVar("T_AnnotationSpin")
T_Button = TypeVar("T_Button")
T_ButtonGroup = TypeVar("T_ButtonGroup")
T_Canvas = TypeVar("T_Canvas")
T_Check = TypeVar("T_Check")
T_Combo = TypeVar("T_Combo")
T_Coverage = TypeVar("T_Coverage")
T_Dialog = TypeVar("T_Dialog")
T_DoubleSpin = TypeVar("T_DoubleSpin")
T_Group = TypeVar("T_Group")
T_Host = TypeVar("T_Host", covariant=True)
T_Label = TypeVar("T_Label")
T_MaskThread = TypeVar("T_MaskThread")
T_Ortho = TypeVar("T_Ortho")
T_Point = TypeVar("T_Point")
T_Progress = TypeVar("T_Progress")
T_Radio = TypeVar("T_Radio")
T_Shortcut = TypeVar("T_Shortcut")
T_Slider = TypeVar("T_Slider")
T_SourceList = TypeVar("T_SourceList")
T_Spin = TypeVar("T_Spin")
T_Splitter = TypeVar("T_Splitter")
T_Timer = TypeVar("T_Timer")
T_Toolbar = TypeVar("T_Toolbar")
T_VolumeThread = TypeVar("T_VolumeThread")
T_Widget = TypeVar("T_Widget")


# 在主窗口状态查询上增加受控更新及交互入口，供界面服务协调状态。
class T_MutableAnnotationMainWindow(
    T_AnnotationMainWindow[
        T_Host,
        T_Timer,
        T_Toolbar,
        T_Action,
        T_Label,
        T_Button,
        T_Combo,
        T_Splitter,
        T_SourceList,
        T_DoubleSpin,
        T_Slider,
        T_Spin,
        T_Group,
        T_Radio,
        T_Check,
        T_Progress,
        T_Dialog,
        T_Shortcut,
        T_Widget,
        T_ButtonGroup,
        T_Canvas,
        T_Ortho,
        T_AnnotationSpin,
        T_Coverage,
        T_VolumeThread,
        T_MaskThread,
        T_Point,
    ]
):
    # 记录当前中英界面语言代码。
    @abstractmethod
    def setLanguage(self, value: str) -> None: ...

    # 设置应用使用的影像集合接口，不暴露集合内部的存储结构。
    @abstractmethod
    def setSources(self, value: I_MutableImageCollection) -> None: ...

    # 记录当前已载入的影像源。
    @abstractmethod
    def setCurrentSource(self, value: I_ImageSource | None) -> None: ...

    # 记录当前已加载的医学影像体积。
    @abstractmethod
    def setVolume(self, value: I_MedicalVolume | None) -> None: ...

    # 记录当前编号的标注项目。
    @abstractmethod
    def setProject(self, value: I_MutableAnnotationProject | None) -> None: ...

    # 记录当前编号对应的 JSON 标注路径。
    @abstractmethod
    def setProjectPath(self, value: I_FilePath | None) -> None: ...

    # 记录当前标注文件编号。
    @abstractmethod
    def setAnnotationIndex(self, value: int) -> None: ...

    # 记录标注编号切换是否正在进行。
    @abstractmethod
    def setInternalSwitchingAnnotation(self, value: bool) -> None: ...

    # 记录当前 LP 切片编号。
    @abstractmethod
    def setCurrentSlice(self, value: int) -> None: ...

    # 记录影像后台加载线程。
    @abstractmethod
    def setLoadThread(self, value: T_VolumeThread | None) -> None: ...

    # 记录后台正在加载的影像源。
    @abstractmethod
    def setInternalLoadingSource(self, value: I_ImageSource | None) -> None: ...

    # 记录影像加载进度框。
    @abstractmethod
    def setLoadingDialog(self, value: T_Dialog | None) -> None: ...

    # 登记锁定操作的进度窗口，结束时清空以避免后续保存误入后台。
    @abstractmethod
    def setBusyProgressDialog(self, value: T_Dialog | None) -> None: ...

    # 记录最近一次影像加载错误。
    @abstractmethod
    def setInternalLoadError(self, value: str | None) -> None: ...

    # 记录项目是否存在尚未落盘的修改。
    @abstractmethod
    def setInternalDirty(self, value: bool) -> None: ...

    # 记录多边形闭合流程是否正在执行。
    @abstractmethod
    def setInternalClosingPolygon(self, value: bool) -> None: ...

    # 记录掩码区间缓存是否需要重算。
    @abstractmethod
    def setInternalMaskCoverageDirty(self, value: bool) -> None: ...

    # 记录是否处于禁止编辑的观察状态。
    @abstractmethod
    def setReadOnly(self, value: bool) -> None: ...

    # 记录三个截面共用的 LPS 体素交点。
    @abstractmethod
    def setObservationPosition(self, value: tuple[int, int, int]) -> None: ...

    # 记录观察模式复用的三维掩码缓存。
    @abstractmethod
    def setInternalObservationMask(self, value: NDArray[np.uint8] | None) -> None: ...

    # 记录进入观察模式前的插值显示设置。
    @abstractmethod
    def setInternalEditingInterpolationVisible(self, value: bool) -> None: ...

    # 记录与参考影像对齐的外置掩码。
    @abstractmethod
    def setExternalMask(self, value: NDArray[np.uint8] | None) -> None: ...

    # 记录当前外置掩码文件路径。
    @abstractmethod
    def setExternalMaskPath(self, value: I_FilePath | None) -> None: ...

    # 记录外置掩码后台加载线程。
    @abstractmethod
    def setExternalMaskThread(self, value: T_MaskThread | None) -> None: ...

    # 记录外置掩码加载进度框。
    @abstractmethod
    def setExternalLoadingDialog(self, value: T_Dialog | None) -> None: ...

    # 记录进入外置掩码预览前保存的编辑状态。
    @abstractmethod
    def setInternalExternalViewState(
        self, value: I_ExternalMaskViewState | None
    ) -> None: ...

    # 记录最近一次外置掩码加载错误。
    @abstractmethod
    def setInternalExternalMaskError(self, value: str | None) -> None: ...

    # 记录自动保存定时器。
    @abstractmethod
    def setAutosaveTimer(self, value: T_Timer) -> None: ...

    # 记录掩码与标注导出工具栏。
    @abstractmethod
    def setAnnotationToolbar(self, value: T_Toolbar) -> None: ...

    # 记录NIfTI 掩码导出动作。
    @abstractmethod
    def setExportAction(self, value: T_Action) -> None: ...

    # 记录UBD 掩码导出动作。
    @abstractmethod
    def setExportUbdAction(self, value: T_Action) -> None: ...

    # 记录JSON 标注导出动作。
    @abstractmethod
    def setExportJsonAction(self, value: T_Action) -> None: ...

    # 记录影像集合标题。
    @abstractmethod
    def setImageCollectionLabel(self, value: T_Label) -> None: ...

    # 记录影像文件导入按钮。
    @abstractmethod
    def setFileButton(self, value: T_Button) -> None: ...

    # 记录DICOM 目录导入按钮。
    @abstractmethod
    def setDicomButton(self, value: T_Button) -> None: ...

    # 记录界面语言标签。
    @abstractmethod
    def setLanguageLabel(self, value: T_Label) -> None: ...

    # 记录界面语言选择框。
    @abstractmethod
    def setLanguageCombo(self, value: T_Combo) -> None: ...

    # 记录影像列表、画布及编辑面板的分隔器。
    @abstractmethod
    def setSplitter(self, value: T_Splitter) -> None: ...

    # 记录已导入影像列表标题。
    @abstractmethod
    def setImportedImagesLabel(self, value: T_Label) -> None: ...

    # 记录已导入影像列表控件。
    @abstractmethod
    def setSourceList(self, value: T_SourceList) -> None: ...

    # 记录标注网格间距标签。
    @abstractmethod
    def setSpacingLabel(self, value: T_Label) -> None: ...

    # 记录标注网格间距输入框。
    @abstractmethod
    def setSpacingSpin(self, value: T_DoubleSpin) -> None: ...

    # 记录载入选中影像按钮。
    @abstractmethod
    def setLoadButton(self, value: T_Button) -> None: ...

    # 登记左侧的卸载影像按钮，供加载和模式切换统一管理状态。
    @abstractmethod
    def setUnloadImageButton(self, value: T_Button) -> None: ...

    # 记录切片画布。
    @abstractmethod
    def setCanvas(self, value: T_Canvas) -> None: ...

    # 记录上一层按钮。
    @abstractmethod
    def setPreviousButton(self, value: T_Button) -> None: ...

    # 记录下一层按钮。
    @abstractmethod
    def setNextButton(self, value: T_Button) -> None: ...

    # 记录上一个有轮廓层按钮。
    @abstractmethod
    def setPreviousLabeledButton(self, value: T_Button) -> None: ...

    # 记录下一个有轮廓层按钮。
    @abstractmethod
    def setNextLabeledButton(self, value: T_Button) -> None: ...

    # 记录当前切片位置滑块。
    @abstractmethod
    def setSliceSlider(self, value: T_Slider) -> None: ...

    # 记录逐层掩码存在性区间条。
    @abstractmethod
    def setMaskCoverageBar(self, value: T_Coverage) -> None: ...

    # 记录当前切片编号输入框。
    @abstractmethod
    def setSliceSpin(self, value: T_Spin) -> None: ...

    # 记录标注编号标签。
    @abstractmethod
    def setAnnotationIndexLabel(self, value: T_Label) -> None: ...

    # 记录标注编号输入框。
    @abstractmethod
    def setAnnotationIndexSpin(self, value: T_AnnotationSpin) -> None: ...

    # 记录多边形模式选择框。
    @abstractmethod
    def setModeGroup(self, value: T_Group) -> None: ...

    # 记录添加区域单选按钮。
    @abstractmethod
    def setAddRadio(self, value: T_Radio) -> None: ...

    # 记录擦除区域单选按钮。
    @abstractmethod
    def setEraseRadio(self, value: T_Radio) -> None: ...

    # 记录只读观察模式单选按钮。
    @abstractmethod
    def setObserveRadio(self, value: T_Radio) -> None: ...

    # 记录观察模式状态标签。
    @abstractmethod
    def setObservationStatus(self, value: T_Label) -> None: ...

    # 记录闭合当前轮廓按钮。
    @abstractmethod
    def setFinishButton(self, value: T_Button) -> None: ...

    # 记录取消当前轮廓按钮。
    @abstractmethod
    def setCancelButton(self, value: T_Button) -> None: ...

    # 记录删除最近编辑轮廓按钮。
    @abstractmethod
    def setDeleteButton(self, value: T_Button) -> None: ...

    # 记录复制上一层标注按钮。
    @abstractmethod
    def setCopyButton(self, value: T_Button) -> None: ...

    # 记录清空当前层按钮。
    @abstractmethod
    def setClearButton(self, value: T_Button) -> None: ...

    # 记录当前层复核复选框。
    @abstractmethod
    def setCompletedCheck(self, value: T_Check) -> None: ...

    # 记录当前层强制空掩码复选框。
    @abstractmethod
    def setForceEmptyCheck(self, value: T_Check) -> None: ...

    # 记录下一未完成层按钮。
    @abstractmethod
    def setNextIncompleteButton(self, value: T_Button) -> None: ...

    # 记录切片复核进度标签。
    @abstractmethod
    def setReviewProgress(self, value: T_Progress) -> None: ...

    # 记录显示自动插值复选框。
    @abstractmethod
    def setShowInterpolation(self, value: T_Check) -> None: ...

    # 记录当前层插值状态标签。
    @abstractmethod
    def setInterpolationStatus(self, value: T_Label) -> None: ...

    # 记录自动保存状态标签。
    @abstractmethod
    def setAutosaveStatus(self, value: T_Label) -> None: ...

    # 记录窗宽窗位设置框。
    @abstractmethod
    def setWindowGroup(self, value: T_Group) -> None: ...

    # 记录窗位标签。
    @abstractmethod
    def setLevelLabel(self, value: T_Label) -> None: ...

    # 记录窗位输入框。
    @abstractmethod
    def setLevelSpin(self, value: T_DoubleSpin) -> None: ...

    # 记录窗宽标签。
    @abstractmethod
    def setWidthLabel(self, value: T_Label) -> None: ...

    # 记录窗宽输入框。
    @abstractmethod
    def setWidthSpin(self, value: T_DoubleSpin) -> None: ...

    # 记录载入外置掩码按钮。
    @abstractmethod
    def setLoadExternalMaskButton(self, value: T_Button) -> None: ...

    # 记录卸载外置掩码按钮。
    @abstractmethod
    def setUnloadExternalMaskButton(self, value: T_Button) -> None: ...

    # 记录编辑操作提示标签。
    @abstractmethod
    def setHintLabel(self, value: T_Label) -> None: ...

    # 逐项登记编辑控件，复制输入而不保留外部容器。
    @abstractmethod
    def setEditingControls(self, value: Iterable[T_Widget]) -> None: ...

    # 复制编辑面板控件集合，供加载期间保存及恢复启用状态。
    @abstractmethod
    def setEditorWidgets(self, value: Iterable[T_Widget]) -> None: ...

    # 逐项登记编辑快捷键，供只读和忙碌状态统一管理。
    @abstractmethod
    def setEditingShortcuts(self, value: Iterable[T_Shortcut]) -> None: ...

    # 进入只读观察模式后选择 NIfTI 或 UBD 掩码文件。
    @abstractmethod
    def choose_external_mask(self) -> None: ...

    # 进入外置掩码加载流程；已有预览或忙碌时拒绝重复操作。
    @abstractmethod
    def load_external_mask(self, path: str | I_FilePath) -> bool: ...

    # 接收已对齐的外置掩码，更新三个截面及绿色存在性区间。
    @abstractmethod
    def external_mask_loaded(
        self, mask: NDArray[np.uint8], presence: NDArray[np.bool_]
    ) -> None: ...

    # 记录后台加载错误，供线程结束后显示提示并恢复编辑状态。
    @abstractmethod
    def external_mask_load_failed(self, message: str) -> None: ...

    # 清理后台线程和加载提示，按成功或失败结果恢复可操作状态。
    @abstractmethod
    def external_mask_thread_finished(self) -> None: ...

    # 移除外置掩码，恢复原编号、切片、编辑模式和插值显示设置。
    @abstractmethod
    def unload_external_mask(self) -> bool: ...

    # 规范语言代码并刷新所有中英界面文案。
    @abstractmethod
    def set_language(self, language: str) -> None: ...

    # 批量导入影像，刷新列表并返回应用维护的影像集合接口。
    @abstractmethod
    def add_sources(self, paths: Iterable[str | I_FilePath]) -> I_ImageCollection: ...

    # 选择一个或多个影像文件并加入可载入列表。
    @abstractmethod
    def choose_image_files(self) -> None: ...

    # 选择 DICOM 目录并将其加入影像集合。
    @abstractmethod
    def choose_dicom_directory(self) -> None: ...

    # 在存在初始影像时自动加载首项；空集合保持未载入状态。
    @abstractmethod
    def load_first_source(self) -> None: ...

    # 读取影像列表当前选择的来源并启动后台加载。
    @abstractmethod
    def load_selected_source(self) -> None: ...

    # 保存并关闭当前影像，从导入列表移除它；忙碌或保存失败时保持现状。
    @abstractmethod
    def unload_imported_image(self) -> bool: ...

    # 回收影像加载线程，关闭进度提示并恢复主窗口和附属视图。
    @abstractmethod
    def load_thread_finished(self) -> None: ...

    # 保存后台影像读取错误，供任务结束时提示并恢复原状态。
    @abstractmethod
    def volume_load_failed(self, message: str) -> None: ...

    # 先保存原编号项目再切换标注文件；只读、忙碌或保存失败时拒绝切换。
    @abstractmethod
    def set_annotation_index(self, index: int) -> bool: ...

    # 接收新影像并打开所选编号项目，成功准备掩码后更新视图。
    @abstractmethod
    def volume_loaded(self, volume: I_MedicalVolume) -> None: ...

    # 切换添加、擦除或观察模式；进入只读前先处理尚未闭合的草稿。
    @abstractmethod
    def update_operation(self) -> None: ...

    # 重绘当前层轮廓或掩码，并同步导航、复核及插值状态。
    @abstractmethod
    def refresh_slice(self) -> None: ...

    # 将 LP 层号限制到有效范围，清除草稿并刷新三个联动截面。
    @abstractmethod
    def set_slice(self, index: int) -> None: ...

    # 按相对步长切换 LP 层，并通过统一刷新逻辑更新视图。
    @abstractmethod
    def move_slice(self, offset: int) -> None: ...

    # 跳到严格早于或晚于当前层的最近轮廓层；找不到时模态提示且不回绕。
    @abstractmethod
    def go_to_labeled_slice(self, direction: int) -> None: ...

    # 向指定层加入轮廓，清除强制空层标志并分配新的编辑序号。
    @abstractmethod
    def add_polygon(self, points: I_PointList, operation: str) -> None: ...

    # 接收顶点拖动结果，更新对应轮廓并立即保存项目。
    @abstractmethod
    def update_polygon(self, polygon_index: int, points: I_PointList) -> None: ...

    # 按编辑序号删除本层最近修改的轮廓，而非简单删除列表末项。
    @abstractmethod
    def delete_last_edited_polygon(self) -> None: ...

    # 清除本层轮廓及显式状态，使其重新参与关键层插值并保存。
    @abstractmethod
    def clear_current_slice(self) -> None: ...

    # 将上一层标注复制到当前层，并立即保存新轮廓。
    @abstractmethod
    def copy_previous_slice(self) -> None: ...

    # 在可编辑状态下更新本层复核标志，并立即保存刷新。
    @abstractmethod
    def set_slice_completed(self, completed: bool) -> None: ...

    # 更新当前层强制空掩码状态，使它优先于轮廓和自动插值。
    @abstractmethod
    def set_force_empty(self, force_empty: bool) -> None: ...

    # 切换当前层复核状态，并将空复核层作为插值边界保存。
    @abstractmethod
    def toggle_completed(self) -> None: ...

    # 查找下一未复核层并跳转，保持当前标注状态不变。
    @abstractmethod
    def go_to_next_incomplete(self) -> None: ...

    # 标记项目已修改，立即保存并刷新切片及复核状态。
    @abstractmethod
    def commit_change(self) -> None: ...

    # 仅在项目有修改且允许写盘时保存，外置掩码预览期间不写 JSON。
    @abstractmethod
    def autosave_if_needed(self) -> None: ...

    # 按当前编号策略保存 JSON；仅非零编号的空轮廓项目会删除文件。
    @abstractmethod
    def save_project(self, *, notify: bool = False, force: bool = False) -> bool: ...

    # 选择 NIfTI 文件名和位置后执行掩码写入。
    @abstractmethod
    def export_mask(self) -> None: ...

    # 选择 UBD 文件名和位置后导出包含插值的掩码。
    @abstractmethod
    def export_ubd_mask(self) -> None: ...

    # 选择 JSON 文件名和位置后导出当前编号标注。
    @abstractmethod
    def export_annotations(self) -> None: ...

    # 构建影像列表、主画布和右侧编辑面板，登记供状态切换使用的控件。
    @abstractmethod
    def _build_ui(self, spacing_mm: float) -> None: ...

    # 按消息键翻译文案并填充格式参数。
    @abstractmethod
    def _text(self, key: str, **values: str | int | float) -> str: ...

    # 根据当前模式选择操作提示键，区分编辑与只读观察。
    @abstractmethod
    def _hint_key(self) -> str: ...

    # 保存编辑状态并进入只读模式，为外置掩码选择和加载做准备。
    @abstractmethod
    def _begin_external_preview(self) -> bool: ...

    # 在后台读取选中的外置掩码，并锁定相关操作直到结果返回。
    @abstractmethod
    def _start_external_mask_load(self, path: I_FilePath) -> None: ...

    # 读取语言选择项并更新界面文案，无需重新启动。
    @abstractmethod
    def _language_changed(self, index: int) -> None: ...

    # 根据当前语言更新标题、按钮、状态及操作提示文本。
    @abstractmethod
    def _retranslate_ui(self) -> None: ...

    # 把编辑和切片导航快捷键连接到对应动作，并登记可禁用项。
    @abstractmethod
    def _bind_shortcuts(self) -> None: ...

    # 按影像集合顺序重建列表，并保留来源对象与列表项的关联。
    @abstractmethod
    def _refresh_source_list(self) -> None: ...

    # 禁用三个视图和编辑入口，并显示不可取消的加载进度提示。
    @abstractmethod
    def _show_loading(self, source: I_ImageSource) -> None: ...

    # 关闭加载提示并恢复先前控件状态，结束影像加载阶段。
    @abstractmethod
    def _finish_loading_ui(self) -> None: ...

    # 打开当前编号的 JSON 或备份；文件不存在时创建对应的新项目。
    @abstractmethod
    def _open_annotation_project(
        self, source: I_ImageSource, volume: I_MedicalVolume, index: int
    ) -> tuple[I_MutableAnnotationProject, I_FilePath]: ...

    # 以当前项目编号刷新输入框，避免信号递归触发项目切换。
    @abstractmethod
    def _sync_annotation_index_spin(self) -> None: ...

    # 显示当前编号及落盘路径，外置预览时明确标注保存已暂停。
    @abstractmethod
    def _show_annotation_path(self) -> None: ...

    # 根据编辑、观察或外置预览状态启用相应控件和快捷键。
    @abstractmethod
    def _apply_mode_ui(self) -> None: ...

    # 按需创建 PS、SL 非模态窗口，避免重复打开同一截面。
    @abstractmethod
    def _ensure_observation_windows(self) -> None: ...

    # 把截面点击转换为共享体素交点，并同步其余截面的层号。
    @abstractmethod
    def _observation_clicked(self, name: str, point: T_Point) -> None: ...

    # 将某截面的固定轴设为指定层号，并同步其余视图的交点和参考线。
    @abstractmethod
    def _set_observation_axis(self, name: str, index: int) -> None: ...

    # 按共享交点刷新 LP、PS、SL 切片、掩码和参考线。
    @abstractmethod
    def _refresh_observation_views(self) -> None: ...

    # 将当前 LP 层按窗宽窗位转换为显示灰度。
    @abstractmethod
    def _windowed_slice(self) -> NDArray[np.uint8]: ...

    # 将指定截面按当前窗宽窗位转换为显示灰度。
    @abstractmethod
    def _windowed_plane(self, plane: NDArray[np.float32]) -> NDArray[np.uint8]: ...

    # 把界面锁定和可选进度委托给交互服务，适用于闭合及另存为等耗时操作。
    @abstractmethod
    def _polygon_busy_ui(
        self,
        status_key: str = "closing_polygon_status",
        *,
        progress_settings: I_ProgressDialogSettings | None = None,
    ) -> AbstractContextManager[None]: ...

    # 检查导出条件并执行掩码写入，只在成功后显示完成提示。
    @abstractmethod
    def _export_mask(self, output: I_FilePath) -> None: ...

    # 记录一个控件及其启用状态，避免加载结束后误启用只读控件。
    @abstractmethod
    def rememberExternalLoadingWidget(
        self, widget: T_Widget, enabled: bool
    ) -> None: ...

    # 清除外置加载前记录的控件启用状态。
    @abstractmethod
    def clearExternalLoadingWidgetStates(self) -> None: ...

    # 记录一个快捷键及其启用状态，供外置加载结束时恢复。
    @abstractmethod
    def rememberExternalLoadingShortcut(
        self, widget: T_Shortcut, enabled: bool
    ) -> None: ...

    # 清除外置加载前记录的快捷键启用状态。
    @abstractmethod
    def clearExternalLoadingShortcutStates(self) -> None: ...

    # 登记指定截面的附属窗口，避免暴露整个窗口字典。
    @abstractmethod
    def setObservationWindow(self, name: str, window: T_Ortho) -> None: ...

    # 移除附属截面窗口的登记，不向调用方暴露窗口映射。
    @abstractmethod
    def clearObservationWindows(self) -> None: ...
