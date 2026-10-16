from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

T_Window = TypeVar("T_Window")
T_MonkeyPatch = TypeVar("T_MonkeyPatch")


# 验证编号切换、独立项目和空编号文件的删除策略。
class T_TestNumberedAnnotations(ABC, Generic[T_Window, T_MonkeyPatch]):
    # 验证编号默认是 0，且标签随界面语言更新。
    @abstractmethod
    def test_number_selector_defaults_to_zero_and_translates(
        self, window: T_Window
    ) -> None: ...

    # 反复切换编号，验证项目独立且影像不会重复加载。
    @abstractmethod
    def test_switching_numbers_keeps_projects_independent_without_reloading_image(
        self, window: T_Window, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 验证回车只提交一次编号，且上下箭头可逐步调整。
    @abstractmethod
    def test_number_input_commits_once_on_enter_and_supports_arrow_steps(
        self, window: T_Window, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 验证标注编号支持任意精度的非负整数并拒绝负值。
    @abstractmethod
    def test_number_input_supports_arbitrary_precision_and_rejects_negative_values(
        self, window: T_Window
    ) -> None: ...

    # 重复选择当前编号，验证不重复读取或保存项目。
    @abstractmethod
    def test_reselecting_active_number_does_not_reload_or_save(
        self, window: T_Window, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 编辑非零编号项目，验证轮廓和插值状态实时写盘。
    @abstractmethod
    def test_numbered_annotation_edits_save_immediately(
        self, window: T_Window, monkeypatch: T_MonkeyPatch, action: str
    ) -> None: ...

    # 删除最后一个轮廓，验证非零编号主文件和备份均清理且不会恢复。
    @abstractmethod
    def test_removing_last_polygon_removes_all_files_and_prevents_backup_resurrection(
        self, window: T_Window, monkeypatch: T_MonkeyPatch, action: str
    ) -> None: ...

    # 清空一层但保留另一层轮廓，验证非零编号文件不被删除。
    @abstractmethod
    def test_removing_one_slice_keeps_file_if_another_slice_has_polygons(
        self, window: T_Window
    ) -> None: ...

    # 验证仅含复核或强制空层状态的项目只在 0 号保留文件。
    @abstractmethod
    def test_review_or_force_empty_without_polygons_only_persists_for_number_zero(
        self, window: T_Window, number: int
    ) -> None: ...

    # 验证强制空层仍有已存轮廓时不会删除非零编号文件。
    @abstractmethod
    def test_forced_empty_with_saved_polygons_keeps_numbered_file(
        self, window: T_Window
    ) -> None: ...

    # 切换编号前闭合草稿，验证它保存到原编号而非新编号。
    @abstractmethod
    def test_switching_closes_and_saves_draft_to_the_outgoing_number(
        self, window: T_Window
    ) -> None: ...

    # 模拟原项目保存失败，核验切换被阻止且编号输入恢复。
    @abstractmethod
    def test_old_save_failure_blocks_switch_and_restores_number_input(
        self, window: T_Window, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 切到不可读或几何不匹配的标注，验证原活动项目不被替换。
    @abstractmethod
    def test_unreadable_or_mismatched_target_does_not_replace_active_project(
        self, window: T_Window, monkeypatch: T_MonkeyPatch, failure: str
    ) -> None: ...

    # 损坏非零编号主文件，验证只恢复该编号自己的备份。
    @abstractmethod
    def test_numbered_project_can_recover_its_own_backup(
        self, window: T_Window
    ) -> None: ...

    # 验证文件删除失败时保留未保存状态并阻止编号切换。
    @abstractmethod
    def test_deletion_failure_keeps_dirty_project_and_blocks_switch(
        self, window: T_Window, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 验证观察模式锁定标注编号，返回编辑模式后才重新启用。
    @abstractmethod
    def test_observation_locks_number_until_return_to_editing(
        self, window: T_Window
    ) -> None: ...

    # 切换影像，验证当前选择的标注编号保持不变。
    @abstractmethod
    def test_selected_number_is_retained_when_loading_another_image(
        self, window: T_Window, tmp_path: I_FilePath
    ) -> None: ...

    # 验证 JSON 导出使用当前编号，并遵守非零空文件删除策略。
    @abstractmethod
    def test_json_export_uses_active_number_and_respects_empty_file_policy(
        self, window: T_Window, monkeypatch: T_MonkeyPatch, empty: bool
    ) -> None: ...

    # 验证尚未载入影像时也可预先选择标注编号。
    @abstractmethod
    def test_index_can_be_set_before_loading_first_image(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 验证空编号输入回退到当前编号，不意外切换项目。
    @abstractmethod
    def test_blank_number_input_restores_active_value(
        self, window: T_Window
    ) -> None: ...

    # 验证编号输入只读时上下箭头也不可用。
    @abstractmethod
    def test_spin_box_read_only_state_disables_arrows(self) -> None: ...

    # 验证载入影像使用所选编号，默认仍为 0 号。
    @abstractmethod
    def test_loading_image_opens_selected_existing_number_and_defaults_to_zero(
        self, window: T_Window
    ) -> None: ...

    # 验证非零编号只有空备份时会清理它，不恢复空文件。
    @abstractmethod
    def test_empty_numbered_backup_is_removed_when_opened_without_primary(
        self, window: T_Window
    ) -> None: ...

    # 验证观察模式不仅禁用输入框，也拒绝程序直接切换编号。
    @abstractmethod
    def test_programmatic_number_change_is_blocked_in_observation(
        self, window: T_Window, monkeypatch: T_MonkeyPatch
    ) -> None: ...
