from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Algorithms.Masks.I_InterpolationAlgorithm import (
    I_InterpolationAlgorithm,
)

if TYPE_CHECKING:
    from ....Abstract.Domain.Annotations.I_MutableAnnotationProject import (
        I_MutableAnnotationProject,
    )
from itertools import pairwise
from typing import final

import numpy as np
from numpy.typing import NDArray


# 在关键层之间插值有符号距离场，保留强制空层和边界层语义。
@final
class C_InterpolationAlgorithm(I_InterpolationAlgorithm):
    # 查询当前层两侧的插值关键层，遇到显式状态时不跨越其边界。
    def interpolation_bounds(
        self, context: I_MutableAnnotationProject, slice_index: int
    ) -> tuple[int, int] | None:
        from ...Domain.Annotations.C_SliceAnnotation import C_SliceAnnotation

        annotation = context.findSlice(slice_index) or C_SliceAnnotation()
        if (
            annotation.getPolygonCount()
            or annotation.getKeyframe()
            or annotation.getCompleted()
            or annotation.getForceEmpty()
        ):
            return None
        keyframes = np.asarray(context.getKeyframeIndices(), dtype=np.int64)
        position = int(np.searchsorted(keyframes, slice_index))
        if position == 0 or position == keyframes.size:
            return None
        return (int(keyframes[position - 1]), int(keyframes[position]))

    # 在相邻关键层距离场之间插值，显式标注或边界层不使用自动结果。
    def interpolated_plane(
        self, context: I_MutableAnnotationProject, slice_index: int
    ) -> NDArray[np.bool_] | None:
        from ...Numerics.Arrays.C_ArrayFactory import C_ArrayFactory

        bounds = context.interpolation_bounds(slice_index)
        if bounds is None:
            return None
        left, right = bounds
        fraction = (slice_index - left) / (right - left)
        left_distance = context.getSignedDistance(context.getManualPlane(left))
        right_distance = context.getSignedDistance(context.getManualPlane(right))
        blended = (1.0 - fraction) * left_distance + fraction * right_distance
        return C_ArrayFactory().wrap(blended >= 0.0)

    # 计算各层是否实际含前景，保留强制空层造成的间断并避免分配完整体积。
    def mask_presence(
        self, context: I_MutableAnnotationProject, *, interpolate: bool = True
    ) -> NDArray[np.bool_]:
        from ...Numerics.Arrays.C_ArrayFactory import C_ArrayFactory

        presence = np.zeros(context.getShapeLps()[2], dtype=bool)
        keyframes = context.getKeyframeIndices()
        if not keyframes:
            return C_ArrayFactory().wrap(presence)
        left = keyframes[0]
        left_plane = context.getManualPlane(left)
        presence[left] = left_plane.any()
        for right in keyframes[1:]:
            right_plane = context.getManualPlane(right)
            presence[right] = right_plane.any()
            if interpolate and right > left + 1:
                if np.any(left_plane & right_plane):
                    presence[left + 1 : right] = True
                elif presence[left] or presence[right]:
                    left_distance = context.getSignedDistance(left_plane)
                    right_distance = context.getSignedDistance(right_plane)
                    for slice_index in range(left + 1, right):
                        fraction = (slice_index - left) / (right - left)
                        blended = (1.0 - fraction) * left_distance
                        blended += fraction * right_distance
                        presence[slice_index] = np.any(blended >= 0.0)
            left = right
            left_plane = right_plane
        return C_ArrayFactory().wrap(presence)

    # 生成 LPS 三维二值掩码，按参数选择是否填入关键层之间的插值。
    def to_mask(
        self, context: I_MutableAnnotationProject, *, interpolate: bool = True
    ) -> NDArray[np.uint8]:
        from ...Domain.Annotations.C_SliceAnnotation import C_SliceAnnotation
        from ...Numerics.Arrays.C_ArrayFactory import C_ArrayFactory

        mask = np.zeros(context.getShapeLps(), dtype=np.uint8)
        for slice_index, annotation in (
            (_entry_index, context.getSlice(_entry_index))
            for _entry_index in context.iterSliceIndices()
        ):
            if (annotation.getPolygonCount() or annotation.getCompleted()) and (
                not annotation.getForceEmpty()
            ):
                mask[:, :, slice_index] = context.getManualPlane(slice_index).T
        if not interpolate:
            return C_ArrayFactory().wrap(mask)
        for left, right in pairwise(context.getKeyframeIndices()):
            if right <= left + 1:
                continue
            left_distance = context.getSignedDistance(context.getManualPlane(left))
            right_distance = context.getSignedDistance(context.getManualPlane(right))
            interval = right - left
            for slice_index in range(left + 1, right):
                annotation = context.findSlice(slice_index) or C_SliceAnnotation()
                if (
                    annotation.getPolygonCount()
                    or annotation.getCompleted()
                    or annotation.getForceEmpty()
                ):
                    continue
                fraction = (slice_index - left) / interval
                blended = (1.0 - fraction) * left_distance + fraction * right_distance
                mask[:, :, slice_index] = (blended >= 0.0).T
        return C_ArrayFactory().wrap(mask)
