from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

T_MonkeyPatch = TypeVar("T_MonkeyPatch")


# 约定真实计算负载的界面回归，避免 sleep 释放 GIL 后掩盖实际线程饥饿。
class T_TestProgressResponsiveness(ABC, Generic[T_MonkeyPatch]):
    # 大轮廓闭合和导出期间，主线程心跳与实际进度文本必须持续更新。
    @abstractmethod
    def test_real_polygon_work_keeps_gui_alive(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch, operation: str
    ) -> None: ...
