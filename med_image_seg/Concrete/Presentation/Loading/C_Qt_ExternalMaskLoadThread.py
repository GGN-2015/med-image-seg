from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Presentation.Loading.T_MutableExternalMaskLoadThread import (
    T_MutableExternalMaskLoadThread,
)
from ..Metaclasses.C_Qt_AbcMeta import C_Qt_AbcMeta

if TYPE_CHECKING:
    from ....Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
from typing import final

from PySide6.QtCore import QThread, Signal, SignalInstance
from PySide6.QtWidgets import QWidget


# 在后台读取外置掩码，通过信号返回结果和错误以免阻塞界面。
@final
class C_Qt_ExternalMaskLoadThread(
    QThread,
    T_MutableExternalMaskLoadThread[QThread, SignalInstance],
    metaclass=C_Qt_AbcMeta,
):
    # 返回影像输入路径。
    def getPath(self) -> I_FilePath:
        return self._state_path

    # 记录影像输入路径。
    def setPath(self, value: I_FilePath) -> None:
        self._state_path = value

    # 返回外置掩码需要对齐的参考影像。
    def getReference(self) -> I_MedicalVolume:
        return self._state_reference

    # 记录外置掩码需要对齐的参考影像。
    def setReference(self, value: I_MedicalVolume) -> None:
        self._state_reference = value

    loaded = Signal(object, object)
    failed = Signal(str)

    # 保存掩码路径与参考影像，供后台线程执行读取和对齐。
    def __init__(
        self, path: I_FilePath, reference: I_MedicalVolume, parent: QWidget
    ) -> None:
        super().__init__(parent)
        self.setPath(path)
        self.setReference(reference)

    # 在线程中读取并对齐外置掩码，通过信号返回结果或错误。
    def run(self) -> None:
        from ...Diagnostics.Progress.C_OperationProgressFactory import (
            C_OperationProgressFactory,
        )
        from ...Storage.Masks.C_MedicalMaskReader import C_MedicalMaskReader

        try:
            with C_OperationProgressFactory().start("external-mask.read", 10.0):
                mask = C_MedicalMaskReader().read(self.getPath(), self.getReference())
                presence = mask.any(axis=(0, 1))
        except Exception as exc:
            self.failed.emit(f"{type(exc).__name__}: {exc}")
            return
        self.loaded.emit(mask, presence)

    # 返回底层界面宿主。
    def getHost(self) -> QThread:
        return self

    # 提供后台读取成功信号，用于把数据交回主线程。
    def getLoaded(self) -> SignalInstance:
        return self.loaded

    # 提供后台读取失败信号，由主线程处理错误提示和状态恢复。
    def getFailed(self) -> SignalInstance:
        return self.failed
