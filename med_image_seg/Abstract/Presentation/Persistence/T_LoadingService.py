from __future__ import annotations

from typing import TYPE_CHECKING

from ...Domain.Annotations.I_MutableAnnotationProject import I_MutableAnnotationProject

if TYPE_CHECKING:
    from ...Domain.Imaging.I_ImageSource import I_ImageSource
    from ...Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from ...Storage.Paths.I_FilePath import I_FilePath
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T_Context = TypeVar("T_Context")


# 约定影像加载与卸载流程，集中保存项目、释放视图及恢复控件状态。
class T_LoadingService(ABC, Generic[T_Context]):
    # 禁用三个视图和编辑入口，并显示不可取消的加载进度提示。
    @abstractmethod
    def show_loading(self, context: T_Context, source: I_ImageSource) -> None: ...

    # 关闭加载提示并恢复先前控件状态，结束影像加载阶段。
    @abstractmethod
    def finish_loading_ui(self, context: T_Context) -> None: ...

    # 保存并释放当前影像及三视图，再移除导入项，不自动载入剩余影像。
    @abstractmethod
    def unload_imported_image(self, context: T_Context) -> bool: ...

    # 打开当前编号的 JSON 或备份；文件不存在时创建对应的新项目。
    @abstractmethod
    def open_annotation_project(
        self, source: I_ImageSource, volume: I_MedicalVolume, index: int
    ) -> tuple[I_MutableAnnotationProject, I_FilePath]: ...

    # 显示当前编号及落盘路径，外置预览时明确标注保存已暂停。
    @abstractmethod
    def show_annotation_path(self, context: T_Context) -> None: ...
