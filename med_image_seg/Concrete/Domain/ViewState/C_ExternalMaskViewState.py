from __future__ import annotations

from dataclasses import dataclass
from typing import final

from ....Abstract.Domain.Records.I_RecordFieldList import I_RecordFieldList
from ....Abstract.Domain.ViewState.I_ExternalMaskViewState import (
    I_ExternalMaskViewState,
)


# 记录外置掩码加载前的编辑状态，供卸载和加载失败时恢复。
@final
@dataclass(slots=True, frozen=True, init=False)
class C_ExternalMaskViewState(I_ExternalMaskViewState):
    _state_mode: str
    _state_annotation_index: int
    _state_position: tuple[int, int, int]
    _state_coverage: tuple[bool, ...]
    _state_autosave_active: bool

    # 保存进入外置预览前的编号、切片、模式和插值显示设置。
    def __init__(
        self,
        mode: str,
        annotation_index: int,
        position: tuple[int, int, int],
        coverage: tuple[bool, ...],
        autosave_active: bool,
    ) -> None:
        object.__setattr__(self, "_state_mode", mode)
        object.__setattr__(self, "_state_annotation_index", annotation_index)
        object.__setattr__(self, "_state_position", position)
        object.__setattr__(self, "_state_coverage", coverage)
        object.__setattr__(self, "_state_autosave_active", autosave_active)

    # 返回进入外置预览前的多边形模式。
    def getMode(self) -> str:
        return self._state_mode

    # 返回当前标注文件编号。
    def getAnnotationIndex(self) -> int:
        return self._state_annotation_index

    # 返回三个视图共享的体素交点。
    def getPosition(self) -> tuple[int, int, int]:
        return self._state_position

    # 返回进入外置预览前的掩码区间快照，供卸载后恢复。
    def getCoverage(self) -> tuple[bool, ...]:
        return self._state_coverage

    # 返回自动保存是否启用。
    def getAutosaveActive(self) -> bool:
        return self._state_autosave_active

    # 返回有序的记录字段名，供序列化读取。
    def getRecordFields(self) -> I_RecordFieldList:
        from ..Records.C_RecordFieldList import C_RecordFieldList

        return C_RecordFieldList(
            ("mode", "annotation_index", "position", "coverage", "autosave_active")
        )
