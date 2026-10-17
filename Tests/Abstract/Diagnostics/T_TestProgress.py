from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

T_MonkeyPatch = TypeVar("T_MonkeyPatch")


# 验证耗时校准、真实完成和界面计时器，避免估计进度误报成功或污染用户数据。
class T_TestProgress(ABC, Generic[T_MonkeyPatch]):
    # 检查 S 曲线单调有界，超出预计耗时也不能提前返回 100。
    @abstractmethod
    def test_estimator_is_monotonic_and_reserves_completion(self) -> None: ...

    # 没有历史时采用初始耗时，但不为查询创建空数据库。
    @abstractmethod
    def test_missing_history_uses_default_without_creating_file(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 仅使用最近的成功样本估计耗时，并限制每个操作类别的保留数量。
    @abstractmethod
    def test_history_uses_recent_successes_and_bounds_retention(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 损坏的历史或不可写目录不得阻止正常影像操作。
    @abstractmethod
    def test_history_failures_are_nonfatal(
        self, tmp_path: I_FilePath, state: str
    ) -> None: ...

    # 拒绝会让估计器退化的无效初始耗时。
    @abstractmethod
    def test_invalid_default_duration_is_rejected(
        self, tmp_path: I_FilePath, default_seconds: float
    ) -> None: ...

    # 数据库被其他进程占用时退回初始值，避免界面无限等待。
    @abstractmethod
    def test_locked_history_uses_default(self, tmp_path: I_FilePath) -> None: ...

    # 重复结束不得产生重复样本，完成后耗时与结果保持不变。
    @abstractmethod
    def test_session_records_real_duration_only_once(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 异常结束记录失败且继续抛出异常，失败耗时不能参与下一次校准。
    @abstractmethod
    def test_failed_context_records_failure_without_swallowing_error(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 同时运行的两个会话必须独立计时，不能共享完成状态。
    @abstractmethod
    def test_sessions_are_independent(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 工厂使用当前操作的历史耗时，不借用其他操作的样本。
    @abstractmethod
    def test_factory_calibrates_from_matching_history(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 零耗时和无效样本不应导致除零或破坏后续估计。
    @abstractmethod
    def test_zero_and_invalid_samples_remain_safe(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 验证界面定时刷新、超时不假完成、中英文案和结束后的定时器清理。
    @abstractmethod
    def test_dialog_updates_until_actual_completion(
        self,
        tmp_path: I_FilePath,
        monkeypatch: T_MonkeyPatch,
        language: str,
        success: bool,
    ) -> None: ...

    # 运行中的不可取消任务不能通过 Esc 或关闭窗口被隐藏。
    @abstractmethod
    def test_dialog_cannot_be_closed_while_running(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 窗口启动完成后结束进度会话，但不把应用事件循环计入启动耗时。
    @abstractmethod
    def test_startup_records_window_preparation(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 字体服务可重复调用，并在 Windows 启动框出现前准备中文字体。
    @abstractmethod
    def test_startup_font_setup_loads_only_missing_fonts(
        self, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 窗口初始化失败时保留原异常，并记录失败而非成功进度。
    @abstractmethod
    def test_startup_failure_records_failed_duration(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 主窗口按实际加载结果结束进度，校验失败不能显示 100%。
    @abstractmethod
    def test_image_loading_finishes_with_actual_result(
        self, tmp_path: I_FilePath, success: bool
    ) -> None: ...
