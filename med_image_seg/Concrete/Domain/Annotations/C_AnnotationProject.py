from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from ....Abstract.Domain.Annotations.I_MutableAnnotationProject import (
    I_MutableAnnotationProject,
)
from ....Abstract.Domain.Annotations.I_MutableSliceAnnotation import (
    I_MutableSliceAnnotation,
)
from ....Abstract.Domain.Annotations.I_PolygonAnnotation import I_PolygonAnnotation
from ....Abstract.Domain.Defaults.E_DefaultValue import E_DefaultValue
from ....Abstract.Domain.Geometry.I_PointList import I_PointList
from ....Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
from ....Abstract.Domain.Imaging.I_Metadata import I_Metadata
from ....Abstract.Domain.Records.I_RecordFieldList import I_RecordFieldList
from ....Abstract.Storage.Paths.I_FilePath import I_FilePath

if TYPE_CHECKING:
    from ....Abstract.Domain.Annotations.I_MutableSliceAnnotation import (
        I_MutableSliceAnnotation,
    )
    from ....Abstract.Domain.Annotations.I_PolygonAnnotation import I_PolygonAnnotation
    from ....Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
    from ....Abstract.Domain.Imaging.I_Metadata import I_Metadata
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
from dataclasses import dataclass
from datetime import UTC, datetime
from itertools import pairwise
from typing import final

import numpy as np
from numpy.typing import NDArray


# 管理各层轮廓、复核和插值状态，生成与影像网格对应的三维掩码。
@final
@dataclass(slots=True, frozen=False, init=False)
class C_AnnotationProject(I_MutableAnnotationProject):
    _state_image_id: str
    _state_source_fingerprint: str
    _state_shape_lps: tuple[int, int, int]
    _state_spacing_lps_mm: tuple[float, float, float]
    _state_origin_lps_mm: tuple[float, float, float]
    _state_slices: dict[int, I_MutableSliceAnnotation]
    _state_metadata: I_Metadata
    _state_edit_counter: int
    _state_schema_version: int
    _state_updated_at: str

    # 保存影像几何和逐层标注，为可选字段建立独立的默认值。
    def __init__(
        self,
        image_id: str,
        source_fingerprint: str,
        shape_lps: tuple[int, int, int],
        spacing_lps_mm: tuple[float, float, float],
        origin_lps_mm: tuple[float, float, float],
        slices: dict[int, I_MutableSliceAnnotation]
        | E_DefaultValue = E_DefaultValue.Unset,
        metadata: I_Metadata | E_DefaultValue = E_DefaultValue.Unset,
        edit_counter: int = 0,
        schema_version: int = 4,
        updated_at: str | E_DefaultValue = E_DefaultValue.Unset,
    ) -> None:
        from ...Domain.Imaging.C_Metadata import C_Metadata

        object.__setattr__(self, "_state_image_id", image_id)
        object.__setattr__(self, "_state_source_fingerprint", source_fingerprint)
        object.__setattr__(self, "_state_shape_lps", shape_lps)
        object.__setattr__(self, "_state_spacing_lps_mm", spacing_lps_mm)
        object.__setattr__(self, "_state_origin_lps_mm", origin_lps_mm)
        object.__setattr__(
            self, "_state_slices", dict() if slices is E_DefaultValue.Unset else slices
        )
        object.__setattr__(
            self,
            "_state_metadata",
            C_Metadata() if metadata is E_DefaultValue.Unset else metadata,
        )
        object.__setattr__(self, "_state_edit_counter", edit_counter)
        object.__setattr__(self, "_state_schema_version", schema_version)
        object.__setattr__(
            self,
            "_state_updated_at",
            (lambda: datetime.now(UTC).isoformat())()
            if updated_at is E_DefaultValue.Unset
            else updated_at,
        )

    # 返回标注所属的影像标识。
    def getImageId(self) -> str:
        return self._state_image_id

    # 记录标注所属的影像标识。
    def setImageId(self, value: str) -> None:
        self._state_image_id = value

    # 返回项目绑定的影像指纹。
    def getSourceFingerprint(self) -> str:
        return self._state_source_fingerprint

    # 记录项目绑定的影像指纹。
    def setSourceFingerprint(self, value: str) -> None:
        self._state_source_fingerprint = value

    # 返回 L、P、S 三轴的体素数量。
    def getShapeLps(self) -> tuple[int, int, int]:
        return self._state_shape_lps

    # 记录L、P、S 三轴的体素数量。
    def setShapeLps(self, value: tuple[int, int, int]) -> None:
        self._state_shape_lps = value

    # 返回 L、P、S 三轴的网格间距，单位为毫米。
    def getSpacingLpsMm(self) -> tuple[float, float, float]:
        return self._state_spacing_lps_mm

    # 记录L、P、S 三轴的网格间距，单位为毫米。
    def setSpacingLpsMm(self, value: tuple[float, float, float]) -> None:
        self._state_spacing_lps_mm = value

    # 返回 LPS 物理原点，单位为毫米。
    def getOriginLpsMm(self) -> tuple[float, float, float]:
        return self._state_origin_lps_mm

    # 记录LPS 物理原点，单位为毫米。
    def setOriginLpsMm(self, value: tuple[float, float, float]) -> None:
        self._state_origin_lps_mm = value

    # 返回影像元数据的只读快照。
    def getMetadata(self) -> I_Metadata:
        return self._state_metadata

    # 记录影像元数据的只读快照。
    def setMetadata(self, value: I_Metadata) -> None:
        self._state_metadata = value

    # 返回项目级编辑序号计数器。
    def getEditCounter(self) -> int:
        return self._state_edit_counter

    # 记录项目级编辑序号计数器。
    def setEditCounter(self, value: int) -> None:
        self._state_edit_counter = value

    # 返回标注 JSON 的格式版本。
    def getSchemaVersion(self) -> int:
        return self._state_schema_version

    # 记录标注 JSON 的格式版本。
    def setSchemaVersion(self, value: int) -> None:
        self._state_schema_version = value

    # 返回项目最近一次保存时间。
    def getUpdatedAt(self) -> str:
        return self._state_updated_at

    # 记录项目最近一次保存时间。
    def setUpdatedAt(self, value: str) -> None:
        self._state_updated_at = value

    # 返回有序的记录字段名，供序列化读取。
    def getRecordFields(self) -> I_RecordFieldList:
        from ..Records.C_RecordFieldList import C_RecordFieldList

        return C_RecordFieldList(
            (
                "image_id",
                "source_fingerprint",
                "shape_lps",
                "spacing_lps_mm",
                "origin_lps_mm",
                "slices",
                "metadata",
                "edit_counter",
                "schema_version",
                "updated_at",
            )
        )

    # 核对标注与影像的体素尺寸、间距和原点，拒绝几何不一致。
    def validate_volume(self, volume: I_MedicalVolume) -> None:
        from ...Algorithms.Validation.C_VolumeGeometryValidator import (
            C_VolumeGeometryValidator,
        )

        return C_VolumeGeometryValidator().validate_volume(self, volume)

    # 取得指定层的可写标注；缺失时创建，越界时拒绝访问。
    def annotation(self, slice_index: int) -> I_MutableSliceAnnotation:
        from .C_SliceAnnotation import C_SliceAnnotation

        if not 0 <= slice_index < self.getShapeLps()[2]:
            raise IndexError("slice_index is outside the volume")
        return self._state_slices.setdefault(slice_index, C_SliceAnnotation())

    # 递增项目编辑序号，使删除操作可找到最近修改的轮廓。
    def _next_edit_order(self) -> int:
        self.setEditCounter(self.getEditCounter() + 1)
        return self.getEditCounter()

    # 向指定层加入轮廓，清除强制空层标志并分配新的编辑序号。
    def add_polygon(self, slice_index: int, polygon: I_PolygonAnnotation) -> None:
        from ..Snapshots.C_PolygonCopy import C_PolygonCopy

        annotation = self.annotation(slice_index)
        annotation.setForceEmpty(False)
        annotation.addPolygon(
            C_PolygonCopy().copy(polygon, edit_order=self._next_edit_order())
        )

    # 更新指定轮廓坐标，清除强制空层标志并刷新其编辑顺序。
    def replace_polygon(
        self, slice_index: int, polygon_index: int, points: I_PointList
    ) -> None:
        from .C_PolygonAnnotation import C_PolygonAnnotation

        annotation = self.annotation(slice_index)
        annotation.setForceEmpty(False)
        previous = annotation.getPolygon(polygon_index)
        annotation.replacePolygon(
            polygon_index,
            C_PolygonAnnotation(
                points=points,
                operation=previous.getOperation(),
                source="manual",
                edit_order=self._next_edit_order(),
            ),
        )

    # 按编辑序号删除本层最近修改的轮廓，而非简单删除列表末项。
    def delete_last_edited_polygon(
        self, slice_index: int
    ) -> I_PolygonAnnotation | None:
        annotation = self.annotation(slice_index)
        if annotation.getPolygonCount() == 0:
            return None
        polygon_index = max(
            range(annotation.getPolygonCount()),
            key=lambda index: annotation.getPolygon(index).getEditOrder(),
        )
        return annotation.removePolygon(polygon_index)

    # 复制源层轮廓并改为人工来源，清除目标层复核与强制空标志。
    def copy_slice(self, source_index: int, target_index: int) -> None:
        from ..Snapshots.C_PolygonCopy import C_PolygonCopy

        source = self.annotation(source_index)
        target = self.annotation(target_index)
        target.setPolygons(
            [
                C_PolygonCopy().copy(
                    polygon, source="manual", edit_order=self._next_edit_order()
                )
                for polygon in source.iterPolygons()
            ]
        )
        target.setCompleted(False)
        target.setForceEmpty(False)

    # 设置指定层的复核标志；已复核的空层也作为插值关键边界。
    def set_completed(self, slice_index: int, completed: bool) -> None:
        annotation = self.annotation(slice_index)
        annotation.setCompleted(bool(completed))
        if completed:
            annotation.setKeyframe(True)

    # 更新当前层强制空掩码状态，使它优先于轮廓和自动插值。
    def set_force_empty(self, slice_index: int, force_empty: bool) -> None:
        self.annotation(slice_index).setForceEmpty(bool(force_empty))

    # 设置指定层是否作为显式插值关键层。
    def set_keyframe(self, slice_index: int, keyframe: bool) -> None:
        self.annotation(slice_index).setKeyframe(bool(keyframe))

    # 移除指定层的标注记录，使该层恢复未标注状态。
    def clear_slice(self, slice_index: int) -> None:
        if not 0 <= slice_index < self.getShapeLps()[2]:
            raise IndexError("slice_index is outside the volume")
        self._state_slices.pop(slice_index, None)

    # 统计已经复核的切片数量。
    def getCompletedCount(self) -> int:
        return sum(
            annotation.getCompleted() for annotation in self._state_slices.values()
        )

    # 检查项目是否存有轮廓，不以最终前景体素数量判断。
    def getHasPolygons(self) -> bool:
        return any(
            annotation.getPolygonCount() > 0
            for annotation in self._state_slices.values()
        )

    # 按层号顺序提供插值关键层，包括显式空边界层。
    def getKeyframeIndices(self) -> tuple[int, ...]:
        return tuple(
            sorted(
                (
                    index
                    for index, annotation in self._state_slices.items()
                    if annotation.getPolygonCount()
                    or annotation.getKeyframe()
                    or annotation.getCompleted()
                    or annotation.getForceEmpty()
                )
            )
        )

    # 统计处于有效关键层插值范围内的切片数量。
    def getInterpolatedSliceCount(self) -> int:
        from .C_SliceAnnotation import C_SliceAnnotation

        return sum(
            (
                1
                for left, right in pairwise(self.getKeyframeIndices())
                for index in range(left + 1, right)
                if not self._state_slices.get(
                    index, C_SliceAnnotation()
                ).getPolygonCount()
                and (
                    not self._state_slices.get(
                        index, C_SliceAnnotation()
                    ).getCompleted()
                )
                and (
                    not self._state_slices.get(
                        index, C_SliceAnnotation()
                    ).getForceEmpty()
                )
            )
        )

    # 按存储顺序分别合成人工与机器轮廓，再取两者并集。
    def _manual_plane(self, slice_index: int) -> NDArray[np.bool_]:
        from ...Algorithms.Masks.C_ManualPlaneAlgorithm import C_ManualPlaneAlgorithm

        return C_ManualPlaneAlgorithm().manual_plane(self, slice_index)

    # 计算二值切片的有符号距离场，为关键层之间的插值提供数值。
    def _signed_distance(self, plane: NDArray[np.bool_]) -> NDArray[np.float32]:
        from ...Algorithms.Masks.C_SignedDistanceAlgorithm import (
            C_SignedDistanceAlgorithm,
        )

        return C_SignedDistanceAlgorithm().signed_distance(plane)

    # 查询当前层两侧的插值关键层，遇到显式状态时不跨越其边界。
    def interpolation_bounds(self, slice_index: int) -> tuple[int, int] | None:
        from ...Algorithms.Masks.C_InterpolationAlgorithm import (
            C_InterpolationAlgorithm,
        )

        return C_InterpolationAlgorithm().interpolation_bounds(self, slice_index)

    # 在相邻关键层距离场之间插值，显式标注或边界层不使用自动结果。
    def interpolated_plane(self, slice_index: int) -> NDArray[np.bool_] | None:
        from ...Algorithms.Masks.C_InterpolationAlgorithm import (
            C_InterpolationAlgorithm,
        )

        return C_InterpolationAlgorithm().interpolated_plane(self, slice_index)

    # 计算各层是否实际含前景，保留强制空层造成的间断并避免分配完整体积。
    def mask_presence(self, *, interpolate: bool = True) -> NDArray[np.bool_]:
        from ...Algorithms.Masks.C_InterpolationAlgorithm import (
            C_InterpolationAlgorithm,
        )

        return C_InterpolationAlgorithm().mask_presence(self, interpolate=interpolate)

    # 生成 LPS 三维二值掩码，按参数选择是否填入关键层之间的插值。
    def to_mask(self, *, interpolate: bool = True) -> NDArray[np.uint8]:
        from ...Algorithms.Masks.C_InterpolationAlgorithm import (
            C_InterpolationAlgorithm,
        )

        return C_InterpolationAlgorithm().to_mask(self, interpolate=interpolate)

    # 委托持久化算法保存项目，同时传递非零编号的空文件删除策略。
    def save(
        self, path: str | I_FilePath, *, delete_if_empty: bool = False
    ) -> I_FilePath:
        from ...Algorithms.Persistence.C_ProjectPersistence import C_ProjectPersistence
        from ...Diagnostics.Progress.C_OperationProgressFactory import (
            C_OperationProgressFactory,
        )

        with C_OperationProgressFactory().start("annotations.save", 1.0):
            return C_ProjectPersistence().save(
                self, path, delete_if_empty=delete_if_empty
            )

    # 返回指定层轮廓合成的二值结果，不填入自动插值。
    def getManualPlane(self, slice_index: int) -> NDArray[np.bool_]:
        return self._manual_plane(slice_index)

    # 返回指定二值切片的有符号距离场，供插值计算使用。
    def getSignedDistance(self, plane: NDArray[np.bool_]) -> NDArray[np.float32]:
        return self._signed_distance(plane)

    # 返回保存了显式状态的层记录数量，而不是影像总层数。
    def getSliceCount(self) -> int:
        return len(self._state_slices)

    # 查询已存在的层标注，不创建新层且不暴露内部字典。
    def findSlice(self, index: int) -> I_MutableSliceAnnotation | None:
        return self._state_slices.get(index)

    # 遍历已保存标注状态的层号，不为未标注层创建记录。
    def iterSliceIndices(self) -> Iterator[int]:
        yield from self._state_slices
