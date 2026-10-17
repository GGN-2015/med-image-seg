from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

T_MonkeyPatch = TypeVar("T_MonkeyPatch")


# 约定掩码另存为的进度回归，防止只显示静止窗口或在失败时误报完成。
class T_TestExportProgress(ABC, Generic[T_MonkeyPatch]):
    # 分别延迟自动保存、体积生成和写盘，验证两种格式的进度刷新与线程隔离。
    @abstractmethod
    def test_progress_updates_through_save_compute_and_write(
        self,
        tmp_path: I_FilePath,
        monkeypatch: T_MonkeyPatch,
        suffix: str,
        language: str,
        stage: str,
    ) -> None: ...

    # 保存、计算或写盘失败，以及保存返回失败时，均应拒绝进度并恢复原界面。
    @abstractmethod
    def test_failures_never_report_success_and_restore_ui(
        self,
        tmp_path: I_FilePath,
        monkeypatch: T_MonkeyPatch,
        suffix: str,
        stage: str,
    ) -> None: ...

    # 用户取消文件选择时，不得启动进度、生成掩码或落盘。
    @abstractmethod
    def test_cancel_does_not_start_work(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch, suffix: str
    ) -> None: ...

    # 观察模式允许导出，但结束后仍须保持只读、三视图和原有禁用状态。
    @abstractmethod
    def test_observation_export_preserves_readonly_state(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch, suffix: str
    ) -> None: ...
