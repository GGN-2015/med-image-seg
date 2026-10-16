from __future__ import annotations

from abc import abstractmethod

from ..Annotations.I_Record import I_Record
from ..Records.I_RecordFieldList import I_RecordFieldList


# 记录外置掩码加载前的编辑状态，供卸载和加载失败时恢复。
class I_ExternalMaskViewState(I_Record):
    # 返回进入外置预览前的多边形模式。
    @abstractmethod
    def getMode(self) -> str: ...

    # 返回当前标注文件编号。
    @abstractmethod
    def getAnnotationIndex(self) -> int: ...

    # 返回三个视图共享的体素交点。
    @abstractmethod
    def getPosition(self) -> tuple[int, int, int]: ...

    # 返回进入外置预览前的掩码区间快照，供卸载后恢复。
    @abstractmethod
    def getCoverage(self) -> tuple[bool, ...]: ...

    # 返回自动保存是否启用。
    @abstractmethod
    def getAutosaveActive(self) -> bool: ...

    # 返回有序的记录字段名，供序列化读取。
    @abstractmethod
    def getRecordFields(self) -> I_RecordFieldList: ...
