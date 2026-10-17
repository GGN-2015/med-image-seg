from abc import ABC, abstractmethod

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath


# 约定影像卸载回归，防止误删文件、丢失标注或自动打开其他影像。
class I_TestImageUnloading(ABC):
    # 仅导入列表或尚未打开影像时，卸载入口必须不可用。
    @abstractmethod
    def test_unload_is_disabled_without_an_open_image(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 点击按钮应关闭当前影像而非选中项，保存草稿且重置空界面。
    @abstractmethod
    def test_unload_removes_current_image_not_selected_row(
        self, tmp_path: I_FilePath, language: str, annotation_index: int
    ) -> None: ...

    # 保存失败必须保留当前影像、列表、切片和可继续编辑的项目。
    @abstractmethod
    def test_save_failure_keeps_image_and_list(self, tmp_path: I_FilePath) -> None: ...

    # 观察或外置预览卸载后，三个截面和掩码缓存都不能残留。
    @abstractmethod
    def test_unload_clears_observation_and_external_preview(
        self, tmp_path: I_FilePath, external: bool
    ) -> None: ...

    # 加载、闭合或切换项目期间拒绝卸载，以免后台结果写回已关闭的影像。
    @abstractmethod
    def test_busy_operations_reject_unloading(
        self, tmp_path: I_FilePath, busy: str
    ) -> None: ...

    # 卸载后可手动加载剩余项或重新导入原影像，且列表索引保持正确。
    @abstractmethod
    def test_manual_loading_works_after_unload(
        self, tmp_path: I_FilePath, target: str
    ) -> None: ...
