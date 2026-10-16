from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, final

from .T_HostedObject import T_HostedObject

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
from typing import Generic, TypeVar

import numpy as np
from numpy.typing import NDArray

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


# 协调影像、当前项目与三视图状态，将布局、加载和导出委托给服务对象。
class T_AnnotationMainWindow(
    T_HostedObject[T_Host],
    Generic[
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
    ],
):
    # 返回当前中英界面语言代码。
    @abstractmethod
    def getLanguage(self) -> str: ...

    # 通过集合接口访问影像，支持按数量、索引和指纹查询。
    @abstractmethod
    def getSources(self) -> I_MutableImageCollection: ...

    # 返回当前已载入的影像源。
    @abstractmethod
    def getCurrentSource(self) -> I_ImageSource | None: ...

    # 返回当前已加载的医学影像体积。
    @abstractmethod
    def getVolume(self) -> I_MedicalVolume | None: ...

    # 返回当前编号的标注项目。
    @abstractmethod
    def getProject(self) -> I_MutableAnnotationProject | None: ...

    # 返回当前编号对应的 JSON 标注路径。
    @abstractmethod
    def getProjectPath(self) -> I_FilePath | None: ...

    # 返回当前标注文件编号。
    @abstractmethod
    def getAnnotationIndex(self) -> int: ...

    # 返回标注编号切换是否正在进行。
    @abstractmethod
    def getInternalSwitchingAnnotation(self) -> bool: ...

    # 返回当前 LP 切片编号。
    @abstractmethod
    def getCurrentSlice(self) -> int: ...

    # 返回影像后台加载线程。
    @abstractmethod
    def getLoadThread(self) -> T_VolumeThread | None: ...

    # 返回后台正在加载的影像源。
    @abstractmethod
    def getInternalLoadingSource(self) -> I_ImageSource | None: ...

    # 返回影像加载进度框。
    @abstractmethod
    def getLoadingDialog(self) -> T_Dialog | None: ...

    # 返回最近一次影像加载错误。
    @abstractmethod
    def getInternalLoadError(self) -> str | None: ...

    # 返回项目是否存在尚未落盘的修改。
    @abstractmethod
    def getInternalDirty(self) -> bool: ...

    # 返回多边形闭合流程是否正在执行。
    @abstractmethod
    def getInternalClosingPolygon(self) -> bool: ...

    # 返回掩码区间缓存是否需要重算。
    @abstractmethod
    def getInternalMaskCoverageDirty(self) -> bool: ...

    # 返回是否处于禁止编辑的观察状态。
    @abstractmethod
    def getReadOnly(self) -> bool: ...

    # 返回 LP、PS、SL 三个视图共享的体素交点。
    @abstractmethod
    def getObservationPosition(self) -> tuple[int, int, int]: ...

    # 返回观察模式复用的三维掩码缓存。
    @abstractmethod
    def getInternalObservationMask(self) -> NDArray[np.uint8] | None: ...

    # 返回进入观察模式前的插值显示设置。
    @abstractmethod
    def getInternalEditingInterpolationVisible(self) -> bool: ...

    # 返回与参考影像对齐的外置掩码。
    @abstractmethod
    def getExternalMask(self) -> NDArray[np.uint8] | None: ...

    # 返回当前外置掩码文件路径。
    @abstractmethod
    def getExternalMaskPath(self) -> I_FilePath | None: ...

    # 返回外置掩码后台加载线程。
    @abstractmethod
    def getExternalMaskThread(self) -> T_MaskThread | None: ...

    # 返回外置掩码加载进度框。
    @abstractmethod
    def getExternalLoadingDialog(self) -> T_Dialog | None: ...

    # 返回进入外置掩码预览前保存的编辑状态。
    @abstractmethod
    def getInternalExternalViewState(self) -> I_ExternalMaskViewState | None: ...

    # 返回最近一次外置掩码加载错误。
    @abstractmethod
    def getInternalExternalMaskError(self) -> str | None: ...

    # 返回自动保存定时器。
    @abstractmethod
    def getAutosaveTimer(self) -> T_Timer: ...

    # 返回掩码与标注导出工具栏。
    @abstractmethod
    def getAnnotationToolbar(self) -> T_Toolbar: ...

    # 返回NIfTI 掩码导出动作。
    @abstractmethod
    def getExportAction(self) -> T_Action: ...

    # 返回UBD 掩码导出动作。
    @abstractmethod
    def getExportUbdAction(self) -> T_Action: ...

    # 返回JSON 标注导出动作。
    @abstractmethod
    def getExportJsonAction(self) -> T_Action: ...

    # 返回影像集合标题。
    @abstractmethod
    def getImageCollectionLabel(self) -> T_Label: ...

    # 返回影像文件导入按钮。
    @abstractmethod
    def getFileButton(self) -> T_Button: ...

    # 返回DICOM 目录导入按钮。
    @abstractmethod
    def getDicomButton(self) -> T_Button: ...

    # 返回界面语言标签。
    @abstractmethod
    def getLanguageLabel(self) -> T_Label: ...

    # 返回界面语言选择框。
    @abstractmethod
    def getLanguageCombo(self) -> T_Combo: ...

    # 返回影像列表、画布及编辑面板的分隔器。
    @abstractmethod
    def getSplitter(self) -> T_Splitter: ...

    # 返回已导入影像列表标题。
    @abstractmethod
    def getImportedImagesLabel(self) -> T_Label: ...

    # 返回已导入影像列表控件。
    @abstractmethod
    def getSourceList(self) -> T_SourceList: ...

    # 返回标注网格间距标签。
    @abstractmethod
    def getSpacingLabel(self) -> T_Label: ...

    # 返回标注网格间距输入框。
    @abstractmethod
    def getSpacingSpin(self) -> T_DoubleSpin: ...

    # 返回载入选中影像按钮。
    @abstractmethod
    def getLoadButton(self) -> T_Button: ...

    # 返回切片画布。
    @abstractmethod
    def getCanvas(self) -> T_Canvas: ...

    # 返回上一层按钮。
    @abstractmethod
    def getPreviousButton(self) -> T_Button: ...

    # 返回下一层按钮。
    @abstractmethod
    def getNextButton(self) -> T_Button: ...

    # 返回上一个有轮廓层按钮。
    @abstractmethod
    def getPreviousLabeledButton(self) -> T_Button: ...

    # 返回下一个有轮廓层按钮。
    @abstractmethod
    def getNextLabeledButton(self) -> T_Button: ...

    # 返回当前切片位置滑块。
    @abstractmethod
    def getSliceSlider(self) -> T_Slider: ...

    # 返回逐层掩码存在性区间条。
    @abstractmethod
    def getMaskCoverageBar(self) -> T_Coverage: ...

    # 返回当前切片编号输入框。
    @abstractmethod
    def getSliceSpin(self) -> T_Spin: ...

    # 返回标注编号标签。
    @abstractmethod
    def getAnnotationIndexLabel(self) -> T_Label: ...

    # 返回标注编号输入框。
    @abstractmethod
    def getAnnotationIndexSpin(self) -> T_AnnotationSpin: ...

    # 返回多边形模式选择框。
    @abstractmethod
    def getModeGroup(self) -> T_Group: ...

    # 返回添加区域单选按钮。
    @abstractmethod
    def getAddRadio(self) -> T_Radio: ...

    # 返回擦除区域单选按钮。
    @abstractmethod
    def getEraseRadio(self) -> T_Radio: ...

    # 返回只读观察模式单选按钮。
    @abstractmethod
    def getObserveRadio(self) -> T_Radio: ...

    # 返回观察模式状态标签。
    @abstractmethod
    def getObservationStatus(self) -> T_Label: ...

    # 返回闭合当前轮廓按钮。
    @abstractmethod
    def getFinishButton(self) -> T_Button: ...

    # 返回取消当前轮廓按钮。
    @abstractmethod
    def getCancelButton(self) -> T_Button: ...

    # 返回删除最近编辑轮廓按钮。
    @abstractmethod
    def getDeleteButton(self) -> T_Button: ...

    # 返回复制上一层标注按钮。
    @abstractmethod
    def getCopyButton(self) -> T_Button: ...

    # 返回清空当前层按钮。
    @abstractmethod
    def getClearButton(self) -> T_Button: ...

    # 返回当前层复核复选框。
    @abstractmethod
    def getCompletedCheck(self) -> T_Check: ...

    # 返回当前层强制空掩码复选框。
    @abstractmethod
    def getForceEmptyCheck(self) -> T_Check: ...

    # 返回下一未完成层按钮。
    @abstractmethod
    def getNextIncompleteButton(self) -> T_Button: ...

    # 返回切片复核进度标签。
    @abstractmethod
    def getReviewProgress(self) -> T_Progress: ...

    # 返回显示自动插值复选框。
    @abstractmethod
    def getShowInterpolation(self) -> T_Check: ...

    # 返回当前层插值状态标签。
    @abstractmethod
    def getInterpolationStatus(self) -> T_Label: ...

    # 返回自动保存状态标签。
    @abstractmethod
    def getAutosaveStatus(self) -> T_Label: ...

    # 返回窗宽窗位设置框。
    @abstractmethod
    def getWindowGroup(self) -> T_Group: ...

    # 返回窗位标签。
    @abstractmethod
    def getLevelLabel(self) -> T_Label: ...

    # 返回窗位输入框。
    @abstractmethod
    def getLevelSpin(self) -> T_DoubleSpin: ...

    # 返回窗宽标签。
    @abstractmethod
    def getWidthLabel(self) -> T_Label: ...

    # 返回窗宽输入框。
    @abstractmethod
    def getWidthSpin(self) -> T_DoubleSpin: ...

    # 返回载入外置掩码按钮。
    @abstractmethod
    def getLoadExternalMaskButton(self) -> T_Button: ...

    # 返回卸载外置掩码按钮。
    @abstractmethod
    def getUnloadExternalMaskButton(self) -> T_Button: ...

    # 返回编辑操作提示标签。
    @abstractmethod
    def getHintLabel(self) -> T_Label: ...

    # 返回外置掩码预览是否启用。
    @abstractmethod
    def getExternalPreviewActive(self) -> bool: ...

    # 取得当前已载入的影像源；尚未就绪时抛出明确错误。
    @final
    def requireCurrentSource(self) -> I_ImageSource:
        value = self.getCurrentSource()
        if value is None:
            raise RuntimeError("数据尚未就绪 / Data is not available")
        return value

    # 取得主窗口中心控件；尚未就绪时抛出明确错误。
    @abstractmethod
    def requireCentralWidget(self) -> T_Widget: ...

    # 返回需随编辑模式启停的控件数量。
    @abstractmethod
    def getEditingControlCount(self) -> int: ...

    # 按索引取得编辑控件，不暴露控件列表。
    @abstractmethod
    def getEditingControl(self, index: int) -> T_Widget: ...

    # 依次访问编辑控件，不返回保存它们的内部列表。
    @final
    def iterEditingControls(self) -> Iterator[T_Widget]:
        for index in range(self.getEditingControlCount()):
            yield self.getEditingControl(index)

    # 返回参与编辑面板状态管理的控件数量。
    @abstractmethod
    def getEditorWidgetCount(self) -> int: ...

    # 按索引取得参与编辑面板状态管理的控件。
    @abstractmethod
    def getEditorWidget(self, index: int) -> T_Widget: ...

    # 依次访问编辑面板控件，供加载时保存和恢复启用状态。
    @final
    def iterEditorWidgets(self) -> Iterator[T_Widget]:
        for index in range(self.getEditorWidgetCount()):
            yield self.getEditorWidget(index)

    # 返回随只读状态禁用的编辑快捷键数量。
    @abstractmethod
    def getEditingShortcutCount(self) -> int: ...

    # 按索引取得编辑快捷键。
    @abstractmethod
    def getEditingShortcut(self, index: int) -> T_Shortcut: ...

    # 依次访问编辑快捷键，供只读或忙碌状态批量禁用。
    @final
    def iterEditingShortcuts(self) -> Iterator[T_Shortcut]:
        for index in range(self.getEditingShortcutCount()):
            yield self.getEditingShortcut(index)

    # 返回当前已登记的附属截面窗口数量。
    @abstractmethod
    def getObservationWindowCount(self) -> int: ...

    # 按截面名称查询附属窗口，尚未创建时返回空值。
    @abstractmethod
    def findObservationWindow(self, index: str) -> T_Ortho | None: ...

    # 遍历已创建的附属截面名称，不暴露内部窗口映射。
    @abstractmethod
    def iterObservationWindowNames(self) -> Iterator[str]: ...

    # 按截面名称取得已登记窗口，尚未创建时抛出查询错误。
    @final
    def getObservationWindow(self, index: str) -> T_Ortho:
        value = self.findObservationWindow(index)
        if value is None:
            raise KeyError(index)
        return value

    # 逐个访问已创建的附属截面窗口。
    @final
    def iterObservationWindows(self) -> Iterator[T_Ortho]:
        for name in self.iterObservationWindowNames():
            yield self.getObservationWindow(name)

    # 返回外置加载前已记录状态的控件数量。
    @abstractmethod
    def getExternalLoadingWidgetCount(self) -> int: ...

    # 按索引取得外置加载前记录的控件。
    @abstractmethod
    def getExternalLoadingWidget(self, index: int) -> T_Widget: ...

    # 按索引查询控件在外置加载前是否启用。
    @abstractmethod
    def getExternalLoadingWidgetEnabled(self, index: int) -> bool: ...

    # 返回外置加载前已记录状态的快捷键数量。
    @abstractmethod
    def getExternalLoadingShortcutCount(self) -> int: ...

    # 按索引取得加载前记录的快捷键。
    @abstractmethod
    def getExternalLoadingShortcut(self, index: int) -> T_Shortcut: ...

    # 按索引查询快捷键在外置加载前是否启用。
    @abstractmethod
    def getExternalLoadingShortcutEnabled(self, index: int) -> bool: ...

    # 取得当前已加载的医学影像体积；尚未就绪时抛出明确错误。
    @final
    def requireVolume(self) -> I_MedicalVolume:
        value = self.getVolume()
        if value is None:
            raise RuntimeError("数据尚未就绪 / Data is not available")
        return value

    # 取得当前编号的标注项目；尚未就绪时抛出明确错误。
    @final
    def requireProject(self) -> I_MutableAnnotationProject:
        value = self.getProject()
        if value is None:
            raise RuntimeError("数据尚未就绪 / Data is not available")
        return value

    # 取得当前编号对应的 JSON 标注路径；尚未就绪时抛出明确错误。
    @final
    def requireProjectPath(self) -> I_FilePath:
        value = self.getProjectPath()
        if value is None:
            raise RuntimeError("数据尚未就绪 / Data is not available")
        return value

    # 取得影像后台加载线程；尚未就绪时抛出明确错误。
    @final
    def requireLoadThread(self) -> T_VolumeThread:
        value = self.getLoadThread()
        if value is None:
            raise RuntimeError("数据尚未就绪 / Data is not available")
        return value

    # 取得后台正在加载的影像源；尚未就绪时抛出明确错误。
    @final
    def requireInternalLoadingSource(self) -> I_ImageSource:
        value = self.getInternalLoadingSource()
        if value is None:
            raise RuntimeError("数据尚未就绪 / Data is not available")
        return value

    # 取得影像加载进度框；尚未就绪时抛出明确错误。
    @final
    def requireLoadingDialog(self) -> T_Dialog:
        value = self.getLoadingDialog()
        if value is None:
            raise RuntimeError("数据尚未就绪 / Data is not available")
        return value

    # 取得最近一次影像加载错误；尚未就绪时抛出明确错误。
    @final
    def requireInternalLoadError(self) -> str:
        value = self.getInternalLoadError()
        if value is None:
            raise RuntimeError("数据尚未就绪 / Data is not available")
        return value

    # 取得观察模式复用的三维掩码缓存；尚未就绪时抛出明确错误。
    @final
    def requireInternalObservationMask(self) -> NDArray[np.uint8]:
        value = self.getInternalObservationMask()
        if value is None:
            raise RuntimeError("数据尚未就绪 / Data is not available")
        return value

    # 取得与参考影像对齐的外置掩码；尚未就绪时抛出明确错误。
    @final
    def requireExternalMask(self) -> NDArray[np.uint8]:
        value = self.getExternalMask()
        if value is None:
            raise RuntimeError("数据尚未就绪 / Data is not available")
        return value

    # 取得当前外置掩码文件路径；尚未就绪时抛出明确错误。
    @final
    def requireExternalMaskPath(self) -> I_FilePath:
        value = self.getExternalMaskPath()
        if value is None:
            raise RuntimeError("数据尚未就绪 / Data is not available")
        return value

    # 取得外置掩码后台加载线程；尚未就绪时抛出明确错误。
    @final
    def requireExternalMaskThread(self) -> T_MaskThread:
        value = self.getExternalMaskThread()
        if value is None:
            raise RuntimeError("数据尚未就绪 / Data is not available")
        return value

    # 取得外置掩码加载进度框；尚未就绪时抛出明确错误。
    @final
    def requireExternalLoadingDialog(self) -> T_Dialog:
        value = self.getExternalLoadingDialog()
        if value is None:
            raise RuntimeError("数据尚未就绪 / Data is not available")
        return value

    # 取得进入外置掩码预览前保存的编辑状态；尚未就绪时抛出明确错误。
    @final
    def requireInternalExternalViewState(self) -> I_ExternalMaskViewState:
        value = self.getInternalExternalViewState()
        if value is None:
            raise RuntimeError("数据尚未就绪 / Data is not available")
        return value

    # 取得最近一次外置掩码加载错误；尚未就绪时抛出明确错误。
    @final
    def requireInternalExternalMaskError(self) -> str:
        value = self.getInternalExternalMaskError()
        if value is None:
            raise RuntimeError("数据尚未就绪 / Data is not available")
        return value
