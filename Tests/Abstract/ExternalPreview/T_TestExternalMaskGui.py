from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

T_MonkeyPatch = TypeVar("T_MonkeyPatch")
T_Window = TypeVar("T_Window")


# 验证外置掩码的加载、只读显示、界面锁定和卸载恢复。
class T_TestExternalMaskGui(ABC, Generic[T_MonkeyPatch, T_Window]):
    # 验证启动后仅载入外置掩码按钮可用，包括尚未载入影像时。
    @abstractmethod
    def test_buttons_start_with_only_load_enabled_even_without_image(
        self, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 验证外置掩码替代三个视图中的轮廓及插值，并更新区间条。
    @abstractmethod
    def test_external_mask_replaces_all_polygon_views_and_coverage(
        self, window: T_Window, tmp_path: I_FilePath, suffix: str
    ) -> None: ...

    # 监测调用，验证外置预览不保存 JSON 或重新栅格化原多边形。
    @abstractmethod
    def test_external_preview_never_calls_json_save_or_full_polygon_rasterization(
        self, window: T_Window, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 卸载外置掩码，核验原编号、切片、模式、区间及快捷键恢复。
    @abstractmethod
    def test_unload_restores_original_number_slice_mode_coverage_and_shortcuts(
        self,
        window: T_Window,
        tmp_path: I_FilePath,
        monkeypatch: T_MonkeyPatch,
        mode: str,
        autosave_active: bool,
    ) -> None: ...

    # 验证外置掩码选择框打开前，软件已经进入只读观察模式。
    @abstractmethod
    def test_file_chooser_opens_after_switching_to_read_only(
        self,
        window: T_Window,
        tmp_path: I_FilePath,
        monkeypatch: T_MonkeyPatch,
        cancel: bool,
    ) -> None: ...

    # 模拟外置掩码加载失败，核验原模式及控件状态恢复。
    @abstractmethod
    def test_failed_external_load_restores_original_editing_state(
        self, window: T_Window, tmp_path: I_FilePath, failure: str
    ) -> None: ...

    # 延迟后台读取，验证事件循环保持响应且三个视图均不可操作。
    @abstractmethod
    def test_external_loading_is_nonblocking_and_locks_all_views_until_completion(
        self, window: T_Window, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 验证空外置掩码显示全灰区间，不回退到原 JSON 轮廓。
    @abstractmethod
    def test_empty_external_mask_displays_all_gray_coverage_without_json_fallback(
        self, window: T_Window, tmp_path: I_FilePath
    ) -> None: ...

    # 开始外置预览前闭合未保存草稿，卸载后恢复其原编辑环境。
    @abstractmethod
    def test_unsaved_draft_is_closed_before_external_preview_then_restored(
        self, window: T_Window, tmp_path: I_FilePath
    ) -> None: ...
