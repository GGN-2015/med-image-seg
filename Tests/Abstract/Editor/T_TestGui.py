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

    # 选择自定义路径导出掩码，核验格式、插值内容和中英保存对话框。
    @abstractmethod
    def test_export_toolbar_actions_write_interpolated_masks(
        self,
        tmp_path: I_FilePath,
        monkeypatch: T_MonkeyPatch,
        suffix: str,
        with_suffix: bool,
        language: str,
    ) -> None: ...

    # 模拟 UBD 导出失败，验证没有错误的成功提示。
    @abstractmethod
    def test_ubd_export_handles_failures_without_success_message(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch, failed_step: str
    ) -> None: ...

    # 另存 JSON 到选定目录，保留原自动保存路径及全部标注信息。
    @abstractmethod
    def test_json_export_saves_annotation_project_to_selected_path(
        self,
        tmp_path: I_FilePath,
        monkeypatch: T_MonkeyPatch,
        suffix: str,
        file_state: str,
        with_annotation_suffix: bool,
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

    # 取消另存为时禁止三个导出动作保存项目、创建文件或提示成功。
    @abstractmethod
    def test_cancel_export_dialog_does_not_write_files(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch, suffix: str
    ) -> None: ...

    # 补齐扩展名后目标已存在时，必须再次确认覆盖而不是静默替换。
    @abstractmethod
    def test_export_confirms_overwrite_after_completing_suffix(
        self,
        tmp_path: I_FilePath,
        monkeypatch: T_MonkeyPatch,
        suffix: str,
        overwrite: bool,
    ) -> None: ...

    # 区分自动保存和另存文件失败，核验导出失败不会切换当前项目路径。
    @abstractmethod
    def test_json_export_reports_selected_path_write_failure(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 保留已有 JSON 的任意合法文件名，导出后继续在原文件自动保存编辑。
    @abstractmethod
    def test_json_export_preserves_name_and_original_autosave(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 验证画布按项查询不暴露列表，返回点的修改不会影响内部坐标。
    @abstractmethod
    def test_canvas_collection_queries_protect_internal_state(self) -> None: ...

    # 验证首个草稿点以不可编辑的黄色圆点显示，避免零长度路径不可见。
    @abstractmethod
    def test_first_draft_point_displays_yellow_position_marker(self) -> None: ...

    # 模拟顶点拖动，验证坐标更新并提交多边形变更信号。
    @abstractmethod
    def test_canvas_vertex_handle_can_be_dragged(self) -> None: ...

    # 验证初始 NIfTI 在后台加载，并按默认策略建立标注文件。
    @abstractmethod
    def test_initial_nifti_loads_in_background_and_creates_json(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 启动时载入已有影像，验证程序采用标注保存的网格而不是当前界面间距。
    @abstractmethod
    def test_initial_image_automatically_loads_existing_json(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 切换强制空层复选框，验证修改立即写入标注文件。
    @abstractmethod
    def test_force_empty_checkbox_saves_immediately(
        self, tmp_path: I_FilePath
    ) -> None: ...
