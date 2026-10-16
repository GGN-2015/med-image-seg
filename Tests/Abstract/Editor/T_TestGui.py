from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

T_MonkeyPatch = TypeVar("T_MonkeyPatch")


# 验证编辑、实时保存、导出及加载过程中的界面状态转换。
class T_TestGui(ABC, Generic[T_MonkeyPatch]):
    # 验证无参数启动显示空影像列表，而不要求预先选择文件。
    @abstractmethod
    def test_no_argument_window_starts_without_images(self) -> None: ...

    # 切换中英语言，验证按钮和提示无需重启即可更新。
    @abstractmethod
    def test_interface_language_can_switch_without_restart(self) -> None: ...

    # 延迟影像加载，验证进度框可见且主界面被禁用。
    @abstractmethod
    def test_loading_dialog_is_visible_and_main_ui_is_disabled(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 添加或修改轮廓，验证标注立即保存到影像旁的 JSON。
    @abstractmethod
    def test_polygon_edits_save_immediately_next_to_image(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 延迟保存和刷新，验证闭合流程结束前界面一直不可操作。
    @abstractmethod
    def test_polygon_closure_disables_ui_until_save_and_refresh_finish(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch, trigger: str
    ) -> None: ...

    # 模拟闭合期间失败，核验控件和快捷键恢复原启用状态。
    @abstractmethod
    def test_polygon_closure_restores_previous_ui_state_after_failure(
        self,
        tmp_path: I_FilePath,
        monkeypatch: T_MonkeyPatch,
        failed_step: str,
        initially_enabled: bool,
    ) -> None: ...

    # 验证不足三个顶点的草稿不会触发闭合计算和忙碌锁定。
    @abstractmethod
    def test_incomplete_polygon_does_not_enter_busy_state(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch, point_count: int
    ) -> None: ...

    # 触发工具栏导出动作，核验文件包含自动插值掩码。
    @abstractmethod
    def test_export_toolbar_actions_write_interpolated_masks(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch, suffix: str
    ) -> None: ...

    # 模拟 UBD 导出失败，验证没有错误的成功提示。
    @abstractmethod
    def test_ubd_export_handles_failures_without_success_message(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch, failed_step: str
    ) -> None: ...

    # 验证 JSON 导出写入影像旁的标注路径。
    @abstractmethod
    def test_json_export_saves_annotation_project_beside_source(
        self,
        tmp_path: I_FilePath,
        monkeypatch: T_MonkeyPatch,
        suffix: str,
        file_state: str,
    ) -> None: ...

    # 模拟 JSON 写盘失败，核验只报告错误而不提示导出成功。
    @abstractmethod
    def test_json_export_reports_save_failure_without_success(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch, dirty: bool
    ) -> None: ...

    # 验证没有当前项目时不产生误导性的导出成功提示。
    @abstractmethod
    def test_json_export_without_project_does_not_report_success(
        self, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 验证画布按项查询不暴露列表，返回点的修改不会影响内部坐标。
    @abstractmethod
    def test_canvas_collection_queries_protect_internal_state(self) -> None: ...

    # 模拟顶点拖动，验证坐标更新并提交多边形变更信号。
    @abstractmethod
    def test_canvas_vertex_handle_can_be_dragged(self) -> None: ...

    # 验证初始 NIfTI 在后台加载，并按默认策略建立标注文件。
    @abstractmethod
    def test_initial_nifti_loads_in_background_and_creates_json(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 启动时载入已有影像，验证自动读取旁边的标注 JSON。
    @abstractmethod
    def test_initial_image_automatically_loads_existing_json(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 切换强制空层复选框，验证修改立即写入标注文件。
    @abstractmethod
    def test_force_empty_checkbox_saves_immediately(
        self, tmp_path: I_FilePath
    ) -> None: ...
