from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

T_Window = TypeVar("T_Window")
T_MonkeyPatch = TypeVar("T_MonkeyPatch")


# 验证只读三视图、十字线联动、掩码截面和编辑状态恢复。
class T_TestObservation(ABC, Generic[T_Window, T_MonkeyPatch]):
    # 核验三个截面的轴顺序及提取出的体素数值。
    @abstractmethod
    def test_plane_sections_have_correct_axes_and_voxel_values(
        self, name: str
    ) -> None: ...

    # 核验截面点击采用像素位置并限制在有效体素范围内。
    @abstractmethod
    def test_plane_clicks_use_pixel_centers_and_clamp_to_volume(
        self, name: str
    ) -> None: ...

    # 验证进入观察模式前先闭合并保存已有草稿。
    @abstractmethod
    def test_entering_observation_closes_and_saves_draft_before_read_only(
        self, window: T_Window, operation: str
    ) -> None: ...

    # 进入只读模式时丢弃不足三个点的草稿，不生成无效轮廓。
    @abstractmethod
    def test_too_short_draft_is_discarded_without_creating_invalid_polygon(
        self, window: T_Window, count: int
    ) -> None: ...

    # 点击任一截面，验证共享交点和其余层号控件同步更新。
    @abstractmethod
    def test_click_in_any_view_updates_shared_intersection_and_slice_controls(
        self,
        window: T_Window,
        name: str,
        clicked: tuple[float, float],
        expected: tuple[int, int, int],
    ) -> None: ...

    # 连续切层，核验三视图交点、层号及参考线始终同步。
    @abstractmethod
    def test_sequential_navigation_keeps_all_three_views_synchronized(
        self, window: T_Window
    ) -> None: ...

    # 验证十字星与其他视图中的同色参考线代表同一截面。
    @abstractmethod
    def test_crosshair_and_reference_line_colors_identify_the_same_planes(
        self, window: T_Window, name: str
    ) -> None: ...

    # 比较附属截面与完整导出掩码，覆盖擦除及空层结果。
    @abstractmethod
    def test_companion_masks_match_export_with_erasures_and_empty_slices(
        self, window: T_Window, index: int
    ) -> None: ...

    # 监测掩码生成次数，验证观察切层和调窗复用缓存。
    @abstractmethod
    def test_observation_reuses_mask_for_navigation_and_contrast(
        self, window: T_Window, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 验证只读模式同时阻止按钮、快捷键、直接编辑调用和顶点拖动。
    @abstractmethod
    def test_read_only_blocks_edit_buttons_shortcuts_direct_methods_and_handle_drags(
        self, window: T_Window
    ) -> None: ...

    # 验证附属视图非模态、不可独立关闭，并跟随模式和主窗口显示。
    @abstractmethod
    def test_companion_windows_are_nonmodal_unclosable_and_follow_mode_and_parent(
        self, window: T_Window
    ) -> None: ...

    # 验证观察模式临时显示插值，退出后恢复原显示偏好。
    @abstractmethod
    def test_observation_restores_interpolation_preference(
        self, window: T_Window
    ) -> None: ...

    # 退出观察并修改轮廓后，验证再次进入时重建掩码而不使用旧缓存。
    @abstractmethod
    def test_reentering_observation_rebuilds_mask_after_editing(
        self, window: T_Window
    ) -> None: ...

    # 观察模式载入不同尺寸影像，核验交点和截面索引仍有效。
    @abstractmethod
    def test_observation_handles_loading_new_volume_with_different_dimensions(
        self, window: T_Window, tmp_path: I_FilePath
    ) -> None: ...

    # 验证加载期间附属视图被禁用，完成后恢复正确的只读状态。
    @abstractmethod
    def test_loading_disables_companion_views_and_restores_read_only_state(
        self, window: T_Window
    ) -> None: ...

    # 模拟重载期间掩码准备失败，核验原影像未被替换。
    @abstractmethod
    def test_failed_mask_preparation_during_reload_preserves_previous_volume(
        self, window: T_Window, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 模拟观察掩码生成失败，核验界面不会残留禁用状态。
    @abstractmethod
    def test_failed_mask_preparation_restores_editing_and_does_not_leave_disabled_ui(
        self, window: T_Window, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 使用单体素影像，验证交点限制和截面提取无越界。
    @abstractmethod
    def test_single_voxel_volume_has_valid_intersection_and_sections(
        self, window: T_Window, tmp_path: I_FilePath
    ) -> None: ...
