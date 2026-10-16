from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Presentation.Loading.T_MutableVolumeLoadThread import (
    T_MutableVolumeLoadThread,
)
from ..Metaclasses.C_Qt_AbcMeta import C_Qt_AbcMeta

if TYPE_CHECKING:
    from ....Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
from typing import final

from PySide6.QtCore import QThread, Signal, SignalInstance


# 在后台读取与重采样影像，通过信号把结果交回主线程。
@final
class C_Qt_VolumeLoadThread(
    QThread, T_MutableVolumeLoadThread[QThread, SignalInstance], metaclass=C_Qt_AbcMeta
):
    # 返回当前处理的影像来源。
    def getSource(self) -> I_ImageSource:
        return self._state_source

    # 记录后台任务需要读取的影像源。
    def setSource(self, value: I_ImageSource) -> None:
        self._state_source = value

    # 返回 LPS 网格间距，单位为毫米。
    def getSpacingMm(self) -> float:
        return self._state_spacing_mm

    # 记录LPS 网格间距，单位为毫米。
    def setSpacingMm(self, value: float) -> None:
        self._state_spacing_mm = value

    loaded = Signal(object)
    failed = Signal(str)

    # 保存影像来源与标注间距，供后台线程执行加载。
    def __init__(self, source: I_ImageSource, spacing_mm: float) -> None:
        super().__init__()
        self.setSource(source)
        self.setSpacingMm(spacing_mm)

    # 在线程中读取影像，通过成功或失败信号把结果交回主线程。
    def run(self) -> None:
        from ...Storage.Volumes.C_MedicalVolumeReader import C_MedicalVolumeReader

        try:
            volume = C_MedicalVolumeReader(self.getSpacingMm()).read(
                self.getSource().getPath()
            )
        except Exception as exc:
            self.failed.emit(f"{type(exc).__name__}: {exc}")
            return
        self.loaded.emit(volume)

    # 返回底层界面宿主。
    def getHost(self) -> QThread:
        return self

    # 提供后台读取成功信号，用于把数据交回主线程。
    def getLoaded(self) -> SignalInstance:
        return self.loaded

    # 提供后台读取失败信号，由主线程处理错误提示和状态恢复。
    def getFailed(self) -> SignalInstance:
        return self.failed
