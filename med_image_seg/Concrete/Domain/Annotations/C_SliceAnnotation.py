from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from ....Abstract.Domain.Annotations.I_MutableSliceAnnotation import (
    I_MutableSliceAnnotation,
)
from ....Abstract.Domain.Annotations.I_PolygonAnnotation import I_PolygonAnnotation
from ....Abstract.Domain.Defaults.E_DefaultValue import E_DefaultValue
from ....Abstract.Domain.Records.I_RecordFieldList import I_RecordFieldList

if TYPE_CHECKING:
    from ....Abstract.Domain.Annotations.I_PolygonAnnotation import I_PolygonAnnotation
from dataclasses import dataclass
from typing import final


# 管理单层轮廓与复核标志，按索引访问多边形而不暴露内部列表。
@final
@dataclass(slots=True, frozen=False, init=False)
class C_SliceAnnotation(I_MutableSliceAnnotation):
    _state_polygons: list[I_PolygonAnnotation]
    _state_completed: bool
    _state_keyframe: bool
    _state_force_empty: bool

    # 复制轮廓列表并保存复核、关键层与强制空层标志。
    def __init__(
        self,
        polygons: list[I_PolygonAnnotation] | E_DefaultValue = E_DefaultValue.Unset,
        completed: bool = False,
        keyframe: bool = False,
        force_empty: bool = False,
    ) -> None:
        object.__setattr__(
            self,
            "_state_polygons",
            list() if polygons is E_DefaultValue.Unset else list(polygons),
        )
        object.__setattr__(self, "_state_completed", completed)
        object.__setattr__(self, "_state_keyframe", keyframe)
        object.__setattr__(self, "_state_force_empty", force_empty)

    # 用输入轮廓替换本层内容，复制集合以隔离调用方的后续修改。
    def setPolygons(self, value: Iterable[I_PolygonAnnotation]) -> None:
        self._state_polygons = list(value)

    # 返回当前层是否已复核。
    def getCompleted(self) -> bool:
        return self._state_completed

    # 记录当前层是否已完成复核。
    def setCompleted(self, value: bool) -> None:
        self._state_completed = value

    # 返回当前层是否被显式设为插值关键层。
    def getKeyframe(self) -> bool:
        return self._state_keyframe

    # 记录当前层是否作为显式插值关键层。
    def setKeyframe(self, value: bool) -> None:
        self._state_keyframe = value

    # 返回本层是否强制无掩码；该状态优先于轮廓与插值。
    def getForceEmpty(self) -> bool:
        return self._state_force_empty

    # 记录当前层是否强制无掩码。
    def setForceEmpty(self, value: bool) -> None:
        self._state_force_empty = value

    # 返回有序的记录字段名，供序列化读取。
    def getRecordFields(self) -> I_RecordFieldList:
        from ..Records.C_RecordFieldList import C_RecordFieldList

        return C_RecordFieldList(("polygons", "completed", "keyframe", "force_empty"))

    # 返回本层已存轮廓数量，包括被强制空层屏蔽的轮廓。
    def getPolygonCount(self) -> int:
        return len(self._state_polygons)

    # 按索引查询本层轮廓，不允许调用方直接修改集合结构。
    def getPolygon(self, index: int) -> I_PolygonAnnotation:
        return self._state_polygons[index]

    # 在当前层末尾追加轮廓，不暴露内部多边形列表。
    def addPolygon(self, polygon: I_PolygonAnnotation) -> None:
        self._state_polygons.append(polygon)

    # 按索引替换已有轮廓，不允许调用方直接修改存储列表。
    def replacePolygon(self, index: int, polygon: I_PolygonAnnotation) -> None:
        self._state_polygons[index] = polygon

    # 按索引移除轮廓并返回被移除项，集合本身仍由切片对象管理。
    def removePolygon(self, index: int) -> I_PolygonAnnotation:
        return self._state_polygons.pop(index)
