from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

T_MonkeyPatch = TypeVar("T_MonkeyPatch")


# 约定闭合进度的回归，确保耗时任务期间界面仍能绘制且异常不会误报完成。
class T_TestPolygonProgress(ABC, Generic[T_MonkeyPatch]):
    # 分别延迟添加、保存和区间计算，检查空格闭合时进度持续刷新及线程隔离。
    @abstractmethod
    def test_space_closure_updates_progress_during_background_work(
        self,
        tmp_path: I_FilePath,
        monkeypatch: T_MonkeyPatch,
        stage: str,
        language: str,
    ) -> None: ...

    # 每个后台阶段失败后都应结束进度、保留原异常语义并恢复编辑状态。
    @abstractmethod
    def test_failed_closure_rejects_progress_and_restores_editor(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch, stage: str
    ) -> None: ...

    # 顶点较多时仅在锁定的绘制过程中处理计时事件，正常编辑不得引入重入。
    @abstractmethod
    def test_large_polygon_refresh_yields_only_while_locked(
        self, enabled: bool
    ) -> None: ...
